"""Local BLE coordinate receiver candidate; no arguments means help, no radio."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import sys

from .events import record_events
from .journal import Binding, Journal, private_directory
from .receiver import receive


def emit(event):
    print(json.dumps(event, ensure_ascii=False, separators=(',', ':')), flush=True)


async def confirm():
    print('在目标开发笔 USB 显示完成随机 passkey 配对，并在笔的本地接口确认当前 epoch。\n'
          '不要在此输入 passkey。完成本地批准后输入 READY；其他输入取消。\n'
          '此声明不是 PC 对 SC/MITM/bond 的独立证明。', file=sys.stderr, flush=True)
    from .console import read_confirmation
    answer = await read_confirmation()
    return answer == 'READY'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command')
    init = sub.add_parser('init-state', help='create one private local directory; no radio')
    init.add_argument('--state-dir', required=True)
    replay = sub.add_parser('replay', help='existing journal -> diagnostic NDJSON; no radio')
    replay.add_argument('--state-dir', required=True)
    replay.add_argument('--session', type=int, required=True)
    replay.add_argument('--windows-private-dir-confirmed', action='store_true')
    connect = sub.add_parser('connect', help='EXPLICIT radio/OS pairing; no automatic reconnect')
    connect.add_argument('--state-dir', required=True)
    connect.add_argument('--target', required=True, help='explicit OS address (Windows/Linux) or UUID (macOS)')
    connect.add_argument('--peer-scope', required=True, help='private local stable label, NOT broadcast name')
    connect.add_argument('--device', required=True, type=int, help='locally verified firmware uint32 device ID')
    connect.add_argument('--enable-radio', action='store_true')
    connect.add_argument('--authorize-os-pairing', action='store_true')
    connect.add_argument('--create-journal', action='store_true', help='only if journal does not exist')
    connect.add_argument('--windows-private-dir-confirmed', action='store_true')
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == 'init-state':
        path = Path(os.path.abspath(args.state_dir))
        if path.exists() or path.is_symlink():
            parser.error('state directory already exists; do not chmod/reset it automatically')
        # Parent must already exist; this command does not create arbitrary trees.
        if any(p.is_symlink() for p in path.parents):
            parser.error('symlink parent rejected')
        path.mkdir(mode=0o700)
        if os.name == 'nt':
            print('Created directory; Windows DACL NOT verified. Restrict it to your user before connect.', file=sys.stderr)
        else:
            private_directory(path)
        return 0
    if args.command == 'replay':
        with Journal(args.state_dir, windows_private_dir_confirmed=args.windows_private_dir_confirmed) as journal:
            for event in record_events(journal.replay(args.session), journal.metadata):
                emit(event)
        return 0
    if not args.enable_radio or not args.authorize_os_pairing:
        parser.error('connect requires --enable-radio and --authorize-os-pairing; no radio started')
    mac = re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', args.target)
    uuid = re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', args.target)
    if not (mac or uuid):
        parser.error('explicit target must be an OS Bluetooth address or device UUID, not a name')
    if not sys.stdin.isatty():
        parser.error('interactive local confirmation required; no unattended radio mode')
    binding = Binding(args.peer_scope, args.target.upper(), args.device)
    asyncio.run(receive(args.state_dir, binding, radio_authorized=True, os_pairing_authorized=True,
                        confirm_local_approval=confirm, emit=emit, create=args.create_journal,
                        windows_private_dir_confirmed=args.windows_private_dir_confirmed))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f'STOP: {error}; journal preserved, no automatic erase/retry.', file=sys.stderr)
        raise SystemExit(1)
