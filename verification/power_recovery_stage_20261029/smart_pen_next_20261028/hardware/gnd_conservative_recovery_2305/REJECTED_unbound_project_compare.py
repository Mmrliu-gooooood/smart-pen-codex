from pathlib import Path
import os,json,tempfile
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gnd-recovery2305'
import pcbnew as p
D=Path(__file__).resolve().parent; S=D.parent/'gnd_fixed_branch_candidate_2159'; f=S/'native/mainboard_revD.kicad_pcb';src=f.read_text();plan=json.loads((S/'plan.json').read_text())
def remove(src,ids):
 lines=src.splitlines(keepends=True);out=[];i=0;n=0
 while i<len(lines):
  if lines[i]in['\t(segment\n','\t(via\n','\t(arc\n']:
   z=[]
   while lines[i]!='\t)\n':z.append(lines[i]);i+=1
   z.append(lines[i]);s=''.join(z)
   if any(u in s for u in ids):n+=1
   else:out+=z
  else:out.append(lines[i])
  i+=1
 if n!=len(ids):raise RuntimeError('remove count')
 return ''.join(out)
def stats(b):
 z=next(z for z in b.Zones()if z.GetNetname()=='3V3_AON');q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In2_Cu));area=q.Area()/1e12;q.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 return dict(area_mm2=area,eroded_pieces=q.OutlineCount(),eroded_area_mm2=q.Area()/1e12)
rows=[]
for g in plan['components']:
 if not g['accepted_preflight']:continue
 t=Path('/tmp/pen-gnd-remove2305.kicad_pcb');t.write_text(remove(src,set(g['objects'])));b=p.LoadBoard(str(t));p.ZONE_FILLER(b).Fill(b.Zones());r=dict(removed_group=g['id'],pads=g['pads'],objects=len(g['objects']),**stats(b));rows.append(r)
print(json.dumps(rows,indent=2))
