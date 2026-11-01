from pathlib import Path
import hashlib,json,subprocess,sys,shutil
O=Path(__file__).resolve().parent; A=O.parent/'optics_paper_screen_20261031_1752'; R=O.parent/'publication_20261031/target_repo'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((A/'MANIFEST.json').read_text()); bad=[p for p,v in m['files'].items() if h(A/p)!=v]
report={'manifest_sha256':h(A/'MANIFEST.json'),'manifest_entries':len(m['files']),'manifest_mismatches':bad,'git_head':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()}
for name,args in [('normal',[sys.executable,'-B','-m','unittest','-v']),('optimized',[sys.executable,'-B','-O','-m','unittest','-v']),('sweep',[sys.executable,'-B','sweep.py']),('crops',[sys.executable,'-B','compare_crops.py'])]:
 p=subprocess.run(args,cwd=O,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(O/(name+'.log')).write_text(p.stdout);report[name+'_exit']=p.returncode
for p in ['sweep.csv','summary.json','crop_comparison.json']:report[p+'_identical']=h(O/p)==h(A/p)
for name in ['sweep_active.py','controls_active.py']:
 code=(A/'decoder_probe'/name).read_text().replace("ROOT=OUT.parents[1]/'publication_20261031/target_repo'",'ROOT=Path('+repr(str(R))+')')
 (O/name).write_text(code)
(O/'initial_results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
