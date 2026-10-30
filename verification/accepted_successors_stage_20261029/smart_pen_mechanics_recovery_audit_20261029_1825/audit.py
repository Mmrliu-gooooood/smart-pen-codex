from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,pcbnew
R=Path(__file__).resolve().parent; W=R.parent; M=W/'smart_pen_mechanics_next_20261028/mechanical'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(b,s):
 if not b:raise ValueError(s)
out={'status':'NOFAB_INDEPENDENT_RECOVERY_AUDIT','manifests':[],'native_ports':{},'geometry':[]}
for name in ['compliant_retainer_longarc_0415','prewired_transfer_refill_last_0532','j301_y92p3_prescreen_0728','compliant_retainer_independent_audit_0500']:
 d=M/name;j=json.loads((d/'manifest.json').read_text()); rows=j['files']; rows=list(rows.values()) if isinstance(rows,dict) else rows
 for x in rows:
  p=d/x['path'];need(p.exists(),str(p));need(sha(p)==x['sha256'],'hash '+str(p));need(p.stat().st_size==x.get('size',x.get('bytes',p.stat().st_size)),'size')
 out['manifests'].append({'directory':str(d.relative_to(W)),'manifest_sha256':sha(d/'manifest.json'),'verified_members':len(rows)})
base=W/'smart_pen_next_20261028/hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';need(sha(base)=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','accepted baseline changed')
b=pcbnew.LoadBoard(str(base));out['native_sha256']=sha(base)
for f in b.GetFootprints():
 if f.GetReference() in ['J103','J301']:
  out['native_ports'][f.GetReference()]={'side':f.GetLayerName(),'origin':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'pads':[{'number':p.GetNumber(),'net':p.GetNetname(),'pcb_xy':[p.GetPosition().x/1e6,p.GetPosition().y/1e6],'pen_xz':[p.GetPosition().x/1e6-7,127-p.GetPosition().y/1e6]} for p in f.Pads()]}
for od in [19,20]:
 p=M/f'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD{od}_t0p93_NOFAB.FCStd';d=A.openDocument(str(p));S={o.Label:o.Shape.copy() for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name)
 need(all(s.isValid() and all(q.Volume>0 for q in s.Solids) for s in S.values()),'invalid shapes')
 refill=S['REF_D1_nominal'];c=Part.makeCylinder(1.175,67,A.Vector(0,-3.8,0));need(refill.cut(c).Volume<1e-8 and c.cut(refill).Volume<1e-8,'refill not exact cylinder')
 contact={k:{'distance_mm':refill.distToShape(S[k])[0],'common_mm3':refill.common(S[k]).Volume}for k in ['REF_Slider','REF_SoftGrip_COMPRESSED_ASSUMPTION','REF_HousingLeft','REF_HousingRight']}
 virtual={k:{'xyz_min':[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],'xyz_max':[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]}for k,s in S.items() if k in ['CONTACT_bare_main','GND_bare_main','REF_CTX_J103.1','REF_CTX_J103.2']}
 sweep=Part.makeCylinder(1.175,135,A.Vector(0,-3.8,-68));hits=[]
 for k,s in S.items():
  if k=='REF_D1_nominal':continue
  bb=s.BoundBox;sb=sweep.BoundBox
  if any(getattr(bb,t+'Max')<=getattr(sb,t+'Min') or getattr(sb,t+'Max')<=getattr(bb,t+'Min')for t in 'XYZ'):continue
  v=s.common(sweep).Volume
  if v>1e-7:hits.append([k,v])
 need(not hits,'refill sweep collision')
 p2=M/f'j301_y92p3_prescreen_0728/ACCESS{od}_B70p5_UNSELECTED_J301_proposed_NOFAB.FCStd';d=A.openDocument(str(p2));T={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name);frame=T['COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED']
 corridor=[]
 for x in [-1.2,1.2]:
  for edge in [33.6,37.2]:
   v=Part.makeBox(1.8,2,edge-28,A.Vector(x-.9,3.194793176328504,28)).common(frame).Volume;need(abs(v-2.016)<1e-7,'corridor failure');corridor.append({'x':x,'edge_z':edge,'common_mm3':v})
 out['geometry'].append({'OD':od,'source_sha256':sha(p),'shape_count':len(S),'refill_contact':contact,'virtual_main_ports':virtual,'continuous_cylinder_refill_sweep_hits':hits,'headward_corridor':corridor})
(R/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
