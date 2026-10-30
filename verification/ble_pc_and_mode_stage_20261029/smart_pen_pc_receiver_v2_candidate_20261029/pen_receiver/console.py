"""Cancellable local terminal read; no hanging input worker after timeout."""
import asyncio
import os
import sys


async def read_confirmation():
    if os.name == 'nt':
        import msvcrt
        chars = []
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\r', '\n'):
                    print(file=sys.stderr, flush=True)
                    return ''.join(chars)
                if ch == '\x03':
                    raise KeyboardInterrupt
                if ch == '\b':
                    if chars:
                        chars.pop()
                elif ch in ('\x00', '\xe0'):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                elif ch.isprintable() and len(chars) < 64:
                    chars.append(ch)
            await asyncio.sleep(.05)
    else:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        def ready():
            if not future.done():
                future.set_result(sys.stdin.readline(65).rstrip('\r\n'))
        loop.add_reader(sys.stdin.fileno(), ready)
        try:
            return await future
        finally:
            loop.remove_reader(sys.stdin.fileno())
