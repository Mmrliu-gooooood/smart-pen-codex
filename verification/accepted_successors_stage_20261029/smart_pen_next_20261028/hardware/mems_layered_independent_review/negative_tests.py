from pathlib import Path
import pcbnew as p,json,subprocess,sys,shutil
D=Path(__file__).resolve().parent;G=D/'guard_boards';G.mkdir(exist_ok=True);rows=[]
for label,mutation,error in [('central_tracks_enabled',lambda z:z.SetDoNotAllowTracks(False),'central flags/layer'),('central_shift',lambda z:z.Move(p.VECTOR2I(p.FromMM(.1),0)),'central outline'),('F_vias_enabled',lambda z:z.SetDoNotAllowVias(False),'F body flags/layer'),('F_pour_enabled',lambda z:z.SetDoNotAllowCopperPour(False),'F body flags/layer')]:
 b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));z=next(z for z in b.Zones()if z.GetZoneName()==('LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN'if label.startswith('central')else'LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA'));mutation(z);path=G/(label+'.kicad_pcb');p.SaveBoard(str(path),b)
 for optimized in [False,True]:
  r=subprocess.run([sys.executable,*(['-O']if optimized else[]),str(D/'check.py'),str(path)],capture_output=True,text=True)
  if r.returncode==0 or error not in r.stderr:raise RuntimeError('Wrong negative rejection '+label+r.stderr[-400:])
  rows.append({'case':label,'optimized':optimized,'exit':r.returncode,'expected_error':error})
# Actual native rule detection, not merely a hardcoded flag validator.
for label,via in [('native_central_track',False),('native_body_through_via',True)]:
 dest=G/label;shutil.copytree(D/'native',dest,dirs_exist_ok=True);path=dest/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(path));net=b.FindNet('GND')
 if via:
  t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(p.FromMM(3.15),p.FromMM(82.5)));t.SetWidth(p.F_Cu,p.FromMM(.45));t.SetDrill(p.FromMM(.2));t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(3.7),p.FromMM(81.8)));t.SetEnd(p.VECTOR2I(p.FromMM(4.3),p.FromMM(82.2)));t.SetWidth(p.FromMM(.15));t.SetLayer(p.F_Cu)
 t.SetNet(net);b.Add(t);p.SaveBoard(str(path),b)
 r=subprocess.run(['kicad-cli','pcb','drc','--all-track-errors','--severity-all','--schematic-parity','--exit-code-violations','--format','json','-o',str(dest/'drc.json'),str(path)],capture_output=True,text=True);d=json.loads((dest/'drc.json').read_text());hits=[v for v in d['violations']if v['type']=='items_not_allowed' and any(i.get('uuid')==t.m_Uuid.AsString()for i in v['items'])]
 expected_rule='LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA' if via else 'LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN'
 if r.returncode!=5 or not any(expected_rule in v['description'] for v in hits):raise RuntimeError('Native keepout negative not detected '+label)
 rows.append({'case':label,'native_exit':r.returncode,'expected_keepout_hits':len(hits),'rules':[v['description']for v in hits]})
print(json.dumps(rows,indent=2))
