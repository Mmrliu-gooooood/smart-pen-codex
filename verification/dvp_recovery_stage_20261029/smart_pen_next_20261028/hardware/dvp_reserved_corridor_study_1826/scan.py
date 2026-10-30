from pathlib import Path
import os,json,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent; base=D.parent/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'
b=p.LoadBoard(str(base))
def shape(o,l):
 q=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(q,l,0,50,p.ERROR_OUTSIDE);return q
def intersects(a,c):
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(a,c);return q.Area()>1
lanes=[]
for l in [p.F_Cu,p.In3_Cu,p.B_Cu]:
 for x in [12.0,12.3,12.6,12.9,13.2,13.5]:
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(round(x*1e6),32000000));t.SetEnd(p.VECTOR2I(round(x*1e6),89000000));t.SetWidth(449998);t.SetLayer(l); copper=shape(t,l) # 0.15 track plus 2*0.15 clearance minus 2nm boundary tolerance
  pad=[];tr=[];rules=[]
  for f in b.GetFootprints():
   for a in f.Pads():
    if a.IsOnLayer(l):
     g=shape(a,l)
     if intersects(copper,g):pad.append({'ref':f.GetReference(), 'pad':a.GetNumber(),'net':a.GetNetname(),'clearance_below_0p15':True})
  for a in b.GetTracks():
   if a.IsOnLayer(l):
    g=shape(a,l)
    if intersects(copper,g):
     tr.append({'uuid':a.m_Uuid.AsString(),'net':a.GetNetname(),'type':'via' if isinstance(a,p.PCB_VIA) else 'track','clearance_below_0p15':True,'center_xy':[a.GetPosition().x/1e6,a.GetPosition().y/1e6]})
  for z in b.Zones():
   if z.GetIsRuleArea() and z.IsOnLayer(l) and z.GetDoNotAllowTracks():
    g=z.Outline()
    if intersects(copper,g):rules.append(z.m_Uuid.AsString())
  lanes.append({'layer':b.GetLayerName(l),'x':x,'y':[32,89],'width':.15,'pad_blockers':pad,'copper_blockers':tr,'keepout_blockers':rules})
nets={}
for lane in lanes:
 for t in lane['copper_blockers']:
  nets.setdefault(t['net'],{})[t['uuid']]=t
out={'status':'READONLY_NOFAB_NOT_A_ROUTED_BOARD','source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'scan_scope':'native finite copper/pad gap <.15mm, full straight lanes y32..89; tail/fanout/reference and body not qualified','lanes':lanes,'unique_obstructing_net_objects':{n:list(v.values()) for n,v in sorted(nets.items())}}
(D/'scan.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'lanes':[{'layer':a['layer'],'x':a['x'],'pads':len(a['pad_blockers']),'copper':len(a['copper_blockers']),'keepouts':len(a['keepout_blockers'])}for a in lanes],'nets':{n:len(v)for n,v in nets.items()}},indent=2))
