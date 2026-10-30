from pathlib import Path
import os,json,hashlib,xml.etree.ElementTree as E
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gate_cam_on_path_maintenance/native';N=D/'native';checked=[]
for f in N.rglob('*'):
 if f.is_file()and f.suffix not in ['.kicad_pcb','.kicad_prl']:
  relative=f.relative_to(N);src=S/relative
  if not src.is_file()or f.read_bytes()!=src.read_bytes():raise RuntimeError('Source/project/library differs '+str(relative))
  checked.append(str(relative))
x=E.parse(D/'fresh.xml');cs={c.get('ref'):c for c in x.findall('./components/comp')};count=len(x.findall('./nets/net/node'));contract=json.loads((D/'native_mpn_contract.json').read_text())
if len(cs)!=102 or count!=356:raise RuntimeError('Fresh source counts')
for ref,part in contract['parts'].items():
 fields={f.get('name'):f.text for f in cs[ref].findall('./fields/field')}
 for k,key in [('Manufacturer','manufacturer'),('MPN','mpn'),('ProcurementStatus','status')]:
  if fields.get(k)!=part[key]:raise RuntimeError('Native MPN field changed '+ref+'.'+k)
f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
def filled(b):return{(z.m_Uuid.AsString(),int(l)):str(z.GetFilledPolysList(l).Format())for z in b.Zones()if not z.GetIsRuleArea()for l in z.GetLayerSet().Seq()}
a=filled(b);p.ZONE_FILLER(b).Fill(b.Zones());z=filled(b)
if a!=z:raise RuntimeError('Fresh refill changed polygons')
O=D/'guard_boards';O.mkdir(exist_ok=True);dest=O/'refilled.kicad_pcb';p.SaveBoard(str(dest),b)
print(json.dumps({'candidate_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'refilled_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'zone_layer_serializations_identical':True,'source_project_library_files_bit_identical_to_1c49':checked,'source_entities':len(cs),'source_endpoints':count,'native_MPN_refs_checked':sorted(contract['parts']),'JP301_source':cs['JP301'].findtext('value')},indent=2))
