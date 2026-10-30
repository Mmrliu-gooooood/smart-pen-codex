"""Background reader for the USB camera port.

A dedicated thread keeps draining the serial port into memory, so a slow
consumer (image decoding, PNG writing, Python GC) never leaves the Windows
serial driver's buffer full. ``SerialPump`` offers the small subset of the
pyserial interface that :class:`UsbCameraClient` uses.
"""

from __future__ import annotations

import threading
import time

# Large driver-side input queue (SetupComm on Windows; ignored elsewhere).
DRIVER_RX_BYTES = 1 << 20
POLL_S = 0.02


class SerialPump:
    """Reads ``serial`` on a thread; ``read`` returns buffered bytes.

    Statistics for diagnosing data loss: ``bytes_read``, ``max_backlog`` (the
    most bytes waiting for the consumer), ``max_read_gap_s`` (longest time the
    thread spent between two port reads while data was flowing).
    """

    def __init__(self, serial, *, read_timeout_s: float = 10.0):
        self._serial = serial
        self._read_timeout_s = read_timeout_s
        set_size = getattr(serial, "set_buffer_size", None)
        if set_size is not None:
            try:
                set_size(rx_size=DRIVER_RX_BYTES)
            except (OSError, ValueError):
                pass
        serial.timeout = POLL_S
        self._buffer = bytearray()
        self._ready = threading.Condition()
        self._stop = threading.Event()
        self._error: BaseException | None = None
        self.bytes_read = 0
        self.max_backlog = 0
        self.max_read_gap_s = 0.0
        self._thread = threading.Thread(
            target=self._run, name="usb-camera-reader", daemon=True
        )
        self._thread.start()

    def _run(self) -> None:
        last_data = None
        try:
            while not self._stop.is_set():
                waiting = getattr(self._serial, "in_waiting", 0)
                data = self._serial.read(max(1, min(waiting, 1 << 16)))
                if not data:
                    last_data = None
                    continue
                now = time.monotonic()
                if last_data is not None:
                    self.max_read_gap_s = max(self.max_read_gap_s, now - last_data)
                last_data = now
                with self._ready:
                    self._buffer += data
                    self.bytes_read += len(data)
                    self.max_backlog = max(self.max_backlog, len(self._buffer))
                    self._ready.notify_all()
        except BaseException as error:  # noqa: BLE001 - handed to the consumer
            with self._ready:
                self._error = error
                self._ready.notify_all()

    # -- pyserial subset --------------------------------------------------------

    def read(self, count: int) -> bytes:
        """Up to ``count`` buffered bytes; waits up to the read timeout for
        the first one and returns b"" if none came."""
        deadline = time.monotonic() + self._read_timeout_s
        with self._ready:
            while not self._buffer:
                if self._error is not None:
                    raise self._error
                remaining = deadline - time.monotonic()
                if remaining <= 0 or self._stop.is_set():
                    return b""
                self._ready.wait(remaining)
            chunk = bytes(self._buffer[:count])
            del self._buffer[: len(chunk)]
            return chunk

    def write(self, data: bytes) -> int | None:
        return self._serial.write(data)

    def flush(self) -> None:
        self._serial.flush()

    def reset_input_buffer(self) -> None:
        with self._ready:
            self._serial.reset_input_buffer()
            self._buffer.clear()

    @property
    def in_waiting(self) -> int:
        with self._ready:
            return len(self._buffer)

    def close(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)
        self._serial.close()

    def stats(self) -> dict[str, float]:
        return {
            "bytes_read": self.bytes_read,
            "max_backlog": self.max_backlog,
            "max_read_gap_s": self.max_read_gap_s,
        }
