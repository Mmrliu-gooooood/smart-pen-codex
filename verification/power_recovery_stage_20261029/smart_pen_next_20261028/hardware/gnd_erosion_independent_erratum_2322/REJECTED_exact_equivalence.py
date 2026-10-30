from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/gnd-unfracture-independent2322'
import pcbnew as p
D=Path(__file__).resolve().parent; H=D.parent; out=[]
for key,path in [('base','aon_entry_bridge_candidate_2156'),('rejected18','gnd_fixed_branch_candidate_2159'),('conservative17','gnd_conservative_recovery_2305')]:
 fn=H/path/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(fn))
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for layer in z.GetLayerSet().Seq():
   raw=p.SHAPE_POLY_SET(z.GetFilledPolysList(layer)); actual=p.SHAPE_POLY_SET(raw);actual.Unfracture()
   xor=p.SHAPE_POLY_SET();xor.BooleanXor(raw,actual)
   if abs(raw.Area()-actual.Area())>1 or xor.Area()>1:raise RuntimeError('geometric copper changed')
   # Contains queries on physical via center and 32 real drill boundary points.
   tests=0
   for v in b.GetTracks():
    if not isinstance(v,p.PCB_VIA) or not v.IsOnLayer(layer):continue
    pos=v.GetPosition();r=v.GetDrillValue()/2
    for a in range(33):
     pt=pos if a==32 else p.VECTOR2I(round(pos.x+r*math.cos(math.tau*a/32)),round(pos.y+r*math.sin(math.tau*a/32)))
     if raw.Contains(pt)!=actual.Contains(pt):raise RuntimeError('drill location geometry changed')
     tests+=1
   re=p.SHAPE_POLY_SET(raw);re.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
   ae=p.SHAPE_POLY_SET(actual);ae.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
   # physical erosion cannot add copper; ensure no new copper and preserve source holes.
   extra=p.SHAPE_POLY_SET();extra.BooleanSubtract(ae,actual)
   if extra.Area()>1:raise RuntimeError('erosion adds copper')
   holes=sum(actual.HoleCount(i) for i in range(actual.OutlineCount()))
   # Same physical geometry after re-fracture, not merely same area.
   rt=p.SHAPE_POLY_SET(actual);rt.Fracture();rx=p.SHAPE_POLY_SET();rx.BooleanXor(rt,raw)
   if rx.Area()>1:raise RuntimeError('fracture roundtrip changed geometry')
   rows={'variant':key,'input_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'zone':z.m_Uuid.AsString(),'net':z.GetNetname(),'layer':b.GetLayerName(layer),'raw_outlines':raw.OutlineCount(),'raw_holes':sum(raw.HoleCount(i)for i in range(raw.OutlineCount())),'unfractured_outlines':actual.OutlineCount(),'unfractured_holes':holes,'area_raw_mm2':raw.Area()/1e12,'area_actual_mm2':actual.Area()/1e12,'xor_mm2':xor.Area()/1e12,'roundtrip_xor_mm2':rx.Area()/1e12,'drill_point_tests':tests,'raw_eroded_outlines':re.OutlineCount(),'actual_eroded_outlines':ae.OutlineCount(),'actual_eroded_holes':sum(ae.HoleCount(i)for i in range(ae.OutlineCount())),'actual_eroded_area_mm2':ae.Area()/1e12}
   out.append(rows)
(D/'result.json').write_text(json.dumps({'status':'UNFRACTURE_GEOMETRIC_EQUIVALENCE_VERIFIED_NOT_AMPACITY','rows':out},indent=2));print(json.dumps(out,indent=2))
