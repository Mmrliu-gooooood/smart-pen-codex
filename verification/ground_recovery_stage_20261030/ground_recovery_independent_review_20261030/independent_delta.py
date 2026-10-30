from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/schmitt-independent-delta'
import pcbnew as p
O=Path(__file__).resolve().parent;R=O.parent/'smart_pen_next_20261028';A=R/'hardware/camera_schmitt_native_0745/native';B=R/'hardware/ground_recovery_native_0818/native'
a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'))
def fills(board):
 out={}
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  raw=z.GetFilledPolysList(z.GetLayer())
  if any(raw.HoleCount(i)for i in range(raw.OutlineCount())):raise RuntimeError('raw already holes')
  n=p.SHAPE_POLY_SET(raw);n.Unfracture()
  for x,y in [(raw,n),(n,raw)]:
   q=p.SHAPE_POLY_SET();q.BooleanSubtract(x,y)
   if q.Area()>1e8:raise RuntimeError('material change')
  out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(n)
 return out
fa,fb=fills(a),fills(b);at={t.m_Uuid.AsString():t for t in a.GetTracks()};bt={t.m_Uuid.AsString():t for t in b.GetTracks()};loss=[];tested=0
for u,t in at.items():
 if u not in bt or isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 for l in {p.F_Cu:[p.In1_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu],p.B_Cu:[p.In4_Cu]}.get(t.GetLayer(),[]):
  tested+=1;s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,t.GetLayer(),0,250,p.ERROR_INSIDE);x=p.SHAPE_POLY_SET();x.BooleanIntersection(s,fa[l]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(s,fb[l]);x.BooleanSubtract(y)
  if x.Area()>1e4:loss.append({'uuid':u,'net':t.GetNetname(),'layer':b.GetLayerName(l),'mm2':x.Area()/1e12})
fps={f.GetReference():f for f in b.GetFootprints()};parts={}
for ref in ['U205','C209','R202']:
 f=fps[ref];parts[ref]={'value':f.GetValue(),'footprint':f.GetFPIDAsString(),'xy_mm':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'rotation':f.GetOrientationDegrees(),'mpn':f.GetFieldByName('MPN').GetText()if f.GetFieldByName('MPN')else None,'pads':[{'number':q.GetNumber(),'net':q.GetNetname(),'xy_mm':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'size_mm':[q.GetSize().x/1e6,q.GetSize().y/1e6]}for q in f.Pads()]}
files=lambda d:{str(f.relative_to(d)):hashlib.sha256(f.read_bytes()).hexdigest()for f in d.rglob('*')if f.is_file()};x,y=files(A),files(B);diff=[{'path':s,'before':x.get(s),'after':y.get(s)}for s in sorted(x.keys()|y.keys())if x.get(s)!=y.get(s)]
print(json.dumps({'reference_tests':tested,'additional_old_signal_losses':loss,'parts':parts,'native_file_delta':diff,'parent_files':len(x),'candidate_files':len(y),'removed_copper':sorted(at.keys()-bt.keys()),'added_copper':sorted(bt.keys()-at.keys()),'method':'Independently implemented actual polygon comparisons, no masks, one-shot guarded native unfracture; native part geometry extracted directly.'},indent=2))
