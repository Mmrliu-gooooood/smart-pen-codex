import os,json,hashlib,sys
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/pen_mech_kicad';os.environ['KICAD_CONFIG_HOME']='/tmp/pen_mech_kicad'
import pcbnew as p
R=Path(__file__).resolve().parent
src=Path(sys.argv[1]) if len(sys.argv)>1 else R.parents[1]/'hardware/mainboard_revC/mainboard_revC_localroutes.kicad_pcb'
b=p.LoadBoard(str(src));out=[]
edgepoints=[]
for g in b.GetDrawings():
 if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.Edge_Cuts:
  edgepoints.extend([(p.ToMM(g.GetStart().x),p.ToMM(g.GetStart().y)),(p.ToMM(g.GetEnd().x),p.ToMM(g.GetEnd().y))])
outline=[min(x for x,y in edgepoints),min(y for x,y in edgepoints),max(x for x,y in edgepoints),max(y for x,y in edgepoints)]
assert outline==[0.,0.,12.,95.],outline
for fp in b.GetFootprints():
 bounds=[]
 for g in list(fp.GraphicalItems())+list(fp.Pads()):
  if isinstance(g,p.PAD) or (isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_Fab):
   bb=g.GetBoundingBox();bounds.append([p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
 assert bounds,fp.GetReference()
 name=str(fp.GetFPID().GetLibItemName());ref=fp.GetReference()
 if 'PICO' in name:h=1.060;basis='Espressif max from electronics source'
 elif 'TSSOP' in name:h=1.2;basis='TI package max from electronics source'
 elif 'VSSOP' in name:h=1.1;basis='TI DGK0008A max from electronics source'
 elif 'SOT-23' in name:h=1.1;basis='Nexperia Fig18 max from electronics source'
 else:h=1.0;basis='ASSUMED; actual passive MPN and capacitor heights not frozen'
 out.append(dict(ref=ref,value=fp.GetValue(),footprint=name,dnp=bool(fp.IsDNP()),xy=[p.ToMM(fp.GetPosition().x),p.ToMM(fp.GetPosition().y)],angle=fp.GetOrientationDegrees(),bounds=[min(t[0] for t in bounds),min(t[1] for t in bounds),max(t[2] for t in bounds),max(t[3] for t in bounds)],height_max=h,height_basis=basis))
result=dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),outline_box_mm=outline,board_mm=[outline[2]-outline[0],outline[3]-outline[1],p.ToMM(b.GetDesignSettings().GetBoardThickness())],method='Actual F.Fab shape + pad AABB, conservative solid prisms; no courtyard/text. NOT exact component STEP.',components=sorted(out,key=lambda x:x['ref']))
(R/'inputs'/'revC_mechanical_extract.json').write_text(json.dumps(result,indent=2));print('Extracted',len(out),'footprints,',sum(not x['dnp'] for x in out),'populated')
