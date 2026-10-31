import reference_final as z
import json,hashlib
p=z.p;xy=lambda v:[v.x,v.y]
def sig(t):return[t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
removed=[u for u in z.aa if u not in z.bb];changed=[u for u in z.aa if u in z.bb and sig(z.aa[u])!=sig(z.bb[u])];new=[t for u,t in z.bb.items()if u not in z.aa]
assert len(removed)==1 and z.aa[removed[0]].GetNetname()=='SENS_D6'and not changed
for u,t in z.aa.items():
 if t.GetNetname()in ['GND','3V3_AON']:assert u in z.bb and sig(t)==sig(z.bb[u])
assert not any(not isinstance(t,p.PCB_VIA)and t.GetLayer()==p.In2_Cu for t in new)
a={f.GetReference():f for f in z.a.GetFootprints()};b={f.GetReference():f for f in z.b.GetFootprints()};assert set(a)==set(b)
for r,f in a.items():
 g=b[r];assert [xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),f.GetValue()]==[xy(g.GetPosition()),g.GetOrientationDegrees(),g.GetLayer(),g.GetValue()]
r={'baseline_sha256':hashlib.sha256((z.D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'selected_sha256':hashlib.sha256((z.D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'removed_SENS_D6_UUID':removed,'changed_retained_copper_UUIDs':changed,'all_existing_AON_GND_copper_exact':True,'all_footprint_poses_values_exact':True,'no_new_In2_tracks':True,'new_object_counts':{n:{'tracks':sum(t.GetNetname()==n and not isinstance(t,p.PCB_VIA)for t in new),'vias':sum(t.GetNetname()==n and isinstance(t,p.PCB_VIA)for t in new)}for n in set(t.GetNetname()for t in new)}};(z.D/'binding.json').write_text(json.dumps(r,indent=2))
