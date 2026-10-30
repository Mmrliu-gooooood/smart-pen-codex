"""Client for the USB camera firmware (``usb_camera/``).

Frames arrive over the ESP32-S3's built-in USB Serial/JTAG port, the same COM
port used for flashing (Espressif VID 0x303A, PID 0x1001), so the PC keeps its
normal Wi-Fi. Protocol: ASCII command lines to the device; binary replies
``b"DPU1" | type | u32 json_len | json | u32 payload_len | payload``.

Firmware v5 adds a CRC-32 (``crc32``) and a per-stream counter (``n``) to
every frame, and the ``TRACK`` stream (:class:`TrackSession`): one ROI frame
per sensor frame plus overview and page snapshots sent in chunks.
"""

from __future__ import annotations

import json
import struct
import time
import zlib
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from digital_pen.camera.serial_pump import SerialPump
from digital_pen.types import CameraFrame

MAGIC = b"DPU1"
ESPRESSIF_VID = 0x303A
USB_SERIAL_JTAG_PID = 0x1001
# Sanity limits for message headers (largest real payload: a UXGA frame).
MAX_JSON_BYTES = 4096
MAX_PAYLOAD_BYTES = 4 * 1024 * 1024


class UsbCameraError(RuntimeError):
    """The device answered with an error message or broke the protocol."""


def check_crc(metadata: dict[str, Any], payload: bytes) -> None:
    """Firmware v5 sends ``crc32`` (zlib CRC-32) with every payload."""
    expected = metadata.get("crc32")
    if expected is not None and zlib.crc32(payload) != int(expected):
        raise UsbCameraError("payload CRC-32 mismatch")


@dataclass(frozen=True)
class UsbFrame:
    """``frame`` is None (and ``error`` set) when the payload did not decode."""

    frame: CameraFrame | None
    metadata: dict[str, Any]
    payload_bytes: int
    error: str | None = None


def find_port() -> str:
    """The COM port of the board's built-in USB Serial/JTAG interface."""
    from serial.tools import list_ports

    matches = [
        port.device
        for port in list_ports.comports()
        if port.vid == ESPRESSIF_VID and port.pid == USB_SERIAL_JTAG_PID
    ]
    if len(matches) != 1:
        raise UsbCameraError(f"expected one ESP32-S3 USB port, found {matches}")
    return matches[0]


def open_serial(port: str, timeout_s: float):
    """Open without asserting DTR/RTS: on the USB Serial/JTAG port those lines
    drive the chip's reset and boot-mode logic."""
    import serial

    connection = serial.Serial()
    connection.port = port
    connection.baudrate = 115200  # ignored by USB CDC
    connection.timeout = timeout_s
    connection.write_timeout = timeout_s
    connection.dtr = False
    connection.rts = False
    connection.open()
    return connection


def decode_payload(metadata: dict[str, Any], payload: bytes) -> np.ndarray:
    width, height = int(metadata["width"]), int(metadata["height"])
    if metadata["format"] == "gray":
        if len(payload) != width * height:
            raise UsbCameraError(f"gray payload {len(payload)} B != {width}x{height}")
        return np.frombuffer(payload, np.uint8).reshape(height, width).copy()
    if metadata["format"] == "jpeg":
        image = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_GRAYSCALE)
        if image is None or image.shape != (height, width):
            raise UsbCameraError("JPEG payload could not be decoded")
        return image
    raise UsbCameraError(f"unknown frame format {metadata['format']!r}")


