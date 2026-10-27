"""Full host gate: missing upstream/dependencies/compiler or ANY skipped test fails."""
import argparse
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream-pc-src',required=True)
    a=p.parse_args();source=Path(a.upstream_pc_src).resolve()
    if not (source/'digital_pen/engine/server.py').is_file():p.error('expected original pc/src directory')
    os.environ['DIGITAL_PEN_SOURCE']=str(source)
    sys.path.insert(0,str(source))
    for module in ['cv2','numpy','fastapi','httpx','uvicorn','bleak']:
        try:importlib.import_module(module)
        except ImportError as error:p.error(f'required dependency {module}: {error}; use setup_host.py')
    if not shutil.which('cc'):p.error('required C11 compiler cc missing (use WSL/developer toolchain for crosswire tests)')
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root))
    suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:return 1
    with tempfile.TemporaryDirectory() as t:
        binary=Path(t)/'portable-test'
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(root/'firmware/portable'),str(root/'firmware/portable/pen.c'),str(root/'tests/test_portable.c'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
    print('FULL HOST GATE PASS: no skipped tests. Radio/camera/physical flash remain untested.')
    return 0
if __name__=='__main__':sys.exit(main())
