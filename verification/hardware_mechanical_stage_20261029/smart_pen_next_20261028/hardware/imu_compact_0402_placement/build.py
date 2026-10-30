from pathlib import Path
import pcbnew as p,json,shutil,sys
D=Path(__file__).resolve().parent;S=D.parent/'imu_decoupling_0805_placement';B=D.parent/'mainboard_input_imu_power_routing'
for f in S.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pro','.kicad_dru']or f.name in ['fp-lib-table','sym-lib-table']):
  z=D/f.relative_to(S);z.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,z)
plugin=p.PCB_IO_MGR.PluginFind(p.PCB_IO_MGR.KICAD_SEXP)
loaded={ref:plugin.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty',name,False)for ref,name in [('C501','C_0402_1005Metric'),('C502','C_0402_1005Metric'),('C503','C_0805_2012Metric')]}
a=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));fs={f.GetReference():f for f in a.GetFootprints()}
metadata={ref:{'value':fs[ref].GetValue(),'path':fs[ref].GetPath().AsString(),'nets':{q.GetNumber():q.GetNetname()for q in fs[ref].Pads()}}for ref in ['C501','C502','C503']}
removed={r['uuid']for r in json.loads((B/'imu_delta.json').read_text())['new_copper']}|{'7ff51579-a344-472f-b95b-ce2f40e14e29','a7ab6d06-9c1d-488d-ba26-6049fdd23d4d','f846f371-173c-4963-b0a4-8c63e175ffb2','b2615cf4-3825-4299-93d3-eb9d1c34af7d','d64ca523-fb12-4098-ab1c-33fda7c93d6e'}
text=(B/'mainboard_revD.kicad_pcb').read_text()
def blocks(t):
 depth=0;quoted=False;escape=False;start=None
 for i,c in enumerate(t):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield start,i+1,t[start:i+1]
   depth-=1
cuts=[]
for lo,hi,block in blocks(text):
 if block.startswith(('(segment','(via'))and any(u in block for u in removed):cuts.append((lo,hi))
 if block.startswith('(footprint')and any('(property "Reference" "'+r+'"'in block for r in metadata):cuts.append((lo,hi))
if len(cuts)!=len(removed)+3:raise RuntimeError(('unexpected exact removal',len(cuts)))
for lo,hi in reversed(cuts):text=text[:lo]+text[hi:]
(D/'mainboard_revD.kicad_pcb').write_text(text);b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
changes=[]
for ref,name,xy,angle in [('C501','C_0402_1005Metric',(6.2,80.7),0),('C502','C_0402_1005Metric',(6.2,82),0),('C503','C_0805_2012Metric',(5.3,84.5),0)]:
 f=loaded[ref];f.SetReference(ref);f.SetValue('10uF 10V X7R 10%'if ref=='C503'else metadata[ref]['value']);f.SetPath(p.KIID_PATH(metadata[ref]['path']));f.SetPosition(p.VECTOR2I(*(round(x*1e6)for x in xy)));f.SetOrientationDegrees(angle);f.SetFPID(p.LIB_ID('Capacitor_SMD',name));b.Add(f)
 for q in f.Pads():q.SetNet(b.FindNet(metadata[ref]['nets'][q.GetNumber()]))
 f.Reference().SetLayer(p.F_Fab);changes.append({'ref':ref,'xy':xy,'angle':angle,'footprint':name})
for ref,x in [('R501',2.6)]:
 f=next(q for q in b.GetFootprints()if q.GetReference()==ref);f.SetPosition(p.VECTOR2I(round(x*1e6),86500000));f.SetOrientationDegrees(0);f.Reference().SetLayer(p.F_Fab);changes.append({'ref':ref,'side':'F.Cu','xy':[x,86.5],'angle':0})
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b);shutil.copyfile(B/'mainboard_revD.kicad_pro',D/'mainboard_revD.kicad_pro');shutil.copyfile(B/'fp-lib-table',D/'fp-lib-table')
sys.path.insert(0,str(D.parent/'explicit_stackup_metadata_candidate'));from embed_stackup import embed
fn=D/'mainboard_revD.kicad_pcb';fn.write_text(embed(fn.read_text(),json.loads((D.parents[1]/'docs/research/stackup_qualification/candidate_contract.json').read_text())))
(D/'placement_delta.json').write_text(json.dumps({'changed':changes,'removed_previous_imu_copper':sorted(removed),'source0402_pending':True},indent=2))
