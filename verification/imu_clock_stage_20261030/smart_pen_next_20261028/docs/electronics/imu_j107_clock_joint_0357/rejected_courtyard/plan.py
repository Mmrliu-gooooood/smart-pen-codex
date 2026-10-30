from pathlib import Path
import sys,contextlib,io,json
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R/'docs/electronics/imu_access_corridor_0345'))
with contextlib.redirect_stdout(io.StringIO()):import explore as z
q=z.g;p=q.p;z.fps['J107'].SetPosition(q.V((5.2,84)))
removed=next(t for t in q.old if q.desc(t)=='2010858e-8edf-52c4-a3a5-f423a79bbfc8');q.old.remove(removed)
# OLD geometry remains on board; filtered finite checking only. No native changes/save.
N='SENS_EXTCLK';new=list(z.items)
def sv(a):
 v=q.via(N,a);v.SetWidth(p.F_Cu,450000);v.SetDrill(200000);return v
new += [q.track(N,p.B_Cu,(4.25,78.6),(4.25,79.2),.15),sv((4.25,79.2)),q.track(N,p.In3_Cu,(4.25,79.2),(4.25,89.4),.15),sv((4.25,89.4)),q.track(N,p.B_Cu,(4.25,89.4),(4.25,90.5),.15)]
if __name__=='__main__':print(json.dumps(q.errors(new),indent=2))
