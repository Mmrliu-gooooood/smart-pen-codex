from pathlib import Path
import pcbnew as p,json,hashlib,math
D=Path(__file__).resolve().parents[1];fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));base=p.LoadBoard(str(D/'baseline_12mm.kicad_pcb'))
def geo(t):return {'type':t.GetClass(),'start_nm':[t.GetStart().x,t.GetStart().y],'end_nm':[t.GetEnd().x,t.GetEnd().y],'layer':b.GetLayerName(t.GetLayer()),'width_nm':t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),'drill_nm':t.GetDrillValue() if isinstance(t,p.PCB_VIA) else None}
def items(x):return {t.m_Uuid.AsString():geo(t) for t in x.GetTracks()}
a,c,old=items(b),items(core),items(base)
retained=set(a)&set(c);assert len(retained)==182 and all(a[k]==c[k] for k in retained)
summary={}
for t in b.GetTracks():
 n=t.GetNetname();r=summary.setdefault(n,{'total_track_length_mm':0,'added_vs_core_track_length_mm':0,'track_widths_mm':set(),'layers':set(),'vias':0})
 if isinstance(t,p.PCB_VIA):r['vias']+=1;continue
 length=math.hypot(t.GetEnd().x-t.GetStart().x,t.GetEnd().y-t.GetStart().y)/1e6;r['total_track_length_mm']+=length;r['added_vs_core_track_length_mm']+=length if t.m_Uuid.AsString() not in c else 0;r['track_widths_mm'].add(p.ToMM(t.GetWidth()));r['layers'].add(b.GetLayerName(t.GetLayer()))
for r in summary.values():r['track_widths_mm']=sorted(r['track_widths_mm']);r['layers']=sorted(r['layers'])
fpold={f.GetReference():f for f in base.GetFootprints()};moves=[]
for f in b.GetFootprints():
 o=fpold[f.GetReference()]
 if o.GetPosition()!=f.GetPosition() or o.GetOrientationDegrees()!=f.GetOrientationDegrees():moves.append({'ref':f.GetReference(),'before_mm_deg':[p.ToMM(o.GetPosition().x),p.ToMM(o.GetPosition().y),o.GetOrientationDegrees()],'after_mm_deg':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]})
r={'pcb_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'outline_mm':[14,45,.8],'comparison_baseline_mm':[12,45,.8],'width_delta_mm':2,'layers':4,'assembly':'double-sided','conditional_component_stack_mm':{'front_max_documented':1.6,'pcb_nominal':.8,'back_max_documented':1.45,'sum':3.85,'with_assumed_0p15mm_per_side_solder':4.15,'not_qualified':'MLCC height, wires, tolerances and shell/assembly clearance'},'core_retained_track_via':182,'core_removed_track_via':[{**c[k],'uuid':k} for k in sorted(set(c)-set(a))],'versus_12mm':{'removed_track_via':[{**old[k],'uuid':k} for k in sorted(set(old)-set(a))],'added_track_via':[{**a[k],'uuid':k} for k in sorted(set(a)-set(old))],'changed_track_via':[{ 'uuid':k,'before':old[k],'after':a[k]} for k in sorted(set(a)&set(old)) if a[k]!=old[k]],'footprint_moves':moves},'net_lengths':summary,'interpretation':'Lengths are sum of trace centerline XY lengths, not endpoint path length; exclude plane distribution and via barrel. Copper fill differs after refill; track/via preservation does not mean all copper unchanged.'}
(D/'layout_metrics.json').write_text(json.dumps(r,indent=2));print(json.dumps({n:v for n,v in summary.items() if n in ['VBUS_5V','CE_PERMISSION_INTERNAL','/thermal/CE_MID','/thermal/NTC_NODE','/core/PACK_NTC']},indent=2))
