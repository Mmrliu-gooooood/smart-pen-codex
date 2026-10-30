from pathlib import Path
import os,sys,json,shutil,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/data1242previa'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
m=json.loads((D/'materialization.json').read_text());N=D/'reference_counterfactuals/ALL_NEW_SIGNAL_VIAS/native';shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));fillers=[p.ZONE_FILLER(b)];fillers[-1].Fill(b.Zones());p.SaveBoard(str(f),b)
if hashlib.sha256(f.read_bytes()).hexdigest()!=m['pcb_sha256']:raise RuntimeError('matched baseline exact')
remove={r['uuid']for r in m['mapping']if r['type']=='via'and r['net'].startswith('CAM_D')};ts=list(b.GetTracks())
for t in ts:
 if t.m_Uuid.AsString()in remove:b.Remove(t)
fillers.append(p.ZONE_FILLER(b));fillers[-1].Fill(b.Zones());p.SaveBoard(str(f),b);planes={}
for ref in [p.In1_Cu,p.In4_Cu]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetLayer()==ref:q.BooleanAdd(native_fractured_once(z.GetFilledPolysList(ref)))
 planes[ref]=q
rows=[]
for t in ts:
 if isinstance(t,p.PCB_VIA)or t.m_Uuid.AsString()not in m['added']:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;q=shape(t,t.GetLayer());q.BooleanSubtract(planes[ref]);rows.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'reference':b.GetLayerName(ref),'missing_pre_new_signal_vias_mm2':q.Area()/1e12})
if any(r['missing_pre_new_signal_vias_mm2']!=0 for r in rows):raise RuntimeError('nonzero pre-new-via inherited reference gap '+str([r for r in rows if r['missing_pre_new_signal_vias_mm2']]))
out={'candidate_sha256':m['pcb_sha256'],'matched_baseline_refill_byte_equal':True,'removed_new_signal_vias':sorted(remove),'all_new_tracks_pre_signal_via_reference_coverage_complete':True,'track_count':len(rows),'tracks':rows,'scope':'Matched-project explanatory counterfactual only. Proves no inherited dominant-GND gap on new paths before their nine signal-via holes; not SI, return-current or actual postfill zero-uncovered claim.'};(D/('pre_via_reference_optimized.json'if sys.flags.optimize else'pre_via_reference.json')).write_text(json.dumps(out,indent=2)+'\n');print('pre-via whole-track check passed')