class UsbCameraClient:
    def __init__(
        self,
        port: str | None = None,
        *,
        timeout_s: float = 10.0,
        connection=None,
        sync_timeout_s: float = 120.0,
        reader_thread: bool = True,
    ):
        """``connection`` replaces the real port (tests). On a real port a
        background thread drains the driver continuously (``SerialPump``,
        statistics in :meth:`reader_stats`) unless ``reader_thread`` is
        False."""
        self._timeout_s = timeout_s
        self._seq = 0
        self.skipped_messages = 0
        # Bytes skipped while looking for the next "DPU1" (boot text or lost
        # sync); stays 0 on a healthy link. resync_events keeps when and what
        # (first 64 bytes, hex) for the first 20 occurrences.
        self.resync_bytes = 0
        self.resync_events: list[dict[str, Any]] = []
        # Messages whose header was damaged (skipped, see _read_message).
        self.bad_headers = 0
        if connection is None:
            connection = open_serial(port or find_port(), timeout_s)
            if reader_thread:
                connection = SerialPump(connection, read_timeout_s=timeout_s)
            owned = True
        else:
            owned = False
        self._serial = connection
        # Drop anything already buffered (e.g. ROM boot messages).
        self._serial.reset_input_buffer()
        if owned:
            # The device may still be answering an earlier, abandoned client
            # (a mode switch with autofocus takes ~17 s): wait for our reply.
            self._command("STATUS")
            self._expect("J", sync_timeout_s)

    def close(self) -> None:
        self._serial.close()

    def reader_stats(self) -> dict[str, float] | None:
        """Background reader statistics (None without the reader thread)."""
        stats = getattr(self._serial, "stats", None)
        return stats() if callable(stats) else None

    def __enter__(self) -> UsbCameraClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- protocol -------------------------------------------------------------

    def _read_exact(self, count: int, deadline: float) -> bytes:
        chunks = []
        remaining = count
        while remaining:
            if time.monotonic() > deadline:
                raise TimeoutError(f"device sent {count - remaining}/{count} bytes")
            chunk = self._serial.read(remaining)
            if chunk:
                chunks.append(chunk)
                remaining -= len(chunk)
        return b"".join(chunks)

    def _read_message(self, timeout_s: float) -> tuple[str, dict[str, Any], bytes]:
        """Next well-formed message. A damaged header (unknown type, absurd
        length, invalid JSON) is logged as a resync and the search for the
        next "DPU1" continues; the stream counter ``n`` then shows anything
        lost with it."""
        deadline = time.monotonic() + timeout_s
        while True:
            self._find_magic(deadline)
            kind = self._read_exact(1, deadline)
            (json_length,) = struct.unpack("<I", self._read_exact(4, deadline))
            if kind not in b"JFCE" or not 0 < json_length <= MAX_JSON_BYTES:
                self._bad_header(f"type {kind!r} json_length {json_length}")
                continue
            raw = self._read_exact(json_length, deadline)
            try:
                metadata = json.loads(raw)
            except ValueError:
                self._bad_header("invalid json " + raw[:64].hex())
                continue
            (payload_length,) = struct.unpack("<I", self._read_exact(4, deadline))
            if payload_length > MAX_PAYLOAD_BYTES:
                self._bad_header(f"payload_length {payload_length}")
                continue
            payload = (
                self._read_exact(payload_length, deadline) if payload_length else b""
            )
            return kind.decode("ascii"), metadata, payload

    def _find_magic(self, deadline: float) -> None:
        """Skip non-protocol bytes (boot text or lost sync) up to "DPU1"."""
        window = b""
        skipped = bytearray()
        count = -4
        while window != MAGIC:
            byte = self._read_exact(1, deadline)
            window = (window + byte)[-4:]
            count += 1
            if len(skipped) < 64:
                skipped += byte
        if count > 0:
            self.resync_bytes += count
            self._log_resync(
                {"bytes": count, "head_hex": bytes(skipped[: min(64, count)]).hex()}
            )

    def _bad_header(self, reason: str) -> None:
        self.bad_headers += 1
        self._log_resync({"bytes": 0, "bad_header": reason})

    def _log_resync(self, event: dict[str, Any]) -> None:
        if len(self.resync_events) < 20:
            self.resync_events.append({"monotonic_s": time.monotonic(), **event})

    def _command(self, line: str) -> None:
        """Send one command tagged with a fresh sequence number."""
        self._seq += 1
        self._serial.write(f"#{self._seq} {line}\n".encode("ascii"))
        self._serial.flush()

    def _expect(self, kind: str, timeout_s: float):
        """Next reply to the latest command; replies to older ones are skipped.

        Replies without ``seq`` (firmware before sequence numbers) are taken
        as they come.
        """
        deadline = time.monotonic() + timeout_s
        while True:
            got, metadata, payload = self._read_message(
                max(0.0, deadline - time.monotonic())
            )
            if metadata.get("seq", self._seq) != self._seq:
                self.skipped_messages += 1
                continue
            if got == "E":
                raise UsbCameraError(metadata.get("error", "device error"))
            if got != kind:
                raise UsbCameraError(f"expected {kind!r} message, got {got!r}")
            return metadata, payload

    @staticmethod
    def _roi(roi: tuple[int, int, int, int] | None) -> str:
        return "" if roi is None else " " + " ".join(str(int(v)) for v in roi)

    def _frame(self, metadata, payload, *, strict: bool = True) -> UsbFrame:
        try:
            check_crc(metadata, payload)
            image = decode_payload(metadata, payload)
        except UsbCameraError as error:
            if strict:
                raise
            return UsbFrame(None, metadata, len(payload), str(error))
        frame = CameraFrame(
            frame_id=int(metadata["id"]),
            timestamp_us=max(0, int(metadata["timestamp_us"])),
            image=image,
            exposure=None,
        )
        return UsbFrame(frame, metadata, len(payload))

    # -- public API -----------------------------------------------------------

    def status(self) -> dict[str, Any]:
        self._command("STATUS")
        return self._expect("J", self._timeout_s)[0]

    def set_mode(
        self, size: str = "uxga", fmt: str = "gray", quality: int = 10
    ) -> dict[str, Any]:
        """Re-initialize the camera (includes an autofocus sweep, up to ~35 s)."""
        self._command(f"MODE {size} {fmt} {int(quality)}")
        return self._expect("J", 60.0)[0]

    def set_quality(self, quality: int) -> dict[str, Any]:
        self._command(f"QUALITY {int(quality)}")
        return self._expect("J", self._timeout_s)[0]

    def set_pll(self, multiplier: int, pclk_div: int) -> dict[str, Any]:
        """Sensor clock for gray modes (firmware v3+): SYSCLK = 1.2 MHz x
        multiplier, PCLK = 2.4 MHz x multiplier / pclk_div. MODE restores the
        driver default (multiplier 10, divider 2)."""
        self._command(f"PLL {int(multiplier)} {int(pclk_div)}")
        return self._expect("J", self._timeout_s)[0]

    def read_reg(self, address: int) -> int:
        self._command(f"READREG {address:x}")
        return int(self._expect("J", self._timeout_s)[0]["value"])

    def write_reg(self, address: int, value: int) -> int:
        self._command(f"REG {address:x} {value:x}")
        return int(self._expect("J", self._timeout_s)[0]["value"])

    def set_exposure_auto(
        self, max_lines: int | None = None, gain_ceiling: int | None = None
    ) -> dict[str, Any]:
        """Auto exposure (v5); optional caps: maximum exposure in sensor lines
        (shorter = less motion blur) and gain ceiling in 1/16 steps. Without
        caps the driver's limits are restored."""
        self._command(_exposure_line(max_lines, gain_ceiling))
        return self._expect("J", self._timeout_s)[0]

    def set_exposure_manual(self, lines: int, gain: int) -> dict[str, Any]:
        """Fixed exposure (sensor lines) and gain (1/16 steps), v5."""
        self._command(f"EXPOSURE manual {int(lines)} {int(gain)}")
        return self._expect("J", self._timeout_s)[0]

    def set_flicker(self, mode: str) -> dict[str, Any]:
        """Anti-flicker band steps (v5.3): ``"clock"`` recomputes them for the
        current sensor clock (10 ms / 8.33 ms for 50 / 60 Hz mains),
        ``"driver"`` restores the driver's values. Exposure caps from
        :meth:`set_exposure_auto` are whole band steps."""
        if mode not in ("clock", "driver"):
            raise ValueError("mode must be 'clock' or 'driver'")
        self._command(f"FLICKER {mode}")
        return self._expect("J", self._timeout_s)[0]

    def set_max_age(self, milliseconds: int) -> dict[str, Any]:
        """Stale-frame limit (v5); 0 restores the default of two sensor frame
        periods plus 25 ms."""
        self._command(f"MAXAGE {int(milliseconds)}")
        return self._expect("J", self._timeout_s)[0]

    def track(
        self,
        roi: tuple[int, int, int, int],
        *,
        overview_ms: int = 500,
        page_ms: int = 1500,
        scale: int = 4,
        bg_bytes: int = 10240,
        keepalive_ms: int = 3000,
        crop: tuple[int, int, int, int] | None = None,
    ) -> TrackSession:
        """Start the v5 ``TRACK`` stream (gray modes).

        Every sensor frame yields one ROI frame; every ``overview_ms`` a
        ``scale``-times smaller whole frame, and every ``page_ms`` a full
        resolution copy of ``crop`` (default: the whole frame), both sent in
        chunks of at most ``bg_bytes`` after each ROI frame. The device stops
        by itself when no host line arrives for ``keepalive_ms``; the session
        sends ``KEEP`` well before that.
        """
        line = (
            "TRACK"
            + self._roi(roi)
            + (
                f" ov={int(overview_ms)} page={int(page_ms)} scale={int(scale)}"
                f" bg={int(bg_bytes)} keep={int(keepalive_ms)}"
            )
        )
        if crop is not None:
            line += " crop=" + ",".join(str(int(v)) for v in crop)
        self._command(line)
        start = self._expect("J", self._timeout_s)[0]
        return TrackSession(self, self._seq, start, keepalive_s=keepalive_ms / 3000)

    def capture(
        self, roi: tuple[int, int, int, int] | None = None, *, strict: bool = True
    ) -> UsbFrame:
        """One frame; with ``strict=False`` a corrupt payload is returned with
        ``error`` set instead of raising."""
        self._command("CAPTURE" + self._roi(roi))
        return self._frame(*self._expect("F", self._timeout_s), strict=strict)

    def stream(
        self, count: int, roi: tuple[int, int, int, int] | None = None
    ) -> Iterator[UsbFrame]:
        """Yield all ``count`` frames; undecodable ones carry ``error`` instead
        of raising, so the link never loses sync mid-stream."""
        self._command(f"STREAM {int(count)}" + self._roi(roi))
        for _ in range(count):
            yield self._frame(*self._expect("F", self._timeout_s), strict=False)


