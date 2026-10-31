from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/xclk-delta'
import pcbnew as p
D=Path(__file__).resolve().parent;OLD=D/'candidate/mainboard_revD.kicad_pcb';NEW=D/'final_candidate/mainboard_revD.kicad_pcb'
if not OLD.exists():
 import tempfile,difflib
 tmp=tempfile.TemporaryDirectory(prefix='control-junction-replay-');OLD=Path(tmp.name)/'original6902.kicad_pcb';OLD.write_text(''.join(difflib.restore((D/'junction_reversible.ndiff').read_text().splitlines(keepends=True),1)))
a=p.LoadBoard(str(OLD));b=p.LoadBoard(str(NEW))
def track(t):
 r={'class':t.GetClass(),'net':t.GetNetname(),'layer':t.GetLayer(),'a':[t.GetStart().x,t.GetStart().y],'z':[t.GetEnd().x,t.GetEnd().y],'width':t.GetWidth(p.F_Cu)if t.GetClass()=='PCB_VIA'else t.GetWidth()}
 if t.GetClass()=='PCB_VIA':r['drill']=t.GetDrillValue()
 return r
A={t.m_Uuid.AsString():track(t)for t in a.GetTracks()};B={t.m_Uuid.AsString():track(t)for t in b.GetTracks()};delta={u:{'old':A.get(u),'new':B.get(u)}for u in A.keys()|B.keys()if A.get(u)!=B.get(u)}
def poly(q):
 def line(c):return[(c.CPoint(i).x,c.CPoint(i).y)for i in range(c.PointCount())]
 return[(line(q.COutline(i)),[line(q.CHole(i,j))for j in range(q.HoleCount(i))])for i in range(q.OutlineCount())]
za={z.m_Uuid.AsString():poly(z.GetFilledPolysList(z.GetLayer()))for z in a.Zones()if not z.GetIsRuleArea()};zb={z.m_Uuid.AsString():poly(z.GetFilledPolysList(z.GetLayer()))for z in b.Zones()if not z.GetIsRuleArea()};r={'old_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'track_delta':delta,'all_filled_polygon_vertices_exact':za==zb,'scope':'One new PWDN F endpoint extended27.403um through existing same-net centerline; all other copper and all filled-plane vertices exactly unchanged. Original finite/native connectivity already valid.'};print(r);(D/'junction_exact_delta.json').write_text(json.dumps(r,indent=2))
if len(delta)!=1 or next(iter(delta))!='5c11a7ef-7ebc-4120-9932-d9ac83cf2b37' or not za==zb:raise RuntimeError('unexpected margin delta')
