from pathlib import Path
import os,sys,json,hashlib,shutil,re,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/schmitt0745'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];BASE=R/'hardware/camera_isolation_control_native_0628/native';SRC=R/'hardware/camera_schmitt_source_0744/native';N=Path(os.environ.get('SCHMITT_NATIVE_OUTPUT',str(D/'native')))
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
sha=lambda x:hashlib.sha256(x).hexdigest();req=lambda c,m:None if c else (_ for _ in ()).throw(RuntimeError(m))
raw=(BASE/'mainboard_revD.kicad_pcb').read_text();req(sha(raw.encode())=='63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c','frozen base')
plan=json.loads((D/'plan.json').read_text());req(not plan['geometry_errors']and not plan['pad_errors'],'plan finite clear')
hand=json.loads((SRC.parent/'handoff.json').read_text());shutil.copytree(SRC,N,dirs_exist_ok=True)
s=raw;removedblocks=[]
for a,z,block in reversed(list(children(s))):
 if (block.startswith(('(segment','(via'))and any(u in block for u in plan['removed']))or(block.startswith('(footprint')and '(property "Reference" "Q201"'in block):removedblocks.append(block);s=s[:a]+s[z:]
req(len(removedblocks)==7,'6 old copper plus Q')
f=N/'mainboard_revD.kicad_pcb';f.write_text(s);b=p.LoadBoard(str(f));V=lambda xy:p.VECTOR2I(*(round(v*1e6)for v in xy))
nc='unconnected-(U205-NC-Pad1)';b.Add(p.NETINFO_ITEM(b,nc))
for ref in ['U205','C209']:
 h=hand[ref];lib,name=h['footprint'].split(':');libpath=N/(lib+'.pretty') if lib=='SmartPenIO'else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
 fp=p.FootprintLoad(str(libpath),name);req(fp is not None,'load footprint')
 fp.SetReference(ref);fp.SetValue(h['value']);fp.SetFPIDAsString(h['footprint']);fp.SetPath(p.KIID_PATH(h['path']));fp.SetPosition(V((3,69)if ref=='U205'else(5.55,68.85)))
 if ref=='C209':fp.SetOrientationDegrees(270)
 b.Add(fp)
 nets={'1':nc,'2':'ISO_GATE','3':'GND','4':'CAM_ISO_OE_N','5':'3V3_AON'}if ref=='U205'else{'1':'3V3_AON','2':'GND'}
 functions={'1':'NC','2':'A','3':'GND','4':'Y','5':'VCC'}if ref=='U205'else{'1':'1','2':'2'}
 types={'1':'no_connect','2':'input','3':'power_in','4':'output','5':'power_in'}if ref=='U205'else{'1':'passive','2':'passive'}
 for pad in fp.Pads():pad.SetNetCode(b.GetNetcodeFromNetname(nets[pad.GetNumber()]));pad.SetPinFunction(functions[pad.GetNumber()]);pad.SetPinType(types[pad.GetNumber()])
 fp.Value().SetVisible(False);fp.Reference().SetVisible(False)
for fp in b.GetFootprints():
 if fp.GetReference()=='R202':fp.SetValue('10k 1%')
 if fp.GetReference()in ['R202','U205','C209']:
  mpn={'R202':'RC0603FR-0710KL','U205':'SN74LVC1G14DCKR','C209':'C0402C104K4RACTU'}[fp.GetReference()]
  field=fp.GetFieldByName('MPN')
  if field is None:field=p.PCB_FIELD(fp,fp.GetNextFieldId(),'MPN');fp.AddField(field)
  field.SetText(mpn);field.SetVisible(False);field.SetPosition(fp.GetPosition())
for row in plan['new']:
 if row['type']=='via':
  t=p.PCB_VIA(b);t.SetPosition(V(row['a']));t.SetWidth(p.F_Cu,round(row['width']*1e6));t.SetDrill(round(row['drill']*1e6));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(V(row['a']));t.SetEnd(V(row['b']));t.SetWidth(round(row['width']*1e6));t.SetLayer(b.GetLayerID(row['layer']))
 t.SetNetCode(b.GetNetcodeFromNetname(row['net']));b.Add(t)
p.SaveBoard(str(f),b)
# Deterministic IDs for only newly created native objects. Existing UUIDs preserved.
s=f.read_text();oldids=set(re.findall(r'\(uuid "([^"]+)"\)',raw))
def normalize(block,key):
 clean=re.sub(r'\(uuid "[^"]+"\)','(uuid)',block)
 def fix(m):
  u=m.group(1)
  return m.group(0)if u in oldids else '(uuid "'+str(uuid.uuid5(uuid.NAMESPACE_URL,'camera-schmitt0745/'+key+'/'+clean))+'")'
 return re.sub(r'\(uuid "([^"]+)"\)',fix,block)
for a,z,block in reversed(list(children(s))):
 if block.startswith('(footprint'):
  ref=re.search(r'\(property "Reference" "([^"]+)"',block).group(1)
  for x,y,child in reversed(list(children(block))):block=block[:x]+normalize(child,'fp/'+ref)+block[y:]
 elif block.startswith(('(segment','(via')):block=normalize(block,'copper')
 s=s[:a]+block+s[z:]
f.write_text(s)
b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);filled=f.read_bytes()
b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(f.read_bytes()==filled,'fill stable')
old=p.LoadBoard(str(BASE/'mainboard_revD.kicad_pcb'));oldtrack={t.m_Uuid.AsString()for t in old.GetTracks()};new=[t.m_Uuid.AsString()for t in b.GetTracks()if t.m_Uuid.AsString()not in oldtrack]
(N.parent/'materialization.json').write_text(json.dumps({'base_sha256':sha(raw.encode()),'pcb_sha256':sha(f.read_bytes()),'source_directory':str(SRC.relative_to(R)),'removed':plan['removed'],'added':sorted(new),'old_fp_removed':['Q201'],'new_fp_added':['U205','C209'],'changed_value':['R202'],'filled_twice_byte_stable':True,'native_track_via_count':len(list(b.GetTracks())),'status':'EXPERIMENT_STABLE_AON_USB_JTAG_ONLY_NOFAB_NOPOWER'},indent=2)+'\n');print('materialized',sha(f.read_bytes()),len(new))
