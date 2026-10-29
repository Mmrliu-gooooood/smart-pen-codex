from pathlib import Path
import pcbnew as p,json,xml.etree.ElementTree as E,hashlib,math
D=Path(__file__).resolve().parent;src=D.parent/'mainboard_revD/routing_trial/xclk5_review/mainboard_revD.kicad_pcb'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def comp(path):
 e=E.parse(path);cs={c.attrib['ref']:{'value':c.findtext('value'),'footprint':c.findtext('footprint') or '','dnp':c.find("property[@name='dnp']") is not None,'excluded':c.find("property[@name='exclude_from_bom']") is not None} for c in e.findall('./components/comp')};ns={(a.attrib['ref'],a.attrib['pin']):n.attrib['name'] for n in e.findall('./nets/net') for a in n};return cs,ns
oldc,oldn=comp(D/'baseline_source.xml');newc,newn=comp(D/'mainboard_revD.xml');require(oldn==newn and len(newn)==374,'source nodes changed');require(oldc.keys()==newc.keys(),'source components changed')
changes=[(r,k,oldc[r][k],newc[r][k]) for r in oldc for k in oldc[r] if oldc[r][k]!=newc[r][k]]
require(changes==[('R217','footprint','Resistor_SMD:R_0603_1608Metric','Resistor_SMD:R_0402_1005Metric')],'unexpected source changes '+repr(changes))
a=p.LoadBoard(str(src));b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
def copper(t):return [t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else 0]
old={t.m_Uuid.AsString():copper(t) for t in a.GetTracks()};new={t.m_Uuid.AsString():copper(t) for t in b.GetTracks()};removed=json.loads((D/'f11_213_seed_delta.json').read_text())['removed_isolated_CAM_D7'];exp=json.loads((D/'f11_213_expected_new.json').read_text());exp.update(json.loads((D/'bias4_ground_expected.json').read_text()))
require(set(old)-set(new)==set(removed),'unexpected missing copper');require(all(old[k]==new[k] for k in old.keys()&new.keys()),'retained copper changed');require(set(new)-set(old)==set(exp),'new copper set differs from literal contracts');require(all(new[k][1]==v for k,v in exp.items()),'literal expected-net mismatch');require(all(old[k][1]=='CAM_D7' for k in removed),'removed non-D7 copper')
oldfp={f.GetReference():f for f in a.GetFootprints()};newfp={f.GetReference():f for f in b.GetFootprints()};require(oldfp.keys()==newfp.keys() and len(newfp)==74,'footprint set changed');pads=0
for ref,f in newfp.items():
 require(f.GetValue()==newc[ref]['value'] and f.IsDNP()==newc[ref]['dnp'] and f.IsExcludedFromBOM()==newc[ref]['excluded'],ref+' property mismatch')
 require(str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())==newc[ref]['footprint'],ref+' FPID mismatch')
 require(f.GetPath().AsString()==oldfp[ref].GetPath().AsString(),ref+' source path mismatch')
 if ref!='R217':
  require((f.GetPosition(),f.GetOrientationDegrees(),f.GetLayer())==(oldfp[ref].GetPosition(),oldfp[ref].GetOrientationDegrees(),oldfp[ref].GetLayer()),ref+' placement changed')
 for pad in f.Pads():require(pad.GetNetname()==newn[ref,pad.GetNumber()],ref+' padnet mismatch');pads+=1
require(pads==269,'pad count')
newtracks=[t for t in b.GetTracks() if t.m_Uuid.AsString() in exp];length={};vias=[]
for t in newtracks:
 if isinstance(t,p.PCB_VIA):vias.append({'net':t.GetNetname(),'xy_mm':[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)],'diameter_mm':p.ToMM(t.GetWidth(p.F_Cu)),'drill_mm':p.ToMM(t.GetDrillValue())})
 else:
  key=t.GetNetname()+' '+b.GetLayerName(t.GetLayer());length[key]=length.get(key,0)+p.ToMM(t.GetLength())
r={'status':'NOFAB candidate; unchanged nets, R217 footprint-only source delta','baseline_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'source_delta':changes,'source_pin_endpoints':len(newn),'footprints':len(newfp),'padshapes':pads,'retained_unchanged_copper':len(old.keys()&new.keys()),'removed_isolated_D7':removed,'literal_new_copper':exp,'new_track_length_mm':length,'new_vias':vias};(D/'bias4_delta_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
