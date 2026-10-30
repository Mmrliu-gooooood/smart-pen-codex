from pathlib import Path
import os,json,hashlib,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/pen-aon-negative';os.environ['XDG_CACHE_HOME']='/tmp/pen-aon-negative-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-aon-negative-data'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/power_zone_freshfill_candidate_2150';m=json.loads((D/'materialization.json').read_text());f=D/'native/mainboard_revD.kicad_pcb'
def req(a,t):
 if not a:raise RuntimeError(t)
def strip(f,remove=None):
 lines=f.read_text().splitlines(keepends=True);out=[];i=0
 while i<len(lines):
  if lines[i]=='\t(segment\n':
   z=[]
   while lines[i]!='\t)\n':z.append(lines[i]);i+=1
   z.append(lines[i])
   if not remove or remove not in ''.join(z):out+=z
  elif lines[i].startswith('\t\t(filled_polygon'):
   i+=1
   while lines[i]!='\t\t)\n':i+=1
  else:out.append(lines[i].replace('(fill yes\n','(fill\n'))
  i+=1
 return ''.join(out)
req(strip(f,m['added_uuid'])==strip(B/'native/mainboard_revD.kicad_pcb'),'OTHER NONFILL TEXT CHANGED')
a=json.loads((D/'analysis.json').read_text());old=json.loads((B/'analysis.json').read_text());req(a['signal_reference_projection']==old['signal_reference_projection'],'REFERENCE CHANGED');req(a['core_summary']==old['core_summary'],'PAD CORE COUNT CHANGED');req(a['foreign_via_antipad_checks']==old['foreign_via_antipad_checks'],'ANTIPAD CHANGED')
b=p.LoadBoard(str(f));bb=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'))
for z,z0 in zip(b.Zones(),bb.Zones()):
 req(z.m_Uuid.AsString()==z0.m_Uuid.AsString(),'ZONE ORDER')
 if z.GetIsRuleArea():continue
 for l in z.GetLayerSet().Seq():req(z.GetFilledPolysList(l).Format()==z0.GetFilledPolysList(l).Format(),'FILLED GEOMETRY CHANGED')
# Actual native deletion negative, isolated /tmp copy. No copper restore/rerouting.
N=Path('/tmp/pen-aon-entry-negative2156');shutil.copytree(D/'native',N,dirs_exist_ok=True);nf=N/f.name;lines=nf.read_text().splitlines(keepends=True);out=[];i=0;removed=0
while i<len(lines):
 if lines[i]=='\t(segment\n':
  z=[]
  while lines[i]!='\t)\n':z.append(lines[i]);i+=1
  z.append(lines[i])
  if m['added_uuid']in ''.join(z):removed+=1
  else:out+=z
 else:out.append(lines[i])
 i+=1
req(removed==1,'NEGATIVE DELETE');nf.write_text(''.join(out));nb=p.LoadBoard(str(nf));p.ZONE_FILLER(nb).Fill(nb.Zones());p.SaveBoard(str(nf),nb)
req(nf.read_bytes()==(B/'native/mainboard_revD.kicad_pcb').read_bytes(),'NEGATIVE DID NOT RECREATE FROZEN BASE')
cmd=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'negative_drc.json'),str(nf)]
r=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(D/'negative_drc.log').write_text(r.stdout);j=json.loads((D/'negative_drc.json').read_text());counts=[len(j[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[2,232,0]and r.returncode==5,'NEGATIVE CLI')
req(hashlib.sha256(f.read_bytes()).hexdigest()==m['pcb_sha'],'CANDIDATE MUTATED');req((D/'analysis.json').read_bytes()==(D/'analysis_optimized.json').read_bytes(),'NORMAL-O')
print(json.dumps(dict(nonfill_native_except_single_added_segment_exact=True,all_filled_polygon_geometry_exact_base=True,all_padcore_memberships_unchanged=True,reference_projections_unchanged=True,all_antipads_unchanged=True,negative_recreated_base_sha=hashlib.sha256(nf.read_bytes()).hexdigest(),negative_full_drc=counts,negative_exit=r.returncode,candidate_unchanged=True,normal_optimized_identical=True),indent=2))
