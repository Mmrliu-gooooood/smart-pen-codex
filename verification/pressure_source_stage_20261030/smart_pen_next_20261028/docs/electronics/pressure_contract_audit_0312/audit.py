import pcbnew as p,json,pathlib,hashlib,itertools,math
root=pathlib.Path('/workspace/scratch/fe148e758944'); out=root/'smart_pen_next_20261028/docs/electronics/pressure_contract_audit_0312'; src=root/'smart_pen_next_20261028/hardware/mcu_supply_access_candidate_0300/native/mainboard_revD.kicad_pcb'; b=p.LoadBoard(str(src)); data=[]
for f in b.GetFootprints():
 if f.GetReference() in ['R503','R504','C504','J103']:
  data.append(dict(ref=f.GetReference(),value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()),side=f.GetLayerName(),fields={x.GetName():x.GetText() for x in f.GetFields()},pads=[dict(number=a.GetNumber(),net=a.GetNetname(),xy=[a.GetPosition().x/1e6,a.GetPosition().y/1e6])for a in f.Pads()]))
calc={}
for r in [100000,47000]:
 rows=[]
 for v,t1,t2,rc in itertools.product([3.,3.6],[.99,1.01],[.99,1.01],[0,1]):
  i=v/(r*t1+1000*t2+rc); rows.append(dict(current_uA=i*1e6,low_v=i*(1000*t2+rc)))
 calc[str(r)]=dict(min_current_uA=min(x['current_uA']for x in rows),max_low_v=max(x['low_v']for x in rows),nominal_uA=3.3/(r+1000)*1e6,release_75pct_us=r*1.01*1.05e-9*math.log(4)*1e6)
res=dict(source=str(src.relative_to(root)),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),components=data,assumed_AON_V=[3,3.6],calculation=calc)
(out/'results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(calc))
