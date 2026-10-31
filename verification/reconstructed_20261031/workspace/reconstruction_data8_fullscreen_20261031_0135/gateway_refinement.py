from pathlib import Path
import json,hashlib,os
os.makedirs('/tmp/d2trial0145',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/d2trial0145';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;q0=O/'intermediate_a931.kicad_pcb';q1=O/'selected_native.kicad_pcb'
if hashlib.sha256(q0.read_bytes()).hexdigest()!='a93102ae5ead18a965fbd7457202aad72e9ffece2d882471dcac8ddb49e2b60d'or hashlib.sha256(q1.read_bytes()).hexdigest()!='f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71':raise RuntimeError('snapshot binding')
a=p.LoadBoard(str(q0));b=p.LoadBoard(str(q1));old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()}
def ident(t):return [t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
changed={u for u in old if ident(old[u])!=ident(new[u])};expected={'6b437cf9-0c5b-492a-9449-6a510087a8e0','c0176840-a919-480b-a4fd-14b52cb9bebe','9650204e-bfdf-4193-a6c2-b1b4c28fcc5b'}
if set(old)!=set(new)or changed!=expected:raise RuntimeError('more than declared three copper objects changed')
j=json.load(open(O/'results.json'));rows=[r for r in j['rows']if r['uuid']in changed]
if len(rows)!=3 or any(r[k]for r in rows for k in ['body_hits','Fab_bbox_hits','courtyard_hits']):raise RuntimeError('changed object projection')
(O/'changed_objects.json').write_text(json.dumps({'before_sha256':hashlib.sha256(q0.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(q1.read_bytes()).hexdigest(),'only_three_copper_objects_changed':True,'rows':rows,'scope':'finite mechanical source/route changes only; reference/fill outcome not qualified'},indent=2)+'\n')
