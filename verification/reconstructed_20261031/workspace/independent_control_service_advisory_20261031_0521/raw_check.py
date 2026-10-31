import reference_final as z
import native_blocks as n,json,hashlib,re
A=(z.D/'native/mainboard_revD.kicad_pcb').read_text();B=(z.D/'candidate/mainboard_revD.kicad_pcb').read_text()
def indexed(s):
 return {m.group(1):v for _,_,v in n.blocks(s)if (m:=re.search(r'\(uuid "([^"\n]+)"\)',v))}
a,b=indexed(A),indexed(B);missing=set(a)-set(b);changed=[u for u in a.keys()&b.keys()if a[u]!=b[u]]
if missing:raise RuntimeError(missing)
if any(not a[u].startswith('(zone')for u in changed):raise RuntimeError(changed)
rows=[]
for u,t in z.bb.items():
 if u not in z.aa and t.GetClass()!='PCB_VIA'and t.GetLayer()==z.p.In2_Cu:rows.append({'net':t.GetNetname(),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'length_mm':t.GetLength()/1e6})
(z.D/'raw_check.json').write_text(json.dumps({'candidate_sha256':hashlib.sha256(B.encode()).hexdigest(),'baseline_sha256':hashlib.sha256(A.encode()).hexdigest(),'missing_uuid_blocks':sorted(missing),'changed_blocks':changed,'all_old_nonzone_uuid_blocks_exact':True,'new_tracks':sum(t.GetClass()!='PCB_VIA'for u,t in z.bb.items()if u not in z.aa),'new_vias':sum(t.GetClass()=='PCB_VIA'for u,t in z.bb.items()if u not in z.aa),'In2_new_tracks':rows,'In2_total_length_mm':sum(r['length_mm']for r in rows)},indent=2))
