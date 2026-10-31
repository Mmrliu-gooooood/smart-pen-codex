import reference_final as z
import json,hashlib,math
p=z.p;xy=lambda v:[v.x,v.y]
def sig(t):return[t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
for u,t in z.aa.items():
 if t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:assert u in z.bb and sig(t)==sig(z.bb[u])
a={f.GetReference():f for f in z.a.GetFootprints()};b={f.GetReference():f for f in z.b.GetFootprints()};assert set(a)==set(b)
for r,f in a.items():
 g=b[r];assert [xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),f.GetValue()]==[xy(g.GetPosition()),g.GetOrientationDegrees(),g.GetLayer(),g.GetValue()]
loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(z.pa[p.In2_Cu,'3V3_AON'],z.pb[p.In2_Cu,'3V3_AON']);gain=p.SHAPE_POLY_SET();gain.BooleanSubtract(z.pb[p.In2_Cu,'3V3_AON'],z.pa[p.In2_Cu,'3V3_AON'])
anchors={}
for xx,yy in [(9.575,42.2375),(9.575,52.0375)]:
 anchors[str((xx,yy))]=[{'pad':f.GetReference()+'.'+q.GetNumber(),'xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6]}for f in z.b.GetFootprints()for q in f.Pads()if q.GetNetname()=='3V3_AON'and math.dist((q.GetPosition().x/1e6,q.GetPosition().y/1e6),(xx,yy))<2.5]
r={'baseline_sha256':hashlib.sha256((z.D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'selected_sha256':hashlib.sha256((z.D/'selected_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'all_existing_power_copper_exact':True,'all_footprint_poses_values_exact':True,'In2_AON_loss_mm2':loss.Area()/1e12,'In2_AON_gain_mm2':gain.Area()/1e12,'current_AON_pads_near_checked_via_anchors':anchors};(z.D/'binding.json').write_text(json.dumps(r,indent=2));print(r)
