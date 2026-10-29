from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,pcbnew as p
D=Path(__file__).resolve().parents[1];S=D.parent/'power_system_schematic';C=D.parent/'power_core_layout_candidate'
a=E.parse(S/'power_system.xml');n=E.parse(D/'power_integrated_study.xml')
def nodes(t):return {(x.attrib['ref'],x.attrib['pin']):net.attrib['name'] for net in t.findall('./nets/net') for x in net}
old=nodes(a);expected={k:v.replace('CE_PERMISSION_EXTERNAL','CE_PERMISSION_INTERNAL') for k,v in old.items() if k[0] not in ['J102','J103'] and not (k[0]=='J5' and k[1] in ['3','4'])}
expected.update({('J5','3'):'GND',('RT102','1'):old['J1','1'],('RT102','2'):'GND',('J104','1'):old['RT101','1'],('J104','2'):'GND'})
assert expected==nodes(n),(set(expected.items())-set(nodes(n).items()),set(nodes(n).items())-set(expected.items()))
comps={x.attrib['ref']:x for x in n.findall('./components/comp')};off={r for r,c in comps.items() if c.find("property[@name='exclude_from_board']") is not None};assert off=={'RT101','RT102'}

for c in a.findall('./components/comp'):
 r=c.attrib['ref']
 if r in ['J102','J103']:continue
 if r!='J5':assert comps[r].findtext('value')==c.findtext('value')
 assert (comps[r].find("property[@name='dnp']") is not None)==(c.find("property[@name='dnp']") is not None)
b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));f={x.GetReference():x for x in b.GetFootprints()};assert set(f)==set(comps)-off
count=0
for r,fp in f.items():
 assert fp.GetValue()==comps[r].findtext('value')
 assert fp.IsDNP()==(comps[r].find("property[@name='dnp']") is not None)
 for pad in fp.Pads():assert pad.GetNetname()==expected[r,pad.GetNumber()];count+=1
base=p.LoadBoard(str(C/'power_core_NOFAB.kicad_pcb'));contract=json.loads((D/'placement_contract.json').read_text());deleted={x['uuid'] for x in contract['removed_only_exposed_CE_branch']};tracks={x.m_Uuid.AsString():x for x in b.GetTracks()}
def geo(t):return (t.GetClass(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetLayer(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else None)
kept=0
for t in base.GetTracks():
 uid=t.m_Uuid.AsString()
 if uid in deleted:assert uid not in tracks;continue
 assert uid in tracks and geo(t)==geo(tracks[uid]);assert tracks[uid].GetNetname()==contract['net_rename'][t.GetNetname()];kept+=1
assert len(tracks)>=kept
baseids={x.m_Uuid.AsString() for x in base.GetTracks()}
added=[q for uid,q in tracks.items() if uid not in baseids]
for q in added:
 if isinstance(q,p.PCB_VIA):assert q.GetDrillValue()==p.FromMM(.3) and q.GetWidth(p.F_Cu)==p.FromMM(.6)
 else:assert q.GetWidth() in ([p.FromMM(.15),p.FromMM(.3)] if q.GetNetname()=='GND' else [p.FromMM(.15)]) and q.GetLayer()!=p.In1_Cu
for fp in base.GetFootprints():
 r=fp.GetReference()
 if r=='J5':continue
 ff=f[r];assert ff.GetPosition()==fp.GetPosition() and ff.GetOrientationDegrees()==fp.GetOrientationDegrees()
 for pad in fp.Pads():
  pp=next(x for x in ff.Pads() if x.GetNumber()==pad.GetNumber());assert pp.GetPosition()==pad.GetPosition() and pp.GetSize()==pad.GetSize() and pp.GetLayerSet().FmtBin()==pad.GetLayerSet().FmtBin()
result={'status':'PASS source, all pads, and preserved core track/via projection; connectivity checked separately','components':len(comps),'board_footprints':len(f),'offboard':sorted(off),'net_pins':len(expected),'nets':len(n.findall('./nets/net')),'board_padshapes':count,'core_copper_items_geometrically_unchanged':kept,'removed_only_obsolete_CE_branch':len(deleted),'added_thermal_track_via_items':len(added),'pcb_sha256':hashlib.sha256((D/'power_integrated_study.kicad_pcb').read_bytes()).hexdigest()}
(D/'projection_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

bom=[{'reference':r,'value':c.findtext('value'),'footprint':c.findtext('footprint'),'on_board':r not in off,'quantity':1,'DNP':c.find("property[@name='dnp']") is not None,'qualification':'candidate; not pack / assembly approved'} for r,c in sorted(comps.items())]
(D/'bom_candidates.json').write_text(json.dumps(bom,indent=2))
