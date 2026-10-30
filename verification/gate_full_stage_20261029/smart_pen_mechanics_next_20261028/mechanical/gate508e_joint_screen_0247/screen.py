import os,sys,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/gate508e';os.environ['XDG_DATA_HOME']='/tmp/gate508e'
import pcbnew as p
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;M=R.parent;H=M.parents[1]/'smart_pen_next_20261028/hardware';V=A.Vector
src=H/'gate_control_output_candidate/mainboard_revD.kicad_pcb';old=H/'gate_input_local_routing/mainboard_revD.kicad_pcb'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def req(b,m):
 if not b:raise ValueError(m)
req(sha(src)=='508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35','hash')
def snapshot(path):
 b=p.LoadBoard(str(path));out={}
 for f in b.GetFootprints():
  out[f.GetReference()]=dict(x=f.GetPosition().x/1e6,y=f.GetPosition().y/1e6,angle=f.GetOrientationDegrees(),side=f.GetLayerName(),fp=str(f.GetFPID().GetLibItemName()),pads=sorted((q.GetNumber(),q.GetNetname(),q.GetPosition().x/1e6,q.GetPosition().y/1e6,q.GetSize().x/1e6,q.GetSize().y/1e6,int(q.GetShape()),q.GetOrientationDegrees())for q in f.Pads()))
 return b,out
b,n=snapshot(src);_,o=snapshot(old);changed=sorted(k for k in n if n[k]!=o[k]);req(changed==['C302','R301','R302','TP301'],'unexpected delta '+str(changed));req(n.keys()==o.keys(),'count')
B=2.264793176328504;dims={'R301':(1.7,.9,.7),'R302':(1.7,.9,.7),'C302':(1.75,.95,1.1),'TP301':(1,1,.15)}
# Retain old TP .15 mm conservative assembly budget; actual rectangular copper lies inside board stack.
new={};contracts={}
for ref,(L,W,h) in dims.items():
 f=next(f for f in b.GetFootprints()if f.GetReference()==ref);v=n[ref];req(v['side']=='B.Cu' and v['angle']==180,'orientation');x=v['x'];y=v['y']
 bs=[[x-L/2,y-W/2,x+L/2,y+W/2]]
 for q in f.Pads():
  bb=q.GetBoundingBox();bs.append([bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6])
 x0,y0,x1,y1=min(t[0]for t in bs),min(t[1]for t in bs),max(t[2]for t in bs),max(t[3]for t in bs)
 new['CTX_'+ref]=Part.makeBox(x1-x0,h,y1-y0,V(x0-7,B-h,127-y1));contracts[ref]=dict(native=v,body_max=[L,W,h],union_pad_bounds=[x0,y0,x1,y1],pen_bounds=[x0-7,B-h,127-y1,x1-7,B,127-y0])
def disjoint(a,b):
 x=a.BoundBox;y=b.BoundBox
 return any(getattr(x,k+'Max')<=getattr(y,k+'Min')+1e-9 or getattr(y,k+'Max')<=getattr(x,k+'Min')+1e-9 for k in 'XYZ')
def hits(s,others):
 out=[]
 for k,t in others.items():
  if disjoint(s,t):continue
  v=s.common(t).Volume
  if v>1e-7:out.append([k,v])
 return out
out=dict(source=str(src),sha256=sha(src),prior_sha256=sha(old),changed=changed,footprints=len(n),contracts=contracts,TP_shape_correction='actual native 1x1 rectangular pad, not preliminary circular claim; .15 external budget retained conservatively; copper .035 inside substrate',studies={})
for name,file,prefix in [('RevC',M/'contact_oblique_harness_revC_0038/contact_oblique_harness.FCStd',''),('RevD',M/'common_datum_bench_revD_0100/common_datum_bench.FCStd','REF_')]:
 d=A.openDocument(str(file));S={ob.Label:ob.Shape.copy() for ob in d.Objects if hasattr(ob,'Shape') and ob.TypeId!='App::DocumentObjectGroup'}
 for k,s in new.items():
  key=prefix+k;req(key in S,'missing '+key);S[key]=s
  next(ob for ob in d.Objects if ob.Label==key).Shape=s
 result={'delta_collisions':{},'fixture_collisions':{},'assembly':[]}
 for k,s in new.items():result['delta_collisions'][k]=hits(s,{j:t for j,t in S.items()if j!=prefix+k and j not in ['Context_ONLY','REF_Context_ONLY']})
 req(not any(result['delta_collisions'].values()),name+' delta collision '+str(result['delta_collisions']))
 if name=='RevD':
  parts={k:s for k,s in S.items()if not k.startswith('REF_')};ctx={k[4:]:s for k,s in S.items()if k.startswith('REF_')}
  for k,s in parts.items():
   h=hits(s,ctx)
   if h:result['fixture_collisions'][k]=h
  req(not result['fixture_collisions'],'fixture collision')
  cas={k:s for k,s in ctx.items()if not k.startswith(('CTX_','Harness_','Solder_','StrainBushing'))};board={k:s for k,s in ctx.items()if k.startswith('CTX_')and k!='CTX_power'}
  opened={k:s for k,s in parts.items()if not k.startswith(('PCB_keeper','Keeper_screw','Keeper_hardstop','PCB_side_shim'))}
  for shift in [0,.1,.5,1,2,5,10]:
   hh=[]
   for k,s in board.items():
    q=s.copy();q.translate(V(0,shift,0));hh.extend([[k]+h for h in hits(q,{**opened,**cas})])
   result['assembly'].append(dict(board_shiftY=shift,hits=hh));req(not hh,'assembly')
  # Own illustrative lateral probe envelope, not a selected probe or electrical contact qualification.
  pt=V(n['TP301']['x']-7,B,127-n['TP301']['y']);start=V(-15,-1,pt.z);u=pt-start;unit=u/u.Length
  shaft=Part.makeCylinder(1,u.Length-5,start,unit);cone=Part.makeCone(1,.25,5,start+unit*(u.Length-5),unit);probe=shaft.fuse(cone)
  result['probe_budget_hits']=hits(probe,{k:s for k,s in S.items()if k!='REF_CTX_TP301'})
  pointed=shaft.fuse(Part.makeCone(1,0,5,start+unit*(u.Length-5),unit))
  result['ideal_point_probe_budget_hits']=hits(pointed,{k:s for k,s in S.items()if k!='REF_CTX_TP301'})
  req(bool(result['probe_budget_hits']),'finite tip negative missed')
  result['probe_budget_endpoint']=[pt.x,pt.y,pt.z]
  result['probe_not_actual_selected_tool']=True
 dest=R/(name+'_gate508e.FCStd');d.recompute();d.saveAs(str(dest));A.closeDocument(d.Name);e=A.openDocument(str(dest));result['reopened_valid']=all(ob.Shape.isValid()for ob in e.Objects if hasattr(ob,'Shape'));req(result['reopened_valid'],'invalid');A.closeDocument(e.Name);result['CAD_sha256']=sha(dest);out['studies'][name]=result
out['status']='FINITE_GEOMETRY_SCREEN_NOFAB_NOT_PHYSICAL_ASSEMBLY_OR_FINAL_SHELL';(R/('optimized.json'if sys.flags.optimize else'results.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
