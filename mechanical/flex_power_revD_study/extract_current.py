import pathlib,json,hashlib,os
os.environ['XDG_CONFIG_HOME']='/tmp/pen_revD_extract'
import pcbnew as p
R=pathlib.Path(__file__).resolve().parent
S=R.parents[2]/'smart_pen_next_20261028'
# Sibling repository root is supplied explicitly, not inferred from current working directory.
S=pathlib.Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028')
sources={'mainboard':'hardware/mainboard_revD/routing_trial/xclk5_review/mainboard_revD.kicad_pcb','power':'hardware/power_integrated_layout_14x45/power_integrated_study.kicad_pcb','usb':'hardware/usb_tail_revB/usb_tail_revA.kicad_pcb'}
result={}
for name,rel in sources.items():
 src=S/rel;b=p.LoadBoard(str(src));pts=[];parts=[]
 for g in b.GetDrawings():
  if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.Edge_Cuts:
   pts.extend([(p.ToMM(g.GetStart().x),p.ToMM(g.GetStart().y)),(p.ToMM(g.GetEnd().x),p.ToMM(g.GetEnd().y))])
 for fp in b.GetFootprints():
  bounds=[]
  for g in list(fp.GraphicalItems())+list(fp.Pads()):
   if isinstance(g,p.PAD) or (isinstance(g,p.PCB_SHAPE) and g.GetLayer() in (p.F_Fab,p.B_Fab)):
    bb=g.GetBoundingBox();bounds.append([p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
  if not bounds:raise RuntimeError(fp.GetReference())
  foot=str(fp.GetFPID().GetLibItemName())
  h,basis=1.,'ASSUMED passive maximum; actual MPN not frozen'
  for token,hh,why in [('PICO',1.06,'Espressif source max'),('TSSOP',1.2,'TI package max'),('VSSOP',1.1,'TI DGK package max'),('SOT-23',1.1,'Nexperia package max')]:
   if token in foot:h,basis=hh,why
  parts.append(dict(ref=fp.GetReference(),value=fp.GetValue(),footprint=foot,dnp=bool(fp.IsDNP()),back=fp.GetLayer()==p.B_Cu,bounds=[min(t[0] for t in bounds),min(t[1] for t in bounds),max(t[2] for t in bounds),max(t[3] for t in bounds)],height=h,height_basis=basis))
 result[name]=dict(source=rel,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),outline=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)],thickness=p.ToMM(b.GetDesignSettings().GetBoardThickness()),parts=parts)
(R/'inputs/current_board_extract.json').write_text(json.dumps(result,indent=2));print([(n,len(x['parts']),x['outline']) for n,x in result.items()])
