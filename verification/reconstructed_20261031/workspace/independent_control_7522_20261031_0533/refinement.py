from pathlib import Path
import os,json,hashlib
os.makedirs('/tmp/service0524',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/service0524';import pcbnew as p
O=Path(__file__).resolve().parent;old=O.parent/'reconstruction_control_service_mechanics_20261031_0520/selected_native.kicad_pcb';new=O/'selected_native.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
need(sha(old)=='6902e59c0bd6cd76053f228343ea6859c4b5bac00d08abfcbd5b15971882aee6'and sha(new)=='7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1','exact source snapshots')
def specs(path):
 b=p.LoadBoard(str(path));return {t.m_Uuid.AsString():{'kind':t.GetClass(),'net':t.GetNetname(),'layer':t.GetLayerName(),'a':[t.GetStart().x,t.GetStart().y],'b':[t.GetEnd().x,t.GetEnd().y],'width':t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),'drill':t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None}for t in b.GetTracks()}
a,z=specs(old),specs(new);need(set(a)==set(z),'UUID set');changed={u:{'before':a[u],'after':z[u]}for u in a if a[u]!=z[u]};need(len(changed)==1,'one object');r=next(iter(changed.values()));x,y=r['before'],r['after'];need(x['net']=='CAM_PWDN_UART_RX'and x['layer']=='F.Cu','exact intended net/layer');need(all(x[k]==y[k]for k in ['kind','net','layer','width','drill','a']),'only end changed');need(x['b']==[10475000,56900000]and y['b']==[10462785,56924530],'exact endpoint refinement')
(O/'refinement_results.json').write_text(json.dumps({'old_sha256':sha(old),'new_sha256':sha(new),'only_one_endpoint_changed':changed,'scope':'real finite geometry change; whole final mechanics rerun independently; plane identity belongs to author/electrical evidence'},indent=2)+'\n')
