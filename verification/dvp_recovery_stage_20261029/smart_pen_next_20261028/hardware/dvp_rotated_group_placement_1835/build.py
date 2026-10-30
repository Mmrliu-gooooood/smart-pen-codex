from pathlib import Path
import os,json,hashlib,shutil
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config';os.environ['XDG_CACHE_HOME']='/tmp/pen-layout-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-layout-data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'j202_low_speed_reference_candidate/native';N=D/'native';shutil.copytree(S,N,dirs_exist_ok=True)
b=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));f={x.GetReference():x for x in b.GetFootprints()};change={}
for r in ['U201','U202','U203']:
 q=f[r];change[r]={'before_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'before_angle':q.GetOrientationDegrees()};q.SetOrientationDegrees(-90)
for r,x,y in [('C201',11.75,31.1375),('C202',11.75,36.8625),('C203',10.35,43.1375),('C204',10.35,48.8625),('C205',10.35,53.1375),('C206',10.35,58.8625)]:
 q=f[r];change[r]={'before_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'before_angle':q.GetOrientationDegrees()};q.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));q.SetOrientationDegrees(0)
for i in range(8):
 r='R'+str(224+i);q=f[r];change[r]={'before_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'before_angle':q.GetOrientationDegrees()};q.SetPosition(p.VECTOR2I(q.GetPosition().x,round((39.1 if i<4 else 40.9)*1e6)))
for r,y in [('R232',50.6),('R235',60.6)]:
 q=f[r];change[r]={'before_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'before_angle':q.GetOrientationDegrees()};q.SetPosition(p.VECTOR2I(10600000,round(y*1e6)))
for r,x,y,flip in [('R218',4.5,41.5,True),('R219',7.5,41.5,True),('R221',3,56,True),('R222',6,56,True),('R223',6,58.6,True),('R232',10.6,50.9,False),('R233',1.5,50.9,False),('R234',7.5,50.9,False),('R206',4.5,50.9,False)]:
 q=f[r]
 if r not in change:change[r]={'before_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'before_angle':q.GetOrientationDegrees(),'before_layer':q.GetLayerName()}
 if flip:q.Flip(q.GetPosition(),False)
 q.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));q.SetOrientationDegrees(0)
for r in change:
 q=f[r];change[r].update({'after_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'after_angle':q.GetOrientationDegrees(),'after_layer':q.GetLayerName()})
# Intentionally a placement-only derivative: no old copper silently retained under moved pads.
removed=list(b.GetTracks())
for t in removed:b.Remove(t)
for z in b.Zones():
 if not z.GetIsRuleArea():z.UnFill()
p.SaveBoard(str(N/'mainboard_revD.kicad_pcb'),b)
(D/'placement_changes.json').write_text(json.dumps({'status':'PLACEMENT_ONLY_ALL_ROUTING_REMOVED_NOFAB','base_sha256':hashlib.sha256((S/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'changed':change,'removed_track_via_count':len(removed),'unchanged_source_and_interface':True,'not_a_successor_accepted_electrical_board':True},indent=2)+'\n')
# Finite courtyard polygon overlaps for all distinct same-side footprints.
coll=[]
for f0 in f.values():f0.BuildCourtyardCaches()
for i,a in enumerate(list(f.values())):
 for c in list(f.values())[:i]:
  if a.GetLayer()!=c.GetLayer():continue
  qa=a.GetCourtyard(a.GetLayer());qc=c.GetCourtyard(c.GetLayer());q=p.SHAPE_POLY_SET();q.BooleanIntersection(qa,qc)
  if q.Area()>1:coll.append({'refs':[a.GetReference(),c.GetReference()],'overlap_mm2':q.Area()/1e12,'involves_changed':a.GetReference()in change or c.GetReference()in change})
(D/'courtyard.json').write_text(json.dumps({'overlaps':coll},indent=2)+'\n');print(json.dumps(coll,indent=2))
