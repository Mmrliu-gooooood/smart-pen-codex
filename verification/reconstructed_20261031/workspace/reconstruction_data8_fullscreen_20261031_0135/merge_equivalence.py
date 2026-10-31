from pathlib import Path
import json,os,hashlib
os.makedirs('/tmp/merge0135',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/merge0135';import pcbnew as p
O=Path(__file__).resolve().parent
q0=O/'source_DIAGNOSTIC.kicad_pcb';q1=O/'intermediate_a931.kicad_pcb'
if hashlib.sha256(q0.read_bytes()).hexdigest()!='86414a58caa9f8e8feb4b04a37e2bce38156accb33afe3b862b7b06c58742c38'or hashlib.sha256(q1.read_bytes()).hexdigest()!='a93102ae5ead18a965fbd7457202aad72e9ffece2d882471dcac8ddb49e2b60d':raise RuntimeError('exact snapshots')
b0=p.LoadBoard(str(q0));b1=p.LoadBoard(str(q1));a={t.m_Uuid.AsString():t for t in b0.GetTracks()};b={t.m_Uuid.AsString():t for t in b1.GetTracks()};kept='59368a34-8818-4ebb-9016-6b7519a3c024';removed='a2960e11-f25b-4220-b12d-d18b7b8fbe4c'
def ident(t):return [t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
if set(a)-set(b)!={removed}or set(b)-set(a)or {u for u in set(a)&set(b)if ident(a[u])!=ident(b[u])}!={kept}:raise RuntimeError('not one collinear merge only')
for t in [a[kept],a[removed],b[kept]]:
 if isinstance(t,p.PCB_VIA)or t.GetNetname()!='PICKUP_INT_N'or t.GetLayer()!=p.F_Cu or t.GetWidth()!=150000:raise RuntimeError('merge identity')
def shape(t):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,p.F_Cu,0,50,p.ERROR_OUTSIDE);return q
old=p.SHAPE_POLY_SET();old.BooleanAdd(shape(a[kept]),shape(a[removed]));new=shape(b[kept]);d0=p.SHAPE_POLY_SET();d1=p.SHAPE_POLY_SET();d0.BooleanSubtract(old,new);d1.BooleanSubtract(new,old);areas=[d0.Area()/1e12,d1.Area()/1e12]
if areas!=[0.0,0.0]:raise RuntimeError('finite copper changed')
(O/'merge_equivalence.json').write_text(json.dumps({'older_sha256':hashlib.sha256(q0.read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(q1.read_bytes()).hexdigest(),'kept_uuid':kept,'removed_uuid':removed,'only_those_copper_objects_changed':True,'old_minus_new_mm2':areas[0],'new_minus_old_mm2':areas[1],'finite_method':'native ERROR_OUTSIDE50nm','scope':'copper merge only; filled-reference equivalence independently handled by electrical author/reviewer'},indent=2)+'\n')
