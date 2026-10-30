from pathlib import Path
import re,json,sys
import os
os.environ["XDG_CONFIG_HOME"]="/tmp/review1312exact"
import pcbnew as p
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'))
from finite_copper import shape
from native_polygon import native_fractured_once
A=D.parent/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb';B=D/'native/mainboard_revD.kicad_pcb'
def blocks(s):
 dep=0;quoted=False;esc=False;start=0
 for i,c in enumerate(s):
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':
   dep+=1
   if dep==2:start=i
  elif c==')':
   if dep==2:yield s[start:i+1]
   dep-=1
def index(path):
 out={}
 for x in blocks(path.read_text()):
  u=re.search(r'\(uuid "([^"]+)"\)',x)
  if u:out[u.group(1)]=x
 return out
old=index(A);new=index(B);m=json.loads((D/'materialization.json').read_text());changed=[];counts={}
for u,x in old.items():
 kind=x.split()[0][1:];counts[kind]=counts.get(kind,0)+1
 if u in new and x!=new[u]:changed.append({'uuid':u,'kind':kind,'reference':re.search(r'\(property "Reference" "([^"]+)"',x).group(1)if kind=='footprint'else None})
assert all(x['kind'] in ['footprint','zone'] for x in changed),changed
assert {x['reference']for x in changed if x['kind']=='footprint'}=={'R210','R217'}
assert set(old)-set(new)==set(m['removed'])
assert set(new)-set(old)==set(m['added'])
a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));aa={t.m_Uuid.AsString():t for t in a.GetTracks()};bb={t.m_Uuid.AsString():t for t in b.GetTracks()}
def plane(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa=plane(a);pb=plane(b);refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]};res=[];n=0;direct_losses=[]
for u,t in aa.items():
 if u not in bb or isinstance(t,p.PCB_VIA):continue
 for r in refs.get(t.GetLayer(),[]):
  n+=1;d=p.SHAPE_POLY_SET();d.BooleanSubtract(pa[r],pb[r]);d.BooleanIntersection(shape(t,t.GetLayer()));
  if d.Area()>0:direct_losses.append({'uuid':u,'area_mm2':d.Area()/1e12})
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),pa[r]);x.BooleanSubtract(pb[r]);v=x.Area()/1e12
  if v>0:
   selfloss=p.SHAPE_POLY_SET();selfloss.BooleanIntersection(shape(t,t.GetLayer()),pa[r]);selfloss.BooleanSubtract(pa[r]);delta=p.SHAPE_POLY_SET();delta.BooleanSubtract(pa[r],pb[r]);delta.BooleanIntersection(shape(t,t.GetLayer()));res.append({'uuid':u,'reference':b.GetLayerName(r),'area_mm2':v,'self_subtraction_residual_mm2':selfloss.Area()/1e12,'plane_delta_first_loss_mm2':delta.Area()/1e12,'net':t.GetNetname(),'vertices_nm':[[[x.COutline(i).CPoint(j).x,x.COutline(i).CPoint(j).y]for j in range(x.COutline(i).PointCount())]for i in range(x.OutlineCount())]})
print(json.dumps({'raw_changed_blocks':changed,'raw_old_block_counts':counts,'exact_retained_projection_count':n,'plane_delta_first_all_positive_losses':direct_losses,'positive_loss_without_threshold':res},indent=2))
