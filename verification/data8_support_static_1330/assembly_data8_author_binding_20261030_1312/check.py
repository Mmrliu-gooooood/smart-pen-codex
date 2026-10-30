from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;W=O.parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
packs=[('hardware','smart_pen_next_20261028/hardware/data_bias_relocate_1242','8f534ddbb2ec79d4f9a2e625fe0850fc42076e4f61716819cdecefe3dfed027c'),('mechanical','assembly_data8_review_20261030_1256','8613efbde985e92fc644e32a24984b32cc046c5615fd7e0200e59fa8c99b4403')];out=[]
for kind,rel,expected in packs:
 root=W/rel;m=root/'manifest.json'
 if h(m)!=expected:raise RuntimeError('manifest changed')
 j=json.load(open(m));n=0
 for f,x in j['files'].items():
  hh=x['sha256']if isinstance(x,dict)else x
  if h(root/f)!=hh:raise RuntimeError('file changed '+f)
  n+=1
 if h(m)!=expected:raise RuntimeError('manifest changed during check')
 out.append({'kind':kind,'manifest_sha256':expected,'verified_files':n})
board=W/packs[0][1]/'native/mainboard_revD.kicad_pcb';sha=h(board)
if sha!='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad':raise RuntimeError('PCB revision changed')
r=json.load(open(W/packs[1][1]/'results.json'))['stages'][0]
if r['sha256']!=sha:raise RuntimeError('mechanical candidate binding')
(O/'results.json').write_text(json.dumps({'status':'PASS_EXACT_AUTHOR_FREEZE_BINDING_NO_GLOBAL_RELEASE','pcb_sha256':sha,'packages':out,'mechanical_report_retained_unmodified':True,'electrical_independent_verdict':'separate; not inferred here'},indent=2)+'\n')
