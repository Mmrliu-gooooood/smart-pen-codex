from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;F=p.F_Cu
base=json.loads((R/'docs/electronics/imu_left_fence_scope_0456/local_plan.json').read_text());g.old=[t for t in g.old if t.m_Uuid.AsString()not in base['removed']];parts={}
def ts(n,l,pts,w=.15):return[g.track(n,l,a,b,w)for a,b in zip(pts,pts[1:])]
def via(n,a,sz=.45,dr=.2):
 v=g.via(n,a);v.SetWidth(F,round(sz*1e6));v.SetDrill(round(dr*1e6));return v
for tag,items in base['parts'].items():
 parts[tag]=[via(t['net'],t['a'],t['width'],t['drill'])if t['type']=='via'else g.track(t['net'],g.b.GetLayerID(t['layer']),t['a'],t['b'],t['width'])for t in items]
parts.update({
'pullup_left':ts('3V3_AON',F,[(1.775,86.5),(.875,86.5)],.2)+[via('3V3_AON',(.875,86.5),.6,.3)],
'pullup_right':ts('3V3_AON',F,[(4.825,86.65),(4.35,86.175),(4.35,84.5)],.2),
'irq_mcu':ts('PICKUP_INT_N',F,[(2.575,9.4),(3.275,9.4),(3.275,8.9)])+[via('PICKUP_INT_N',(3.275,8.9))],
'scl_mcu':ts('AON_I2C_SCL',F,[(2.575,11),(3.45,11),(3.45,12.475),(3.925,12.475)])+[via('AON_I2C_SCL',(3.925,12.475))],
'sda_mcu':ts('AON_I2C_SDA',F,[(2.575,11.4),(3.125,11.4),(3.125,12.94),(2.575,12.94),(2.575,13.1)])+[via('AON_I2C_SDA',(2.575,13.1))]
})
for tag,items in parts.items():print(tag,g.errors(items),flush=True)
print('JOINT',g.errors(sum(parts.values(),[])),flush=True)
