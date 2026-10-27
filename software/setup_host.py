"""Explicit local venv setup. Downloads dependencies only into chosen directory."""
import argparse
from pathlib import Path
import subprocess
import os
import venv
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--venv',required=True,help='new local environment directory')
a=p.parse_args();target=Path(a.venv).resolve()
if target.exists():p.error('choose a NEW directory; existing environments are not modified')
venv.EnvBuilder(with_pip=True).create(target)
python=target/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
subprocess.run([str(python),'-m','pip','install','-r',str(Path(__file__).with_name('requirements-host.txt'))],check=True)
print(f'Installed only in {target}; run {python} software/verify_host.py --upstream-pc-src PATH')
