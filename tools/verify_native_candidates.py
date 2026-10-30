#!/usr/bin/env python3
"""Portable KiCad 9 candidate review. Exit 5 means known INCOMPLETE hardware, not success."""
import argparse, collections, hashlib, json, os, pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BOARDS={
 'power':('hardware/power14_single_feed_revB','power_integrated_study','94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc'),
 'mainboard':('hardware/mainboard_href2_candidate','mainboard_revD','228b04b42c45ebb37ca96a27d84a4f7a48f3e2b805c63dff0c2c6a5be2e6fb69')}
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
def run(args,env,cwd,out):
 r=subprocess.run(args,env=env,cwd=cwd,capture_output=True,text=True)
 out.with_suffix('.stdout').write_text(r.stdout);out.with_suffix('.stderr').write_text(r.stderr)
 return r

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--board',choices=['power','mainboard','all'],default='all');p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--kicad-share',type=pathlib.Path,default=pathlib.Path('/usr/share/kicad'));a=p.parse_args()
 require(shutil.which('kicad-cli'),'kicad-cli is required');o=a.output.resolve();o.mkdir(parents=True,exist_ok=False)
 env=dict(os.environ)
 for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
  d=o/n;d.mkdir();env[k]=str(d)
 env['KICAD9_FOOTPRINT_DIR']=str(a.kicad_share.resolve()/'footprints');env['KICAD9_SYMBOL_DIR']=str(a.kicad_share.resolve()/'symbols')
 config=o/'config/kicad/9.0';config.mkdir(parents=True)
 for n in ['fp-lib-table','sym-lib-table']:
  src=a.kicad_share/'template'/n;require(src.is_file(),f'Missing KiCad library table {src}; set --kicad-share');shutil.copyfile(src,config/n)
 v=run(['kicad-cli','version'],env,o,o/'version');require(v.returncode==0 and v.stdout.strip().startswith('9.'),'KiCad 9 required for recorded baselines')
 summaries=[];bad=False;incomplete=False
 for key in BOARDS if a.board=='all' else [a.board]:
  rel,name,sha=BOARDS[key];source=ROOT/rel;pcb=source/(name+'.kicad_pcb');require(hashlib.sha256(pcb.read_bytes()).hexdigest()==sha,f'{key} source hash changed')
  manifest=source/('SINGLE_FEED_REVB_MANIFEST.json' if key=='power' else 'manifest.json')
  for relpath, expected_hash in json.loads(manifest.read_text())['files'].items():
   require(hashlib.sha256((source/relpath).read_bytes()).hexdigest()==expected_hash,f'{key} frozen file changed: {relpath}')
  work=o/key;shutil.copytree(source,work);reports=o/(key+'_reports');reports.mkdir()
  erc=reports/'erc.json';drc=reports/'drc.json'
  e=run(['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(erc),str(work/(name+'.kicad_sch'))],env,work,reports/'erc_run')
  d=run(['kicad-cli','pcb','drc','--severity-all','--all-track-errors','--schematic-parity','--exit-code-violations','--format','json','-o',str(drc),str(work/(name+'.kicad_pcb'))],env,work,reports/'drc_run')
  require(erc.is_file() and drc.is_file(),'Missing fresh JSON reports');ej=json.loads(erc.read_text());dj=json.loads(drc.read_text())
  require(isinstance(ej.get('sheets'),list),'Unexpected ERC JSON schema')
  ev=[v for s in ej['sheets'] for v in s['violations']];types=dict(collections.Counter(v['type'] for v in dj['violations']));parity=dict(collections.Counter(v['type'] for v in dj['schematic_parity']))
  counts={'erc':len(ev),'violations':types,'unconnected':len(dj['unconnected_items']),'parity':parity}
  expected={'erc':0,'violations':{},'unconnected':0,'parity':{}} if key=='power' else {'erc':0,'violations':{'via_dangling':33,'track_dangling':3},'unconnected':2,'parity':{'missing_footprint':16}}
  matched=counts==expected and e.returncode==0 and d.returncode==(0 if key=='power' else 5)
  bad|=not matched;incomplete|=key=='mainboard'
  summaries.append({'board':key,'sha256':sha,'erc_exit':e.returncode,'drc_exit':d.returncode,'counts':counts,'expected':expected,'matches_recorded_baseline':matched,'status':'INCOMPLETE_NOFAB' if key=='mainboard' else 'STATIC_CHECKS_ONLY_NOFAB'})
 result={'kicad':v.stdout.strip(),'boards':summaries,'all_expected':not bad,'manufacturing_approved':False};(o/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return 1 if bad else 5 if incomplete else 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print('VALIDATION ERROR: '+str(e),file=sys.stderr);sys.exit(1)