def _exposure_line(max_lines: int | None, gain_ceiling: int | None) -> str:
    if max_lines is None:
        if gain_ceiling is not None:
            raise ValueError("gain_ceiling needs max_lines")
        return "EXPOSURE auto"
    line = f"EXPOSURE auto {int(max_lines)}"
    return line if gain_ceiling is None else f"{line} {int(gain_ceiling)}"


@dataclass(frozen=True)
class TrackEvent:
    """One item of a TRACK stream.

    ``kind``: ``roi``, ``overview`` or ``page`` (with ``image``); ``reply`` (a
    JSON answer to a command sent during the stream); ``error`` (device error
    or an integrity failure found here, ``error`` says which); ``end`` (the
    device's summary, always last). ``arrival_s`` is ``time.monotonic()`` when
    the message (for snapshots: the last chunk) was read.
    """

    kind: str
    metadata: dict[str, Any]
    image: np.ndarray | None = None
    arrival_s: float = 0.0
    error: str | None = None


class TrackSession:
    """Reader and controller of one TRACK stream; use from a single thread.

    Iterate to receive :class:`TrackEvent` objects; call :meth:`set_roi`,
    :meth:`set_crop`, :meth:`snap` or :meth:`stop` between events. Integrity
    checks: CRC-32 of every payload, the gap-free message counter ``n`` and
    the chunk offsets of snapshots. Failures become ``error`` events and are
    counted in :attr:`stats`; damaged data is never returned as an image.
    """

    def __init__(
        self,
        client: UsbCameraClient,
        seq: int,
        start: dict[str, Any],
        *,
        keepalive_s: float = 1.0,
    ):
        self.seq = seq
        self.start = start
        self.end: dict[str, Any] | None = None
        self.stats = {
            "roi": 0,
            "overview": 0,
            "page": 0,
            "replies": 0,
            "device_errors": 0,
            "crc_errors": 0,
            "lost_messages": 0,
            "incomplete_snapshots": 0,
            "foreign_messages": 0,
            "unfinished_at_end": 0,
            "skipped_chunks": 0,
            "snapshot_crc_errors": 0,
            "device_mutated": 0,
        }
        # Raw copies of damaged messages (first 20), for offline comparison
        # with a good frame or snapshot of the same place.
        self.bad_messages: list[dict[str, Any]] = []
        self._dropped: dict[str, int] = {}
        self._client = client
        self._keepalive_s = keepalive_s
        self._last_write = time.monotonic()
        self._next_n = 0
        self._snaps: dict[str, dict[str, Any]] = {}

    # -- control --------------------------------------------------------------

    def _send(self, line: str) -> int:
        self._client._command(line)
        self._last_write = time.monotonic()
        return self._client._seq

    def set_roi(self, roi: tuple[int, int, int, int]) -> int:
        """Move the ROI; returns the command's seq, echoed as ``roi_seq`` by
        the first frame that uses it. The device keeps the window inside the
        frame (``x``/``y`` of each frame say where it really was)."""
        return self._send("ROI" + self._client._roi(roi))

    def set_crop(self, crop: tuple[int, int, int, int] | None) -> int:
        """Page snapshot area (None: whole frame)."""
        if crop is None:
            return self._send("PAGE full")
        return self._send("PAGE" + self._client._roi(crop))

    def snap(self) -> int:
        """Request a page snapshot from the next frame."""
        return self._send("SNAP")

    def set_exposure_auto(
        self, max_lines: int | None = None, gain_ceiling: int | None = None
    ) -> int:
        """Answered by a ``reply`` event carrying the new status."""
        return self._send(_exposure_line(max_lines, gain_ceiling))

    def stop(self) -> int:
        """Ask the device to end the stream; keep iterating until ``end``."""
        return self._send("STOP")

    def close(self, timeout_s: float = 5.0) -> dict[str, Any] | None:
        """Stop and drain the stream; returns the device's end summary."""
        if self.end is None:
            self.stop()
            deadline = time.monotonic() + timeout_s
            for _ in self:
                if time.monotonic() > deadline:
                    break
        return self.end

    # -- reading --------------------------------------------------------------

    def __iter__(self) -> Iterator[TrackEvent]:
        while self.end is None:
            if time.monotonic() - self._last_write >= self._keepalive_s:
                self._send("KEEP")
            kind, metadata, payload = self._client._read_message(
                self._client._timeout_s
            )
            yield from self._handle(kind, metadata, payload, time.monotonic())

    def _error(self, counter: str, text: str, metadata, arrival) -> TrackEvent:
        self.stats[counter] += 1
        return TrackEvent("error", metadata, arrival_s=arrival, error=text)

    def _keep_bad(self, reason: str, kind: str, metadata, payload, arrival) -> None:
        if len(self.bad_messages) < 20:
            self.bad_messages.append(
                {
                    "reason": reason,
                    "type": kind,
                    "arrival_s": arrival,
                    "metadata": metadata,
                    "payload": bytes(payload),
                }
            )

    def _drop_snapshot(self, name: str, snap: int) -> None:
        """Forget a damaged snapshot; its remaining chunks are skipped quietly
        (one error per snapshot, not one per chunk)."""
        self._snaps.pop(name, None)
        self._dropped[name] = snap

    def _handle(self, kind, metadata, payload, arrival) -> list[TrackEvent]:
        seq = metadata.get("seq", self.seq)
        if kind == "J" and metadata.get("track") == "end" and seq == self.seq:
            self.end = metadata
            # Snapshots still in transit when the stream ends are abandoned
            # by the device; that is not damage, so they are counted apart.
            self.stats["unfinished_at_end"] += len(self._snaps)
            self._snaps.clear()
            return [TrackEvent("end", metadata, arrival_s=arrival)]
        if kind == "E":
            text = metadata.get("error", "device error")
            return [self._error("device_errors", text, metadata, arrival)]
        if seq != self.seq:
            if kind == "J":
                self.stats["replies"] += 1
                return [TrackEvent("reply", metadata, arrival_s=arrival)]
            self.stats["foreign_messages"] += 1
            return []
        if kind not in ("F", "C"):
            return []
        events = []
        n = int(metadata.get("n", self._next_n))
        if n != self._next_n:
            self.stats["lost_messages"] += max(n - self._next_n, 1)
            events.append(
                TrackEvent(
                    "error",
                    metadata,
                    arrival_s=arrival,
                    error=f"message counter jumped {self._next_n} -> {n}",
                )
            )
        self._next_n = n + 1
        self.stats["device_mutated"] = max(
            self.stats["device_mutated"], int(metadata.get("mutated", 0))
        )
        try:
            check_crc(metadata, payload)
        except UsbCameraError as error:
            self._keep_bad("crc", kind, metadata, payload, arrival)
            if kind == "C":
                self._drop_snapshot(metadata["kind"], int(metadata["snap"]))
            return [*events, self._error("crc_errors", str(error), metadata, arrival)]
        if kind == "F":
            try:
                image = decode_payload(metadata, payload)
            except UsbCameraError as error:
                event = self._error("device_errors", str(error), metadata, arrival)
                return [*events, event]
            self.stats["roi"] += 1
            return [*events, TrackEvent("roi", metadata, image, arrival)]
        return [*events, *self._chunk(metadata, payload, arrival)]

    def _chunk(self, metadata, payload, arrival) -> list[TrackEvent]:
        name = metadata["kind"]
        events = []
        if int(metadata["offset"]) != 0 and self._dropped.get(name) == int(
            metadata["snap"]
        ):
            self.stats["skipped_chunks"] += 1
            return events
        current = self._snaps.get(name)
        if int(metadata["offset"]) == 0:
            self._dropped.pop(name, None)
            if current is not None:
                text = f"{name} snapshot {current['meta']['snap']} incomplete"
                events.append(
                    self._error("incomplete_snapshots", text, current["meta"], arrival)
                )
            current = {"meta": metadata, "data": bytearray(), "chunks": 0}
            self._snaps[name] = current
        elif (
            current is None
            or current["meta"]["snap"] != metadata["snap"]
            or len(current["data"]) != int(metadata["offset"])
        ):
            self._drop_snapshot(name, int(metadata["snap"]))
            text = f"{name} chunk out of order (snap {metadata['snap']})"
            return [self._error("incomplete_snapshots", text, metadata, arrival)]
        current["data"] += payload
        current["chunks"] += 1
        total = int(metadata["total"])
        if len(current["data"]) < total:
            return events
        self._snaps.pop(name)
        first = current["meta"]
        width, height = int(first["width"]), int(first["height"])
        if len(current["data"]) != total or total != width * height:
            text = f"{name} snapshot size mismatch"
            return [*events, self._error("incomplete_snapshots", text, first, arrival)]
        data = bytes(current["data"])
        expected = first.get("snap_crc32")
        if expected is not None and zlib.crc32(data) != int(expected):
            # Every chunk arrived intact, but the snapshot differs from what
            # the device checksummed right after copying it.
            self._keep_bad("snapshot_crc", "C", first, data, arrival)
            text = f"{name} snapshot {first['snap']} changed on the device"
            return [*events, self._error("snapshot_crc_errors", text, first, arrival)]
        image = np.frombuffer(data, np.uint8).reshape(height, width).copy()
        self.stats[name] += 1
        meta = {
            **first,
            "chunks": current["chunks"],
            "last_sent_us": metadata.get("sent_us"),
        }
        return [*events, TrackEvent(name, meta, image, arrival)]
