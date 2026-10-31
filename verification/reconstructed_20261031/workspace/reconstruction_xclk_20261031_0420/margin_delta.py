from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/xclk-delta'
import pcbnew as p
D=Path(__file__).resolve().parent;OLD=D/'clean_candidate/mainboard_revD.kicad_pcb';OLD=OLD if OLD.exists()else D.parent/'independent_xclk_advisory_20261031_0443/final_candidate/mainboard_revD.kicad_pcb';NEW=D/'final_candidate/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(OLD));b=p.LoadBoard(str(NEW))
def track(t):
 r={'class':t.GetClass(),'net':t.GetNetname(),'layer':t.GetLayer(),'a':[t.GetStart().x,t.GetStart().y],'z':[t.GetEnd().x,t.GetEnd().y],'width':t.GetWidth(p.F_Cu)if t.GetClass()=='PCB_VIA'else t.GetWidth()}
 if t.GetClass()=='PCB_VIA':r['drill']=t.GetDrillValue()
 return r
A={t.m_Uuid.AsString():track(t)for t in a.GetTracks()};B={t.m_Uuid.AsString():track(t)for t in b.GetTracks()};delta={u:{'old':A.get(u),'new':B.get(u)}for u in A.keys()|B.keys()if A.get(u)!=B.get(u)}
def poly(q):
 def line(c):return[(c.CPoint(i).x,c.CPoint(i).y)for i in range(c.PointCount())]
 return[(line(q.COutline(i)),[line(q.CHole(i,j))for j in range(q.HoleCount(i))])for i in range(q.OutlineCount())]
za={z.m_Uuid.AsString():poly(z.GetFilledPolysList(z.GetLayer()))for z in a.Zones()if not z.GetIsRuleArea()};zb={z.m_Uuid.AsString():poly(z.GetFilledPolysList(z.GetLayer()))for z in b.Zones()if not z.GetIsRuleArea()};r={'old_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'track_delta':delta,'all_filled_polygon_vertices_exact':za==zb,'scope':'Three new XCLK F track endpoints shifted north40um, all other copper and filled plane vertices unchanged; nominal full U101 budget gap .025→.065mm, not manufacturing margin.'};print(r);(D/'margin_delta.json').write_text(json.dumps(r,indent=2))
if len(delta)!=6 or sum(v['old']is None for v in delta.values())!=3 or sum(v['new']is None for v in delta.values())!=3 or not za==zb:raise RuntimeError('unexpected margin delta')
