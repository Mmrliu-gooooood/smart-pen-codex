import os,sys,json
from pathlib import Path
os.environ.update(XDG_CONFIG_HOME='/tmp/c207review/config',XDG_CACHE_HOME='/tmp/c207review/cache',XDG_DATA_HOME='/tmp/c207review/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import build,components,shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'final_faf2912.kicad_pcb'));a=p.LoadBoard(str(D/'baseline8312.kicad_pcb'));graph={n:components(v)for n,v in build(b).items()};cores={net:next(c for c in graph[net]if anchor in c)for net,anchor in [('GND','J106.3'),('3V3_AON','J106.2')]}
def req(c,m):
 if not c:raise RuntimeError(m)
req({'C207.2','U204.4'}<=set(cores['GND']),'ground core');req({'C207.1','U204.8','C301.1','U301.1'}<=set(cores['3V3_AON']),'AO core')
planes={}
for board,label in[(a,'old'),(b,'new')]:
 q=p.SHAPE_POLY_SET()
 for z in board.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()=='3V3_AON'and z.GetLayer()==p.In2_Cu:q.BooleanAdd(native_fractured_once(z.GetFilledPolysList(p.In2_Cu)))
 planes[label]=q
V=lambda x:p.VECTOR2I(round(x[0]*1e6),round(x[1]*1e6));via=V((12.05,64.875));corept=V((11.0,64.875));islands=[i for i in range(planes['new'].OutlineCount())if planes['new'].UnitSet(i).Contains(via)and planes['new'].UnitSet(i).Contains(corept)];req(bool(islands),'localAOpatch continuity')
rows=[]
for width in [.3,.5]:
 t=p.PCB_TRACK(b);t.SetStart(corept);t.SetEnd(via);t.SetLayer(p.In2_Cu);t.SetWidth(round(width*1e6));q=shape(t,p.In2_Cu);q.BooleanSubtract(planes['new']);rows.append({'corridor_width_mm':width,'area_outside_AON_mm2':q.Area()/1e12})
info={'GND_AON_core_sizes':[len(cores['GND']),len(cores['3V3_AON'])],'local_pin_connectivity_checked':['C207.2','U204.4','C207.1','U204.8','C301.1','U301.1'],'AON_local_stitch_and_old_core_same_filled_islands':islands,'AON_patch_corridors_from_11_64p875_to_12p05_64p875':rows,'interpretation':'NewGNDvia antipad does not sever this sampled localAO connection. Widths descriptive CAD evidence, not current-density/thermal/inductance qualification.'}
(D/'final_local_check.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
