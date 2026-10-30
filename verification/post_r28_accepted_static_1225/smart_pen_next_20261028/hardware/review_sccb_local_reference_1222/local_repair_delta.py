from pathlib import Path
import os,json,sys,hashlib,collections
os.environ['XDG_CONFIG_HOME']='/tmp/sccb1216delta'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from native_polygon import native_fractured_once
A=D.parent/'sccb_bypass_native_1131/native/mainboard_revD.kicad_pcb';B=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(A));b=p.LoadBoard(str(B))
def req(c,s):
 if not c:raise RuntimeError(s)
def sig(t):
 xy=lambda v:(v.x,v.y)
 return(t.GetNetname(),t.GetClass(),t.GetLayerSet().FmtHex(),tuple(sorted([xy(t.GetStart()),xy(t.GetEnd())])),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
aa=collections.Counter(sig(t)for t in a.GetTracks());bb=collections.Counter(sig(t)for t in b.GetTracks());removed=list((aa-bb).elements());added=list((bb-aa).elements());req(len(removed)==2 and len(added)==4,'exact two-segment local repair');req(all(r[1]=='PCB_TRACK'for r in removed+added),'no via edit');req(collections.Counter(r[0]for r in removed)=={'CAM_SDA':1,'3V3_AON':1},'bounded two nets')
az={z.m_Uuid.AsString():z for z in a.Zones()};bz={z.m_Uuid.AsString():z for z in b.Zones()};req(set(az)==set(bz),'same zones');deltas=[]
for u,z in az.items():
 if z.GetIsRuleArea():continue
 l=z.GetLayer();x=native_fractured_once(z.GetFilledPolysList(l));y=native_fractured_once(bz[u].GetFilledPolysList(l));loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(x,y);gain=p.SHAPE_POLY_SET();gain.BooleanSubtract(y,x);req(loss.Area()==0 and gain.Area()==0,'all filled reference geometry identical');deltas.append({'zone':u,'layer':b.GetLayerName(l),'loss_mm2':loss.Area()/1e12,'gain_mm2':gain.Area()/1e12})
print(json.dumps({'diagnostic_parent_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'removed_geometry':removed,'added_geometry':added,'all_via_geometry_unchanged':True,'all_filled_zone_geometry_identical':deltas,'scope':'Two local segment repairs only relative to1131; full source/moved footprints checked separately against accepted8312; no adoption of1131 source-reference gate'},indent=2))
