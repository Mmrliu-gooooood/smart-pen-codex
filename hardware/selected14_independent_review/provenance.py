from pathlib import Path
import hashlib,json,os
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p
D=Path(__file__).resolve().parent;H=D.parent
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
def req(v,m):
 if not v:raise RuntimeError(m)
verified={}
for name,expected in [('rf_width14_selected_board_candidate','dadc37f520951626c9c9c7d1b099d792d9975899b9a7841b61deea007114764f'),('mainboard_fixture_allocation_v3','1cf18808c04caf28839d677aaf92230f6e7757703602acd331ecd8d905cc96d8'),('mainboard_integration_harness_revB','7c789f8e99f0592979a7a3d0058f00aa4e93fd8f656a28e03f162be0a4bec48b')]:
 d=H/name;req(sha(d/'manifest.json')==expected,'manifest drift '+name);m=json.loads((d/'manifest.json').read_text());fs=m.get('files',m)
 for f,v in fs.items():req(sha(d/f)==(v if isinstance(v,str) else v['sha256']),'file drift '+name+'/'+f)
 verified[name]={'manifest_sha256':expected,'file_count':len(fs)}
for f in (H/'mainboard_fixture_allocation_v3/mainboard_projection').rglob('*.kicad_sch'):req(sha(f)==sha(D/'native_snapshot'/f.relative_to(H/'mainboard_fixture_allocation_v3/mainboard_projection')),'Native sheet differs')
a=p.LoadBoard(str(H/'rf_feed_conditional_candidate/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native_snapshot/mainboard_revD.kicad_pcb'))
def geom(t):return(t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth())
ta={t.m_Uuid.AsString():t for t in a.GetTracks()};tb={t.m_Uuid.AsString():t for t in b.GetTracks()};changes=[]
for uid,t in ta.items():
 if t.GetNetname()not in ['3V3_AON','GND']:continue
 req(uid in tb,'Power conductor removed')
 if geom(t)!=geom(tb[uid]):req(not isinstance(t,p.PCB_VIA),'Power via moved');changes.append(uid)
allowed={v['uuid'] for v in json.loads((D/'native_snapshot/local_clearance_delta.json').read_text()) if 'terminal_recenter'in v};req(set(changes)==allowed,'Unexpected return/power delta')
contract=D/'native_snapshot/stackup_contract_snapshot.json';req(contract.read_bytes()==(H.parent/'docs/research/stackup_qualification/candidate_contract.json').read_bytes(),'Stackup contract drift')
print(json.dumps({'frozen_inputs':verified,'all_selected_source_sheets_match_v3':True,'unchanged_old_power_and_ground_vias_trunks':True,'changed_terminal_branches':changes,'stackup_contract_sha256':sha(contract)},indent=2))
