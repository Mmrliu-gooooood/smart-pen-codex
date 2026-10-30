from pathlib import Path
import os,json,hashlib,shutil,sys
for k,v in [('XDG_CONFIG_HOME','/tmp/pen-native1950-config'),('XDG_CACHE_HOME','/tmp/pen-native1950-cache'),('XDG_DATA_HOME','/tmp/pen-native1950-data')]:os.environ[k]=v
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/dvp_rotated_group_placement_1835/native';M=R/'docs/electronics/dvp_joint_feasibility_1942';N=Path(sys.argv[2]).resolve() if len(sys.argv)==3 and sys.argv[1]=='--replay-dir' else D/'native'
replay=N!=D/'native'; saved=json.loads((D/'materialization.json').read_text()) if replay else None
if N.exists():raise RuntimeError('Refuse overwrite native output')
source=S/'mainboard_revD.kicad_pcb'
if hashlib.sha256(source.read_bytes()).hexdigest()!='7d197c4db87e936bd26fc9bb6052036aaf42c3a0e3e92032eac445e4909a6ff1':raise RuntimeError('INPUT HASH')
shutil.copytree(S,N,ignore=shutil.ignore_patterns('*.kicad_prl'))
b=p.LoadBoard(str(source));fs={f.GetReference():f for f in b.GetFootprints()};delta=json.loads((M/'placement_delta.json').read_text());g=json.loads((M/'result.json').read_text())['geometry']
V=lambda xy:p.VECTOR2I(*(round(v*1e6) for v in xy))
for ref,x in delta.items():
 f=fs[ref];a=x['after']
 if b.GetLayerName(f.GetLayer())!=a['layer']:f.Flip(f.GetPosition(),False)
 f.SetPosition(V(a['xy']));f.SetOrientationDegrees(a['angle'])
 if b.GetLayerName(f.GetLayer())!=a['layer']:raise RuntimeError('LAYER '+ref)
ids=[]
for i,x in enumerate(g):
 net=b.GetNetcodeFromNetname(x['net'])
 if net<=0:raise RuntimeError('UNKNOWN NET '+x['net'])
 if x['type']=='via':
  t=p.PCB_VIA(b);t.SetPosition(V(x['start']));t.SetWidth(p.F_Cu,450000);t.SetDrill(200000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(V(x['start']));t.SetEnd(V(x['end']));t.SetWidth(150000);t.SetLayer(b.GetLayerID(x['layer']))
 t.SetNetCode(net)
 b.Add(t);ids.append(t.m_Uuid.AsString())
b.BuildConnectivity();p.SaveBoard(str(N/'mainboard_revD.kicad_pcb'),b)
if replay:
 file=N/'mainboard_revD.kicad_pcb';text=file.read_text()
 for new,old in zip(ids,saved['added_uuids']):text=text.replace(new,old)
 file.write_text(text);reloaded=p.LoadBoard(str(file));p.SaveBoard(str(file),reloaded);ids=saved['added_uuids']
out={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'source_geometry_sha256':hashlib.sha256((M/'result.json').read_bytes()).hexdigest(),'changed_refs':sorted(delta),'added_objects':len(ids),'added_uuids':ids,'filled_planes':False,'status':'RESEARCH_ONLY_NOFAB_NOT_POWER_CONNECTED'}
if not replay:(D/'materialization.json').write_text(json.dumps(out,indent=2)+'\n')
if replay and out['output_sha256']!=saved['output_sha256']:raise RuntimeError('REPLAY SHA MISMATCH')
print(json.dumps(out,indent=2))
