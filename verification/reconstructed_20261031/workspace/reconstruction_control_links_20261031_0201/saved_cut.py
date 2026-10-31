from pathlib import Path
import os,sys,shutil,json,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;i=int(sys.argv[1]);n=['CAM_SCL','CAM_SDA'][i];out=D/('saved_cut_'+str(i));shutil.copytree(D/'final_candidate',out);b=p.LoadBoard(str(out/'mainboard_revD.kicad_pcb'));fps=list(b.GetFootprints());f=next(f for f in fps if f.GetReference()=='U101');pads=list(f.Pads());q=next(q for q in pads if q.GetNumber()==str(44+i));tracks=list(b.GetTracks());ts=[t for t in tracks if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)and(t.GetStart()==q.GetPosition()or t.GetEnd()==q.GetPosition())]
if len(ts)!=1:raise RuntimeError(len(ts))
u=ts[0].m_Uuid.AsString();b.Remove(ts[0]);p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'mainboard_revD.kicad_pcb'),b);(D/'final_validation'/('saved_cut_'+str(i)+'.json')).write_text(json.dumps({'net':n,'cut_uuid':u,'scope':'Diagnostic only; not release candidate; final untouched.'},indent=2))
