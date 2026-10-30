import geometry as g,json
p=g.p
oldboard=p.LoadBoard(str(g.R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
nets=['AON_I2C_SCL','AON_I2C_SDA','PICKUP_INT_N']
new=[t for t in oldboard.GetTracks() if t.GetNetname()in nets]
r={'old_objects':len(new),'layers':{},'pads':[],'errors':g.errors(new)}
for n in nets:r['layers'][n]={oldboard.GetLayerName(l):sum(1 for t in new if t.GetNetname()==n and t.IsOnLayer(l))for l in g.L}
for q in g.pads:
 if q.GetNetname()in nets or g.desc(q).startswith(('R501.','R502.')):r['pads'].append({'ref':g.desc(q),'value':q.GetParentFootprint().GetValue(),'net':q.GetNetname(),'xy':g.xy(q),'layers':[g.b.GetLayerName(l)for l in g.L if q.IsOnLayer(l)]})
open(__file__.replace('inspect_old.py','old_geometry_audit.json'),'w').write(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
