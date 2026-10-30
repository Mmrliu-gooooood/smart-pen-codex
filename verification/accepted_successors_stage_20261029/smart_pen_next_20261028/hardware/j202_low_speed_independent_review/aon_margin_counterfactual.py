from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
from copper_geometry import build,components,shape
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));newids=set(json.loads((D/'geometry_delta.json').read_text())['added']);before=build(b);beforec=components(before['3V3_AON']);cut=p.SHAPE_POLY_SET();ids=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in newids:
  q=shape(t,p.In2_Cu);q.Inflate(325000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,250,True);cut.BooleanAdd(q);ids.append(t.m_Uuid.AsString())
lost=0
for z in b.Zones():
 if z.GetIsRuleArea()or not z.IsOnLayer(p.In2_Cu)or z.GetNetname()!='3V3_AON':continue
 old=z.GetFilledPolysList(p.In2_Cu);new=p.SHAPE_POLY_SET();new.BooleanSubtract(old,cut);lost+=old.Area()-new.Area();z.SetFilledPolysList(p.In2_Cu,new)
after=build(b);afterc=components(after['3V3_AON']);split=[g for g in beforec if not any(set(g)<=set(v)for v in afterc)];out={'status':'COUNTERFACTUAL_REMOVAL_ONLY_NOT_FABRICATED','extra_disc_inflation_from_via_annulus_mm':.325,'affected_vias':ids,'additional_AON_area_removed_mm2':lost/1e12,'before_AON_pad_components':beforec,'after_AON_pad_components':afterc,'old_pad_group_splits':split,'note':'Only In2 AON fill removed in discs around every new signal/VIO via: annulus radius + .325mm. Existing tracks/pads/vias unchanged. Preserved pad connectivity screens reliance on thin local plane margins, not current density/thermal margin or all-plane erosion.'};(D/'aon_margin_counterfactual.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if split:raise RuntimeError('COUNTERFACTUAL_AON_SPLIT')
