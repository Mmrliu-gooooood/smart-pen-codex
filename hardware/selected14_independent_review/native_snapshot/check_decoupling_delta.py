from pathlib import Path
import pcbnew as p,json,hashlib,html,math
D=Path(__file__).resolve().parent;S=D.parent/'rf_feed_conditional_candidate';a=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()};ta={t.m_Uuid.AsString():t for t in a.GetTracks()};tb={t.m_Uuid.AsString():t for t in b.GetTracks()}
def geom(t):return (t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth())
changed=[]
for uid,t in ta.items():
 if t.GetNetname() not in ['3V3_AON','GND']:continue
 if uid not in tb:raise RuntimeError('removed power copper '+uid)
 if geom(t)!=geom(tb[uid]):
  if isinstance(t,p.PCB_VIA):raise RuntimeError('old power/ground via moved')
  changed.append({'uuid':uid,'net':t.GetNetname(),'before_mm':[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)],'after_mm':[p.ToMM(tb[uid].GetStart().x),p.ToMM(tb[uid].GetStart().y),p.ToMM(tb[uid].GetEnd().x),p.ToMM(tb[uid].GetEnd().y)],'before_length_mm':p.ToMM(t.GetLength()),'after_length_mm':p.ToMM(tb[uid].GetLength()),'width_mm':p.ToMM(t.GetWidth())})
allowed={v['uuid'] for v in json.loads((D/'local_clearance_delta.json').read_text()) if 'terminal_recenter'in v}
if {x['uuid'] for x in changed}!=allowed:raise RuntimeError('unexpected power change')
# Preserve the physical C104 footprint and all its originally local copper, not just net identity.
f=fa['C104'];cx,cy=p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y);checked=[]
for uid,t in ta.items():
 if t.GetNetname() not in ['GND','3V3_AON']:continue
 x,y=p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y);z,w=p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)
 if min(math.hypot(x-cx,y-cy),math.hypot(z-cx,w-cy))<1.5:
  if geom(t)!=geom(tb[uid]):raise RuntimeError('C104 local power copper changed')
  checked.append(uid)
rows={'status':'LOCAL_GEOMETRY_EVIDENCE_NOT_LOOP_INDUCTANCE_QUALIFICATION','old_power_vias_and_trunks_preserved':True,'changed_terminal_branches':changed,'C104_local_unchanged_UUIDs':checked,'note':'These are decoupling terminal branches, not a justified total MCU rail current model; no fabricated DC current penalty.'};(D/'decoupling_delta.json').write_text(json.dumps(rows,indent=2))
# Native geometry comparison, deliberately labelled as a layer view, not a schematic.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1450" viewBox="0 0 1000 1450"><rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-size="18">Native F copper + through vias: RF baseline / integrated candidate</text>']
refs=['C103','C203','C201','C205','C104'];scale=52
for i,ref in enumerate(refs):
 center=fb[ref].GetPosition();cx,cy=p.ToMM(center.x),p.ToMM(center.y)
 for j,board in enumerate([a,b]):
  ox,oy=35+j*490,55+i*275;key=f'c{i}{j}';svg.append(f'<defs><clipPath id="{key}"><rect x="{ox}" y="{oy+20}" width="430" height="230"/></clipPath></defs><text x="{ox}" y="{oy+12}" font-size="15">{ref} — {"before" if j==0 else "after"}</text><rect x="{ox}" y="{oy+20}" width="430" height="230" fill="#fafafa" stroke="#aaa"/><g clip-path="url(#{key})">')
  def xy(v):return (ox+180+(p.ToMM(v.x)-cx)*scale,oy+135+(p.ToMM(v.y)-cy)*scale)
  def color(n):return '#16864c' if n=='GND' else '#d23535' if n=='3V3_AON' else '#9aa2aa'
  for t in board.GetTracks():
   if not isinstance(t,p.PCB_VIA) and t.GetLayer()!=p.F_Cu:continue
   x,y=xy(t.GetStart());z,w=xy(t.GetEnd());c=color(t.GetNetname())
   if isinstance(t,p.PCB_VIA):svg.append(f'<circle cx="{x}" cy="{y}" r="{p.ToMM(t.GetWidth(p.F_Cu))*scale/2}" fill="{c}"/><circle cx="{x}" cy="{y}" r="{p.ToMM(t.GetDrillValue())*scale/2}" fill="white"/>')
   else:svg.append(f'<line x1="{x}" y1="{y}" x2="{z}" y2="{w}" stroke="{c}" stroke-width="{p.ToMM(t.GetWidth())*scale}" stroke-linecap="round"/>')
  for f in board.GetFootprints():
   for pad in f.Pads():
    if not pad.IsOnLayer(p.F_Cu):continue
    q=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(q,p.F_Cu,0,1000,p.ERROR_OUTSIDE)
    for k in range(q.OutlineCount()):
     o=q.COutline(k);pts=' '.join(f'{xy(o.CPoint(n))[0]},{xy(o.CPoint(n))[1]}' for n in range(o.PointCount()));svg.append(f'<polygon points="{pts}" fill="{color(pad.GetNetname())}" opacity=".65"/>')
    if f.GetReference()==ref:
     x,y=xy(pad.GetPosition());svg.append(f'<text x="{x}" y="{y}" font-size="12">{pad.GetNumber()}</text>')
  svg.append('</g>')
svg.append('<text x="20" y="1440" font-size="14">Red=AON; green=GND; gray=other nets. Filled planes omitted from this comparison; verified separately.</text></svg>');(D/'decoupling_before_after.svg').write_text(''.join(svg));print('terminal branches',len(changed),'C104 local items',len(checked))
