from pathlib import Path
import subprocess,os,json
D=Path(__file__).resolve().parent;env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME='/tmp/xclk-cuts-replay')
for mode,flags in [('',[]),('optimized_',['-O'])]:
 for i in range(4):
  d=D/'final_validation'/f'saved_cut_{mode}{i}';board=d/'mainboard_revD.kicad_pcb';subprocess.run(['/usr/bin/python3',*flags,str(D/'fill_one.py'),str(board)],check=True,env=env);subprocess.run(['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--format','json','-o',str(d)+'_drc.json',str(board)],check=True,env=env)
