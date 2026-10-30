"""Read-only positive native; create separate fully refilled per-target cut boards.
Expected dependency closures are declared from selected20 anchor graph BEFORE execution.
"""
from pathlib import Path
import os,sys,json,shutil,subprocess,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1]
BASE=R/'docs/electronics/ground_recovery_plan_0807/selected20_final.json'
selection=json.loads(BASE.read_text());targets=sorted({r['target_pad']for r in selection['new']})
EXPECTED={x:[x]for x in targets}
EXPECTED.update({'R224.2':['R224.2','R228.2'],'R226.2':['R206.2','R226.2'],'J104.3':['J104.3','R223.2'],'R220.2':['R220.2','R225.2']})
def require(c,s):
 if not c:raise RuntimeError(s)
require(len(targets)==20,'exact20declared')
DECL={'selection_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'expected_lost_core_pads':EXPECTED,'basis':'selected20 directed anchors: R228→R224; R206→proposed R226 via; R223→proposed J104 via; R225→proposed R220 branch; other targets original-core anchor or own via','no_source_or_positive_native_edits':True}
# --declare is usable before native exists, never loads or writes a PCB.
if '--declare'in sys.argv:
 print(json.dumps(DECL,indent=2));sys.exit()
name=os.environ.get('GROUND_NEG_CASE')
if not name:
 require((D/'native/mainboard_revD.kicad_pcb').exists(),'native_ready required')
 out=[]
 for x in targets:
  env={**os.environ,'GROUND_NEG_CASE':x}
  run=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[__file__],env=env,capture_output=True,text=True)
  (D/f'negative_ground_{x}{"_O"if sys.flags.optimize else""}.log').write_text(run.stderr)
  require(run.returncode==0,x+' '+run.stderr)
  out.append(json.loads(run.stdout))
 print(json.dumps({'status':'TRUE_REFILLED_20_GROUP_CUTS_NOFAB_NOPOWER','declaration':DECL,'cases':out},indent=2));sys.exit()
require(name in targets,'case must be one of20')
config=Path('/tmp/ground0818negative')/name
for sub in ['config','cache','data']:(config/sub).mkdir(parents=True,exist_ok=True)
os.environ.update(XDG_CONFIG_HOME=str(config/'config'),XDG_CACHE_HOME=str(config/'cache'),XDG_DATA_HOME=str(config/'data'))
import pcbnew as p
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
m=json.loads((D/'materialization.json').read_text());rows=[r for r in m['mapping']if r['target_pad']==name];selected=sorted(r['uuid']for r in rows);require(selected,'nonempty exact mapping')
positive=D/'native/mainboard_revD.kicad_pcb';positive_sha=hashlib.sha256(positive.read_bytes()).hexdigest()
a=p.LoadBoard(str(positive));na=build(a);ca={n:components(v)for n,v in na.items()};before=next(c for c in ca['GND']if'J106.3'in c)
require(len(before)==91,'positive91core');require(len(ca['GND'])==13,'positive13groundcomponents')
require(all(x in before for x in targets),'positive all selected targets in core')
root=D/'native_negative'/name;shutil.copytree(D/'native',root,dirs_exist_ok=True);f=root/'mainboard_revD.kicad_pcb';s=f.read_text();cuts=[]
for aa,zz,block in children(s):
 if block.startswith(('(segment','(via'))and any(u in block for u in selected):cuts.append((aa,zz))
require(len(cuts)==len(selected),'exact mapped copper deletion')
for aa,zz in reversed(cuts):s=s[:aa]+s[zz:]
f.write_text(s);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
b2=p.LoadBoard(str(f));nb=build(b2);cb={n:components(v)for n,v in nb.items()};core=next(c for c in cb['GND']if'J106.3'in c)
lost=sorted(set(before)-set(core));gained=sorted(set(core)-set(before));require(lost==sorted(EXPECTED[name]),'actuallost '+str(lost)+' expected '+str(EXPECTED[name]));require(not gained,'unexpected gained ground pads')
require(set(ca)==set(cb),'net names preserved')
for net in ca:
 if net!='GND':require(ca[net]==cb[net],'nonGND physical change '+net)
for sig,pins in {'NIB_CONTACT_N':['C504.1','R503.2','R504.1','U101.7'],'STRAP_GPIO3':['R103.1','U101.8'],'AON_I2C_SCL':['R501.2','U101.10','U501.1'],'AON_I2C_SDA':['R502.2','U101.11','U501.4'],'PICKUP_INT_N':['U101.6','U501.12']}.items():require(cb[sig]==[sorted(pins)],'unrelated '+sig)
require('J202.18'in next(c for c in cb['SENS_EXTCLK']if'U203.13'in c),'clock retained')
args=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(root/'drc.json'),str(f)]
run=subprocess.run(args,capture_output=True,text=True);(root/'drc.log').write_text(run.stdout+run.stderr);d=json.loads((root/'drc.json').read_text());counts=[len(d[k])for k in['violations','unconnected_items','schematic_parity']]
expected_unconnected=76+len(cb['GND'])-len(ca['GND'])
require(run.returncode==5 and counts[1]==expected_unconnected and counts[2]==0,'DRC expected '+str(expected_unconnected)+' actual '+str(counts)+' return'+str(run.returncode))
require(all(v['type']in['track_dangling','via_dangling']for v in d['violations']),'unexpected physical DRC '+str(d['violations']))
require(hashlib.sha256(positive.read_bytes()).hexdigest()==positive_sha,'positive changed')
print(json.dumps({'case':name,'removed_new_copper':selected,'declared_expected_lost':sorted(EXPECTED[name]),'actual_lost_pads':lost,'actual_gained_pads':gained,'remaining_GND_core_pad_count':len(core),'GND_component_count_before':len(ca['GND']),'GND_component_count_after':len(cb['GND']),'newly_isolated_components':[c for c in cb['GND']if set(c)&set(lost)],'actual_DRC_unconnected_parity':counts,'expected_unconnected_from_component_delta':expected_unconnected,'cut_induced_DRC_violations':d['violations'],'all_nonGND_component_graphs_preserved':True,'pressure_STRAP_IMU_I2C_clock_preserved':True,'positive_pcb_sha256':positive_sha,'cut_pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2))
