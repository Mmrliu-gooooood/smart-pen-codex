from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;F=p.F_Cu;B=p.B_Cu
remove=['13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711','64d94581-4427-5e32-b859-8e4da0842006']
g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove]
def ts(n,l,points,w=.15):return[g.track(n,l,a,b,w)for a,b in zip(points,points[1:])]
def vi(n,a):
 q=g.via(n,a);q.SetWidth(F,450000);q.SetDrill(200000);return q
parts={
'aon_top_reconnect':ts('3V3_AON',F,[(2.65,79.9),(2.65,79.1),(5.72,79.1),(5.72,80.7)],.25),
'aon_left_reconnect':[vi('3V3_AON',(2.65,82.0))]+ts('3V3_AON',B,[(2.65,82.0),(2.,81.35),(2.,80.4),(2.65,79.9)],.25),
'scl_local':ts('AON_I2C_SCL',F,[(3.2375,81.25),(2.95,81.25),(2.65,80.9)])+[vi('AON_I2C_SCL',(2.65,80.9))],
'irq_local':ts('PICKUP_INT_N',F,[(3.75,81.2375),(3.825,81.075),(3.825,80.8),(4.025,80.8),(4.7,80.125)])+[vi('PICKUP_INT_N',(4.7,80.125))],
'sda_local':ts('AON_I2C_SDA',F,[(3.2375,82.75),(2.975,82.75),(2.9,82.675),(2.375,82.675)])+[vi('AON_I2C_SDA',(2.375,82.675))]
}
for name,items in parts.items():print(name,g.errors(items),flush=True)
print('JOINT',g.errors(sum(parts.values(),[])),flush=True)
if __name__=='__main__':
 def spec(t):
  v=isinstance(t,p.PCB_VIA)
  return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else g.b.GetLayerName(t.GetLayer()),a=[t.GetStart().x/1e6,t.GetStart().y/1e6],b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
 (D/'local_plan.json').write_text(json.dumps({'status':'READONLY_LOCAL_FANOUT_MODEL_NOT_NATIVE','parent_sha':'69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc','removed':remove,'parts':{k:[spec(t)for t in ts]for k,ts in parts.items()},'geometry_errors':g.errors(sum(parts.values(),[]))},indent=2)+'\n')
