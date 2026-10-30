"""One explicitly authorized Bleak connection. No discovery command or reconnect loop."""
import asyncio
import math
from contextlib import suppress
from importlib.metadata import version
from time import monotonic

from .identity import record_digest

from .journal import Journal
from .protocol import ACK, EXPECTED_INFO, INFO, SERVICE, TX, Record, Reassembler, encode_ack


class ReceiverError(RuntimeError):
    pass


def _characteristics(client):
    services = [s for s in client.services if s.uuid.lower() == SERVICE]
    if len(services) != 1:
        raise ReceiverError("expected exactly one frozen pen service")
    result = {}
    for uuid, prop in [(TX, "notify"), (ACK, "write"), (INFO, "read")]:
        matches = [c for c in services[0].characteristics if c.uuid.lower() == uuid]
        if len(matches) != 1 or prop not in matches[0].properties:
            raise ReceiverError("missing/ambiguous GATT characteristic or required property")
        result[uuid] = matches[0]
    return result


async def receive(directory, binding, *, radio_authorized=False, os_pairing_authorized=False,
                  confirm_local_approval=None, client_factory=None, emit=lambda event: None,
                  create=False, windows_private_dir_confirmed=False, queue_size=96,
                  journal_factory=Journal):
    """Return after disconnect; restart requires another explicit invocation.

    `confirm_local_approval` is a local operator interaction, not proof of SC/MITM.
    Each invocation owns a fresh client, callback closure, queue and reassembler.
    Never call a previous client's callback on a new client or reuse partial data.
    """
    if not radio_authorized or not os_pairing_authorized or confirm_local_approval is None:
        raise ReceiverError("explicit radio, OS-pairing authorization and local confirmation required")
    binding.validate()
    if type(queue_size) is not int or not 3 <= queue_size <= 4096:
        raise ValueError("queue_size must be 3..4096")
    # Refuse unsafe/unwritable journal BEFORE importing Bleak or constructing client.
    with journal_factory(directory, binding, create=create,
                         windows_private_dir_confirmed=windows_private_dir_confirmed) as journal:
        def send_event(event):
            emit({"source_namespace": journal.metadata["source_namespace"], **event})

        if client_factory is None:
            if version("bleak") != "3.0.2":
                raise ReceiverError("reviewed optional dependency is bleak==3.0.2")
            from bleak import BleakClient
            client_factory = BleakClient
        queue = asyncio.Queue(maxsize=queue_size)
        disconnected = asyncio.Event()
        overflow = asyncio.Event()
        clock_fault = asyncio.Event()
        last_observed = None
        assembly = Reassembler()
        active = False
        generation = object()  # Process-local isolation tag, not wire epoch/security evidence.

        def on_data(_, data):
            nonlocal last_observed
            if not active or disconnected.is_set() or overflow.is_set() or clock_fault.is_set():
                return
            observed_at = monotonic()
            if not math.isfinite(observed_at) or last_observed is not None and observed_at < last_observed:
                clock_fault.set()
                assembly.reset()
                return
            last_observed = observed_at
            try:
                queue.put_nowait((generation, observed_at, bytes(data)))
            except asyncio.QueueFull:
                overflow.set()
                assembly.reset()

        def on_disconnect(_):
            nonlocal active
            active = False
            assembly.reset()
            disconnected.set()

        # A string target may cause Bleak's implicit scan, ONLY within this explicit command.
        async with client_factory(binding.target, pair=True, timeout=60,
                                  disconnected_callback=on_disconnect) as client:
            chars = _characteristics(client)
            subscribed = False
            try:
                # On macOS accessing protected INFO can initiate OS pairing. This
                # read is never approval, and 05/08 only permit the local prompt.
                try:
                    probe = bytes(await client.read_gatt_char(chars[INFO], use_cached=False))
                    if probe != EXPECTED_INFO:
                        raise ReceiverError("unexpected INFO; no synthetic/unknown firmware fallback")
                except Exception as exc:
                    if getattr(exc, "code", None) not in (0x05, 0x08):
                        raise
                    send_event({"type": "LOCAL_APPROVAL_REQUIRED", "host_security_attested": False})
                approved = await asyncio.wait_for(confirm_local_approval(), timeout=55)
                if approved is not True or disconnected.is_set() or not client.is_connected:
                    raise ReceiverError("local confirmation missing or connection already ended")
                info = bytes(await client.read_gatt_char(chars[INFO], use_cached=False))
                if info != EXPECTED_INFO:
                    raise ReceiverError("frozen INFO mismatch")
                send_event({"type": "CONNECTED", "source": "dev_usb_no_sensor",
                      "host_security_attested": False, "UI_allowed": False})
                active = True
                await client.start_notify(chars[TX], on_data)
                subscribed = True
                while not disconnected.is_set():
                    if clock_fault.is_set():
                        raise ReceiverError("callback observation clock fault: stop, no ACK")
                    if overflow.is_set():
                        raise ReceiverError("notification overflow: stop, preserve journal, explicit reconnect/replay")
                    try:
                        token, received_at, fragment = await asyncio.wait_for(queue.get(), timeout=.1)
                    except asyncio.TimeoutError:
                        continue
                    if token is not generation or not active or disconnected.is_set():
                        continue
                    try:
                        raw = assembly.accept(fragment, now=received_at)
                    except ValueError as exc:
                        send_event({"type": "REJECTED_FRAGMENT", "reason": str(exc), "ACK_sent": False})
                        continue
                    if raw is None:
                        continue
                    record = Record.decode(raw)
                    if record.device != binding.device:
                        raise ReceiverError("record device differs from explicit local binding")
                    # Disk I/O does not block callback processing. Cancellation must
                    # wait for the one commit worker before closing SQLite; no ACK.
                    commit = asyncio.create_task(asyncio.to_thread(journal.accept, raw))
                    try:
                        inserted = await asyncio.shield(commit)
                    except asyncio.CancelledError:
                        while not commit.done():
                            try:
                                await asyncio.shield(commit)
                            except asyncio.CancelledError:
                                continue
                            except Exception:
                                break
                        with suppress(Exception):
                            commit.result()
                        raise
                    await asyncio.sleep(0)  # dispatch queued disconnect/overflow before ACK
                    if disconnected.is_set() or not active or not client.is_connected:
                        break
                    if clock_fault.is_set():
                        raise ReceiverError("callback clock fault during commit: no ACK")
                    if overflow.is_set():
                        raise ReceiverError("overflow during commit: durable data kept, no ACK")
                    # EXTRA commit (or identical already-durable row) completed, and
                    # ALL 3 fragments were received in THIS connection. Exact ACK.
                    await client.write_gatt_char(chars[ACK], encode_ack(record.session, record.seq), response=True)
                    send_event({"type": "DURABLE_RECORD", "device": record.device,
                          "session": str(record.session), "seq": record.seq,
                          "record_sha256": record_digest(record),
                          "duplicate": not inserted, "ACK_write_response": True,
                          "device_ACK_durable": "unknown", "UI_allowed": False})
            finally:
                active = False
                assembly.reset()
                while not queue.empty():
                    queue.get_nowait()
                if subscribed and client.is_connected:
                    await client.stop_notify(chars[TX])
