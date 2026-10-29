from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,hashlib,re
D=Path(__file__).resolve().parents[1]
a=E.parse(D/'source_before.xml');z=E.parse(D/'mainboard_revD.xml')
def comps(t):return {c.attrib['ref']:{'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'dnp':c.find("property[@name='dnp']") is not None,'bom':c.find("property[@name='exclude_from_bom']") is not None} for c in t.findall('./components/comp')}
def nodes(t):return {(a.attrib['ref'],a.attrib['pin']):n.attrib['name'] for n in t.findall('./nets/net') for a in n}
ca,cz=comps(a),comps(z);na,nz=nodes(a),nodes(z);assert na==nz and len(nz)==374
changes=[(r,k,ca[r][k],cz[r][k]) for r in ca for k in ca[r] if ca[r][k]!=cz[r][k]]
assert changes==[('J106','footprint','', 'SmartPenIO:PowerWireLands3_KeyGap_NOFAB')],changes
b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};contract={c['ref']:c for c in json.loads((D/'schematic/unified_component_contract.json').read_text())};ct=0
for ref,f in fs.items():
 assert f.GetValue()==cz[ref]['value'] and f.IsDNP()==cz[ref]['dnp'] and f.IsExcludedFromBOM()==cz[ref]['bom']
 assert str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())==cz[ref]['footprint']
 c=contract[ref];assert f.GetPath().AsString()=='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c['sheet_path']+c['symbol_uuid']
 for pad in f.Pads():assert pad.GetNetname()==nz[ref,pad.GetNumber()];ct+=1
assert len(fs)==74 and ct==269
f=fs['J106'];geo=json.loads((D/'wireland_dimension_contract.json').read_text());assert [p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)]==[6,84]
for pad in f.Pads():
 c=geo['pads'][pad.GetNumber()];assert [p.ToMM(pad.GetPosition().x)-6,p.ToMM(pad.GetPosition().y)-84]==c['local_xy_mm']
 assert [p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y)]==c['size_mm']
 assert set(pad.GetLayerSet().Seq())=={p.F_Cu,p.F_Mask};assert abs(p.ToMM(pad.GetLocalSolderMaskMargin())-.04)<1e-8
 assert pad.GetShape()==(p.PAD_SHAPE_RECT if pad.GetNumber()=='1' else p.PAD_SHAPE_ROUNDRECT)
 if pad.GetNumber()!='1':assert abs(p.ToMM(pad.GetRoundRectCornerRadius())-.05)<2e-6

print('Native source/path/pin/DNP/FPID and J106 dimensions checked: 74 fp / 269 padshape')
