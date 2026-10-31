from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(D));import geometry_native as g
p=g.p;g.b=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));g.MASK_OVERRIDE=D/'proposed_obstacles.json';oldpos=(6.625,41.875);newpos=(6.875,41.975);removed=[];fleads=[]
for t in g.b.GetTracks():
 if t.GetNetname()!='CAM_PCLK':continue
 if isinstance(t,p.PCB_VIA):
  if t.GetPosition()==g.V(oldpos):removed.append(t)
 else:
  a,z=t.GetStart(),t.GetEnd()
  if t.GetLayer()==p.B_Cu and min(a.x,z.x)>=5975000 and min(a.y,z.y)>=40700000 and max(a.y,z.y)<=42000000:removed.append(t)
  elif t.GetLayer()==p.F_Cu and(a==g.V(oldpos)or z==g.V(oldpos)):removed.append(t);fleads.append((a,z))
u={t.m_Uuid.AsString()for t in removed};g.old=[t for t in g.b.GetTracks()if t.m_Uuid.AsString()not in u];g.pads=[q for f in g.b.GetFootprints()for q in f.Pads()];new=[];spec=[]
def chain(n,l,pts):
 for a,z in zip(pts,pts[1:]):
  t=g.track(n,l,a,z,.15);new.append(t);spec.append({'uuid':t.m_Uuid.AsString(),'net':n,'layer':g.b.GetLayerName(l),'a':a,'z':z})
def via(n,xy):
 t=g.via(n,xy);t.SetWidth(p.F_Cu,450000);t.SetDrill(200000);new.append(t);spec.append({'uuid':t.m_Uuid.AsString(),'net':n,'via':xy})
chain('CAM_PCLK',p.B_Cu,[(5.975,40.775),(6.05,40.85),(6.05,41.975),newpos]);via('CAM_PCLK',newpos)
for a,z in fleads:
 q=z if a==g.V(oldpos)else a;chain('CAM_PCLK',p.F_Cu,[newpos,(q.x/1e6,q.y/1e6)])
chain('CAM_VSYNC',p.B_Cu,[(5.375,39.5),(4.55,39.5),(4.55,40.35),(6.0,40.45),(6.675,41.4)]);via('CAM_VSYNC',(6.675,41.4));chain('CAM_VSYNC',p.F_Cu,[(5.675,43.1375),(5.675,41.65),(6.675,41.4)])
e=g.errors(new);r={'status':'REJECTED_JOINT_PREFLIGHT'if e else'PREFLIGHT_ONLY_NOT_ADOPTED','selected_source':'5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433','removed_PCLK_objects':[t.m_Uuid.AsString()for t in removed],'new':spec,'errors':e,'scope':'One bounded PCLK B dogleg/via/F-attachment replacement and short VSYNC B/F gateway proposal, no poses/power copper/USB changes. In-memory feasibility only, no native board saved. Existing same-net VSYNC tree retained for collision checking; a feasible proposal would still require deleting obsolete branches and full physical/refill/reference review. Failure is specific to these coordinates and current copper, not global impossibility.'};(D/'local_junction_prefilter/results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
