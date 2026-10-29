from pathlib import Path
import json,subprocess,os,uuid
D=Path(__file__).resolve().parent;S=D.parent/'mainboard_href3_candidate';O=D/'guards';O.mkdir(exist_ok=True)
expected=json.loads((S/'href_Broute_expected_new.json').read_text());expected.update(json.loads((S/'href3b_candidate_expected_new.json').read_text()));key=next(iter(expected));bad=expected.copy();bad[key]='WRONG_LITERAL_TEST';cases={'good':json.dumps(expected),'bad_net':json.dumps(bad),'empty':'{}','missing':json.dumps({str(uuid.uuid4()):'CAM_HREF'}),'duplicate':'{"'+key+'":"CAM_HREF","'+key+'":"GND"}'};rows=[]
for opt in [False,True]:
 for case,contents in cases.items():
  tag=case+('_O' if opt else '_normal');c=O/(tag+'.json');c.write_text(contents);mark=O/(tag+'.marker');out=O/(tag+'.rpt');cmd=['/usr/bin/python3']+(['-O'] if opt else [])+[str(S/'validate_expected.py'),str(S/'mainboard_revD.kicad_pcb'),str(c)]
  r=subprocess.run(cmd,capture_output=True,text=True);(O/(tag+'.stdout')).write_text(r.stdout);(O/(tag+'.stderr')).write_text(r.stderr);drc=None
  if r.returncode==0:
   mark.write_text('guard returned success');q=subprocess.run(['kicad-cli','pcb','drc','--exit-code-violations','--all-track-errors','--schematic-parity','--severity-all','-o',str(out),str(S/'mainboard_revD.kicad_pcb')],capture_output=True,text=True);drc=q.returncode;(O/(tag+'.drc.log')).write_text(q.stdout+q.stderr)
  ok=(r.returncode==0 and drc==5 and out.exists()) if case=='good' else (r.returncode!=0 and not mark.exists() and not out.exists())
  rows.append({'case':tag,'guard_exit':r.returncode,'drc_exit':drc,'after_guard_marker':mark.exists(),'expected_result':ok})
  if not ok:raise RuntimeError('guard failure '+tag)
(D/'guard_review.json').write_text(json.dumps(rows,indent=2));print('10/10 expected; good DRC exits5; bad blocked before DRC')
