#!/usr/bin/python3
import os
os.environ.update(XDG_CONFIG_HOME='/tmp/rebuild-kicad/config',XDG_CACHE_HOME='/tmp/rebuild-kicad/cache',XDG_DATA_HOME='/tmp/rebuild-kicad/data')
import pcbnew as p,json,math,hashlib,xml.etree.ElementTree as E
from pathlib import Path
B=Path(__file__).resolve().parents[1];A=B.parent/'usb_tail_revA';ba=p.LoadBoard(str(A/'usb_tail_revA.kicad_pcb'));bb=p.LoadBoard(str(B/'usb_tail_revA.kicad_pcb'))
def pads(b):return {(f.GetReference(),a.GetNumber(),a.m_Uuid.AsString()):a for f in b.GetFootprints() for a in f.Pads()}
a,z=pads(ba),pads(bb);assert a.keys()==z.keys();changes=[]
for k in a:
 x,y=a[k],z[k];assert x.GetNetname()==y.GetNetname();assert x.GetDrillSize()==y.GetDrillSize();assert x.GetLayerSet().FmtHex()==y.GetLayerSet().FmtHex()
 if x.GetSize()!=y.GetSize() or x.GetPosition()!=y.GetPosition():
  assert k[0]=='J101' and k[1] in ['A1','B12','A12','B1'];assert abs(p.ToMM(y.GetPosition().y-x.GetPosition().y)-.04)<1e-8;assert abs(p.ToMM(y.GetSize().y)-1.07)<1e-8
  changes.append(k[:2])
assert len(changes)==4
for f in ['usb_tail_revA.kicad_pro']:assert (A/f).read_bytes()==(B/f).read_bytes()
def xmlmap(d):
 x=E.parse(d/'usb_tail_revA.xml');return {(q.attrib['ref'],q.attrib['pin']):n.attrib['name'] for n in x.findall('./nets/net') for q in n}
assert xmlmap(A)==xmlmap(B)
assert 'Found 0 DRC violations' in (B/'drc.rpt').read_text();assert 'Found 0 Footprint errors' in (B/'drc.rpt').read_text();assert 'Found 0 unconnected pads' in (B/'drc.rpt').read_text()
r={'changed_copper_pads':changes,'all_pad_net_drill_layer_checks':'PASS','symbol_pin_net_map_unchanged':True,'project_rules_byte_identical':True,'minimum_clearance_mm':math.hypot(.16,.73)-.475,'bounding_rectangle_area_reduction_percent':100*.08/1.15,'rounded_copper_area_reduction_percent':100*.6*.08/(.6*1.15-(4-math.pi)*.15**2),'board_sha256':hashlib.sha256((B/'usb_tail_revA.kicad_pcb').read_bytes()).hexdigest(),'status':'ASSEMBLY-UNQUALIFIED GEOMETRY CANDIDATE; NO FAB'}
(B/'delta_checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
