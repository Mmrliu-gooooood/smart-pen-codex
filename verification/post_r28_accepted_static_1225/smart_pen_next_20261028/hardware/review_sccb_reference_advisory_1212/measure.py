from pathlib import Path
import os,sys,json,hashlib,math
os.environ.update(XDG_CONFIG_HOME='/tmp/sccbrefreview/config',XDG_CACHE_HOME='/tmp/sccbrefreview/cache',XDG_DATA_HOME='/tmp/sccbrefreview/data')
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'sccb_bypass_native_1131/native/mainboard_revD.kicad_pcb';data=S.read_bytes();assert hashlib.sha256(data).hexdigest()=='faf2912fb2896891b21c1e7f96f8bdc65253cac04ec47b31bfde81e3ded3e424';(D/'snapshot.kicad_pcb').write_bytes(data);sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'snapshot.kicad_pcb'));xy=lambda v:[v.x/1e6,v.y/1e6];vias=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)];source=next(v for v in vias if v.GetNetname()=='CAM_SDA'and v.GetPosition().y<70000000);sink=next(v for v in vias if v.GetNetname()=='CAM_SDA'and v.GetPosition().y>70000000)
info={'vias':[],'planes':[],'small_crossing':[]}
for v in [source,sink]:
 nearest=sorted([q for q in vias if q.GetNetname()=='GND'],key=lambda q:math.dist(xy(q.GetPosition()),xy(v.GetPosition())))[:3];info['vias'].append({'net':v.GetNetname(),'xy':xy(v.GetPosition()),'nearest_GND':[{'xy':xy(q.GetPosition()),'distance_mm':math.dist(xy(q.GetPosition()),xy(v.GetPosition()))}for q in nearest]})
for z in b.Zones():
 if not z.GetIsRuleArea():info['planes'].append({'layer':b.GetLayerName(z.GetLayer()),'net':z.GetNetname(),'min_thickness_mm':z.GetMinThickness()/1e6})
def planes(board):
 ps={}
 for z in board.Zones():
  if not z.GetIsRuleArea():ps.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return ps
ps=planes(b);target=next(v for v in vias if v.m_Uuid.AsString()=='2d9a88b6-696a-4b82-9d44-db35fd53f9d7');plane=ps[p.In4_Cu];hole=None
for i in range(plane.OutlineCount()):
 for j in range(plane.HoleCount(i)):
  h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(i,j))
  if h.Contains(target.GetPosition()):hole=h
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.GetNetname()!='CAM_SDA'or t.GetLayer()!=p.In3_Cu:continue
 q=shape(t,p.In3_Cu);q.BooleanIntersection(hole)
 if q.Area()>0:
  bb=q.BBox();info['small_crossing'].append({'uuid':t.m_Uuid.AsString(),'segment':[xy(t.GetStart()),xy(t.GetEnd())],'area_mm2':q.Area()/1e12,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6],'foreign_via':xy(target.GetPosition())})
# Counterfactual removes only foreign CAM_CT/CAM_ON source-neighbor vias to separate merged-hole excess.
refs=[(p.F_Cu,p.In1_Cu),(p.In3_Cu,p.In4_Cu),(p.In3_Cu,p.In2_Cu)]
projections={}
for layer,ref in refs:
 q=p.SHAPE_POLY_SET()
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='CAM_SDA'and t.GetLayer()==layer:q.BooleanAdd(shape(t,layer))
 projections[(layer,ref)]=q
for u in ['b58acc3d-d2c1-4178-94b7-659cccc17876','5cdd688f-237f-4e73-a8ef-6af583aa886b']:b.Remove(next(t for t in b.GetTracks()if t.m_Uuid.AsString()==u))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());new=planes(b);info['foreign_source_hole_counterfactual']=[]
for key,q in projections.items():
 layer,ref=key;x=p.SHAPE_POLY_SET();x.BooleanSubtract(q,ps[ref]);y=p.SHAPE_POLY_SET();y.BooleanSubtract(q,new[ref]);reg=p.SHAPE_POLY_SET();reg.BooleanSubtract(x,y);info['foreign_source_hole_counterfactual'].append({'signal':b.GetLayerName(layer),'ref':b.GetLayerName(ref),'before_missing_mm2':x.Area()/1e12,'after_foreign_vias_removed_missing_mm2':y.Area()/1e12,'recovered_projection_mm2':reg.Area()/1e12})
(D/'measurements.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
