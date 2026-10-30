from pathlib import Path
import os,json,hashlib,xml.etree.ElementTree as E,collections
os.environ['XDG_CONFIG_HOME']='/tmp/mainboard-index0203'
import pcbnew as p
from finite_copper import build,components
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/sens_tree_candidate_0158';B=S/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(B));xml=E.parse(D/'source_netlist.xml').getroot();comps={c.get('ref'):c for c in xml.findall('.//components/comp')};pins={}
for n in xml.findall('.//nets/net'):
 for q in n: pins[q.get('ref')+'.'+q.get('pin')]=dict(q.attrib,source_net=n.get('name'))
ns=build(b);groups={n:components(v)for n,v in ns.items()};core=json.loads((S/'verification.json').read_text())['core'];rows=[];uidmap={}
for f in b.GetFootprints():
 for q in f.Pads():
  name=f.GetReference()+'.'+q.GetNumber();u=q.m_Uuid.AsString();src=pins.get(name);c=comps.get(f.GetReference());sheet=next((a.get('value')for a in c.findall('property')if a.get('name')=='Sheetfile'),None)if c is not None else None
  row=dict(pad=name,uuid=u,net=q.GetNetname(),source=src,source_sheet=sheet,value=f.GetValue(),position=[q.GetPosition().x/1e6,q.GetPosition().y/1e6],layers=[b.GetLayerName(l)for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]if q.IsOnLayer(l)])
  if src and src['source_net']!=q.GetNetname():raise RuntimeError('net mismatch '+name)
  rows.append(row);uidmap[u]=row
for t in b.GetTracks():uidmap[t.m_Uuid.AsString()]=dict(net=t.GetNetname(),kind=t.GetClass(),uuid=t.m_Uuid.AsString())
drc=json.loads((S/'drc.json').read_text());airs=collections.defaultdict(list)
for i,e in enumerate(drc['unconnected_items']):
 nets={uidmap[x['uuid']]['net']for x in e['items']if x['uuid']in uidmap}
 if len(nets)!=1:raise RuntimeError('cannot assign airwire '+str(i)+str(nets))
 airs[next(iter(nets))].append(dict(index=i,items=[dict(x,actual=uidmap.get(x['uuid']))for x in e['items']]))
remaining={}
for net in ['3V3_AON','GND']:
 remaining[net]=[r for r in rows if r['net']==net and r['pad']not in core[net]['after']and not any(x.startswith(r['pad']+'#'+r['uuid'])for x in core[net]['after'])]
if [len(remaining[n])for n in ['3V3_AON','GND']]!=[16,45]:raise RuntimeError('core counts')
# Old source only supplies candidate object inventory; any changed pads prohibit blind whole-net reuse.
oldpath=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';old=p.LoadBoard(str(oldpath));oldpads={f.GetReference()+'.'+q.GetNumber():(q.GetPosition().x,q.GetPosition().y,q.GetNetname())for f in old.GetFootprints()for q in f.Pads()};oldobjects=collections.defaultdict(list)
for t in old.GetTracks():oldobjects[t.GetNetname()].append(dict(uuid=t.m_Uuid.AsString(),kind=t.GetClass(),layer=old.GetLayerName(t.GetLayer()),width=(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6))
def category(n):
 if n in ['3V3_AON','GND','SENS_VIO_1V8','CAM_3V3_SW','CAM_LOAD']:return 'power_ground_or_commissioned_output'
 if (n.startswith('CAM_D') and n[5:].isdigit())or n in ['CAM_PCLK','CAM_VSYNC','CAM_HREF','CAM_XCLK']:return 'MCU_to_translator_DVP_or_clock'
 if n.startswith('SENS_'):return 'head_DVP_reference_or_control'
 if n in ['UNUSED_A_INPUT','UNUSED_B_INPUT']:return 'required_unused_input_bias_NOT_open_output'
 if n=='BATTERY_ADC':return 'battery_measurement_port'
 if n=='IO_ENABLE_LINK':return 'camera_gate_SCCB_or_mode_control'
 if 'SCCB'in n or 'ISO'in n or n.startswith('CAM_'):return 'camera_gate_SCCB_or_mode_control'
 if n in ['CONTACT','NIB_CONTACT_N']or any(s in n for s in ['PRESS','PEN','FORCE','FSR','TIP']):return 'pressure_pen_contact'
 if any(s in n for s in ['USB','UART','BOOT','EN','RESET']):return 'host_USB_boot_control'
 if any(r['source_sheet']and 'pickup' in r['source_sheet'] for r in rows if r['net']==n):return 'pickup_IMU_or_pressure_side'
 return 'other_source_review'
netrows=[]
for n,g in sorted(groups.items()):
 pads=[r for r in rows if r['net']==n];changed=[r['pad']for r in pads if oldpads.get(r['pad'])!=(round(r['position'][0]*1e6),round(r['position'][1]*1e6),n)]
 netrows.append(dict(net=n,category=category(n),physical_pad_count=len(pads),components=g,native_unconnected_count=len(airs[n]),native_unconnected=airs[n],pads=pads,old_reuse_candidate=dict(old_sha=hashlib.sha256(oldpath.read_bytes()).hexdigest(),objects=oldobjects[n],changed_pad_positions_or_net=changed,status='READ_ONLY_INVENTORY_NOT_ROUTE_APPROVAL'))) 
opens=[r for r in rows if r['pad'].startswith('JP301.')or not r['net']or r['net'].startswith('unconnected-')]
r=dict(status='READ_ONLY_NOFAB_NOT_FORMAL_BASELINE_REPLACEMENT',pcb_sha=hashlib.sha256(B.read_bytes()).hexdigest(),native_counts=[len(drc[k])for k in ['violations','unconnected_items','schematic_parity']],core_counts={n:dict(connected=len(c['after']),total=c['total'])for n,c in core.items()},remaining_core_pads=remaining,all_nets=netrows,open_boundary_review=opens,notes=['JP301 two DIFFERENT nets must remain isolated across switch; same-side net airwires still require connection','Empty net and source unconnected pins are not proposed shorting targets','143 CLI airwire items are not 143 pads; component counts use finite copper actual layer geometry','Source pinfunction from exported same source XML, never empty PCB GetPinFunction'])
(D/'recovery.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(counts=r['native_counts'],remaining={n:len(x)for n,x in remaining.items()},nets_with_airwires=[(x['net'],x['category'],x['native_unconnected_count'],len(x['components']))for x in netrows if x['native_unconnected_count']],opens=[(x['pad'],x['net'])for x in opens]),indent=2))
