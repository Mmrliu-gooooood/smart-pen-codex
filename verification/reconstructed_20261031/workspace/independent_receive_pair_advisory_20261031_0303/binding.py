from pathlib import Path
import os
os.environ["XDG_CONFIG_HOME"]="/tmp/receive_advisory_config"
import pcbnew as p,json,hashlib,math,sys
D=Path(__file__).resolve().parent;sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();a=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'selected_candidate/mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));uid=lambda t:t.m_Uuid.AsString();xy=lambda x:[x.x/1e6,x.y/1e6]
def sig(t):return[t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
aa={uid(t):t for t in a.GetTracks()};bb={uid(t):t for t in b.GetTracks()};ba={uid(t):t for t in base.GetTracks()};assert set(aa)==set(bb);changes=[{'uuid':u,'before':sig(t),'after':sig(bb[u])}for u,t in aa.items()if sig(t)!=sig(bb[u])];assert len(changes)==6;assert all(r['before'][0]in['CAM_PCLK','CAM_HREF']for r in changes)
for r in ['C104']:
 fa=next(f for f in base.GetFootprints()if f.GetReference()==r);fb=next(f for f in b.GetFootprints()if f.GetReference()==r);assert fa.GetPosition()==fb.GetPosition()and fa.GetOrientationDegrees()==fb.GetOrientationDegrees()
feed=['11d26ef2-133b-41cb-8242-f0750c446f96','4b070c1d-13f5-48c3-a7dc-442af935bad8','6938faac-6324-49cf-90da-fc988559d16b'];assert all(sig(ba[u])==sig(bb[u])for u in feed);assert sum(bb[u].GetLength()for u in feed)==2550000
rows={}
for name,B in [('baseline',base),('selected',b)]:
 cap=next(q for f in B.GetFootprints()if f.GetReference()=='C104'for q in f.Pads()if q.GetNumber()=='2');pos=cap.GetPosition();ts=[t for t in B.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and(t.GetStart()==pos or t.GetEnd()==pos)];rows[name]={'cap_pad_mm':xy(pos),'incident_GND_tracks':[sig(t)for t in ts],'incident_length_mm':sum(t.GetLength()/1e6 for t in ts)}
r={'baseline_sha256':sha(D/'native/mainboard_revD.kicad_pcb'),'diagnostic_sha256':sha(D/'final_candidate/mainboard_revD.kicad_pcb'),'selected_sha256':sha(D/'selected_candidate/mainboard_revD.kicad_pcb'),'six_changed_objects_only':changes,'C104_direct_AON_feed_unchanged_mm':2.55,'C104_GND':rows};(D/'binding.json').write_text(json.dumps(r,indent=2))
