from pathlib import Path
import os,json,hashlib,argparse,math
os.environ['XDG_CONFIG_HOME']='/tmp/tail-final0933';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;parser=argparse.ArgumentParser();parser.add_argument('--board',required=True,type=Path);a=parser.parse_args();q=a.board.resolve();base=W/'assembly_clearance_candidate_20261030_0921/tail100/native_placement_ONLY_NOFAB/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(q));old=p.LoadBoard(str(base))
def fp(f):
 return {'ref':f.GetReference(),'value':f.GetValue(),'lib':f.GetFPIDAsString(),'pose':[f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayerName()],'dnp':f.IsDNP(),'pads':sorted([{'n':z.GetNumber(),'xy':[z.GetPosition().x,z.GetPosition().y],'size':[z.GetSize().x,z.GetSize().y],'angle':z.GetOrientationDegrees(),'layers':str(z.GetLayerSet().FmtHex()),'net':z.GetNetname(),'shape':int(z.GetShape())}for z in f.Pads()],key=lambda z:(z['n'],z['xy']))}
rows={f.GetReference():fp(f)for f in b.GetFootprints()};before={f.GetReference():fp(f)for f in old.GetFootprints()};changes=[r for r in set(rows)|set(before)if rows.get(r)!=before.get(r)]
if changes:raise RuntimeError('installation-native contract changed: '+str(changes))
edges=[]
for z in b.GetDrawings():
 if z.GetLayerName()=='Edge.Cuts':
  if z.GetShapeStr()!='Line':raise RuntimeError('nonlinear edge needs explicit bound')
  edges.extend([(z.GetStart().x/1e6,z.GetStart().y/1e6),(z.GetEnd().x/1e6,z.GetEnd().y/1e6)])
bounds=[min(x for x,y in edges),min(y for x,y in edges),max(x for x,y in edges),max(y for x,y in edges)]
if bounds!=[0,-6.5,14,93.3]:raise RuntimeError('unexpected outline')
ledger=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];vias=[]
oldvias={(t.GetPosition().x,t.GetPosition().y,t.GetWidth(),t.GetDrillValue(),t.GetNetname())for t in old.GetTracks()if isinstance(t,p.PCB_VIA)}
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):continue
 ident=(t.GetPosition().x,t.GetPosition().y,t.GetWidth(),t.GetDrillValue(),t.GetNetname())
 if ident in oldvias:continue
 x,y=t.GetPosition().x/1e6,t.GetPosition().y/1e6;rad=t.GetWidth()/2e6;near=[]
 for r in ledger:
  for e in r['contexts'][0]['entities']:
   bb=list(e['projected_current_bounds_not_final_assembly'])
   if r['ref']=='J202':bb[2]+=1.7;bb[5]+=1.7
   dx=max(bb[0]-(x-7),0,(x-7)-bb[3]);dz=max(bb[2]-(127-y),0,(127-y)-bb[5]);gap=math.hypot(dx,dz)-rad
   if gap<.5:near.append({'entity':e['label'],'side':r['current_pose'][3],'signed_projection_gap_mm':gap})
 vias.append({'net':t.GetNetname(),'xy':[x,y],'diameter':rad*2,'drill':t.GetDrillValue()/1e6,'near_projection':near})
j202=next(f for f in b.GetFootprints()if f.GetReference()=='J202');j202.BuildCourtyardCaches()
courtyard={'native_graphics':[{'shape':g.GetShapeStr(),'start':[g.GetStart().x/1e6,g.GetStart().y/1e6],'end':[g.GetEnd().x/1e6,g.GetEnd().y/1e6]}for g in j202.GraphicalItems()if g.GetLayer()==p.B_CrtYd],'cache_area_mm2':j202.GetCourtyard(p.B_Cu).Area()/1e12,'correction':'Native courtyard exists. Prior no accepted courtyard wording does not mean absence; process qualification is still absent.'}
result={'J202_courtyard':courtyard,'board':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'baseline_placement_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'all103_full_fp_pad_contract_equal':not changes,'outline_bounds':bounds,'size':[bounds[2]-bounds[0],bounds[3]-bounds[1]],'new_or_moved_vias':vias,'scope':'projection gaps of full installation budgets, not proof via protrusion/collision or tenting/connector seating qualification'};(O/'native_contract.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
