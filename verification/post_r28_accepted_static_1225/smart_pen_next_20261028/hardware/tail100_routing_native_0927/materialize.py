from pathlib import Path
import os,json,hashlib,shutil,uuid
os.environ.update(XDG_CONFIG_HOME='/tmp/tail0927/config',XDG_CACHE_HOME='/tmp/tail0927/cache',XDG_DATA_HOME='/tmp/tail0927/data')
import pcbnew as p
D=Path(__file__).resolve().parent;BASE=D.parent/'ground_local_native_0920/native';N=Path(os.environ.get('TAIL_NATIVE_OUTPUT',str(D/'native')));M=D/'selected_final.json';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
req(sha(BASE/'mainboard_revD.kicad_pcb')=='ff70d9171b364e2d89ce13d109f22a2362afe76c340d384e194fb541bed6af8a','accepted R218 exact parent');req(sha(M)=='942ffd23066793b2172a65dfda1e3cf1e66465366604ff1e8ff40b965a222ac0','pinned geometry model');m=json.loads(M.read_text());shutil.copytree(BASE,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));ts={t.m_Uuid.AsString():t for t in b.GetTracks()};V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))
def apply(t,r):
 if r['type']=='via':t.SetPosition(V(r['a']));t.SetWidth(p.F_Cu,round(r['width']*1e6));t.SetDrill(round(r['drill']*1e6))
 else:t.SetStart(V(r['a']));t.SetEnd(V(r['b']));t.SetWidth(round(r['width']*1e6));t.SetLayer(b.GetLayerID(r['layer']))
for r in m['changed']:apply(ts[r['uuid']],r['after'])
added=[];remap={}
for r in m['added']:
 req(r['type']=='track','only new tracks');t=p.PCB_TRACK(b);t.SetNetCode(b.GetNetcodeFromNetname(r['net']));apply(t,r);u=str(uuid.uuid5(uuid.NAMESPACE_URL,'tail1000927/'+json.dumps(r,sort_keys=True)));remap[t.m_Uuid.AsString()]=u;b.Add(t);added.append(u)
fj=next(fj for fj in b.GetFootprints()if fj.GetReference()=='J202');fj.SetPosition(V(m['J202']['after']));edge=[]
for s in b.GetDrawings():
 if s.GetLayer()==p.Edge_Cuts:
  changed=False
  for get,setter in [('GetStart','SetStart'),('GetEnd','SetEnd')]:
   v=getattr(s,get)()
   if v.y==95000000:getattr(s,setter)(p.VECTOR2I(v.x,93300000));changed=True
  if changed:edge.append(s.m_Uuid.AsString())
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);text=f.read_text()
for old,new in remap.items():text=text.replace(old,new)
f.write_text(text);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);raw=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(raw==f.read_bytes(),'stable refill')
(N.parent/'materialization.json').write_text(json.dumps({'base_sha256':sha(BASE/'mainboard_revD.kicad_pcb'),'pcb_sha256':sha(f),'model_sha256':sha(M),'changed':[r['uuid']for r in m['changed']],'removed':[],'added':sorted(added),'edge_changed':edge,'J202_translation_mm':[0,-1.7],'refill_byte_stable':True,'status':'NOFAB_NOPOWER_PENDING_INDEPENDENT_REVIEW'},indent=2)+'\n');print(sha(f),len(m['changed']),len(added))
