import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/pen_width14_extract'
import pcbnew as p
R=Path(__file__).resolve().parent;src=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/physical_interface_placement_candidate/mainboard_revD.kicad_pcb')
raw=src.read_bytes();sha=hashlib.sha256(raw).hexdigest()
if sha!='6b6d35a6dc493b57abc39426057661a8bbc2f106bc9d0d2769bfa60f4f8c928a':raise RuntimeError('Native input changed; coordinate authority must be rechecked')
b=p.LoadBoard(str(src));parts=[]
for f in b.GetFootprints():
 name=str(f.GetFPID().GetLibItemName());ref=f.GetReference();bounds=[]
 for g in list(f.GraphicalItems())+list(f.Pads()):
  if isinstance(g,p.PAD) or (isinstance(g,p.PCB_SHAPE) and g.GetLayer() in [p.F_Fab,p.B_Fab]):
   bb=g.GetBoundingBox();bounds.append([p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
 if not bounds:raise RuntimeError(ref)
 ht=1.3+.15;basis='Unknown passive/body1.3 plus solder.15 assumption'
 for token,h in [('PICO',1.06),('TSSOP',1.2),('VSSOP',1.1),('SOT-23',1.1)]:
  if token in name:ht=h+.15;basis=token+' source package bound plus.15 solder'
 if ref in ['R112','R113']:ht=1.+.15;basis='Digital proposal body1.0 plus solder.15, not qualified MPN'
 if ref=='AE101':ht=1.4+.15;basis='Johanson maximum1.4 plus.15 solder'
 if ref=='J109':ht=2.;basis='Digital proposal wire+solder2.0 from F copper surface; no added.15'
 a,c=[min(v[i] for v in bounds) for i in [0,1]];bb,dd=[max(v[i] for v in bounds) for i in [2,3]]
 if ref=='AE101':
  x,y=p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)
  if abs(f.GetOrientationDegrees()-90)>1e-6:raise RuntimeError('AE rotation needs oriented package model')
  a,c,bb,dd=min(a,x-.9),min(c,y-1.7),max(bb,x+.9),max(dd,y+1.7)
 parts.append(dict(ref=ref,value=f.GetValue(),nets={pad.GetNumber():pad.GetNetname() for pad in f.Pads()},footprint=name,side='B' if f.GetLayer()==p.B_Cu else 'F',dnp=f.IsDNP(),bounds=[a,c,bb,dd],height_total=ht,height_basis=basis))
(R/'input.json').write_text(json.dumps({'source':str(src),'sha256':sha,'parts':parts,'count':len(parts),'native_thickness_attribute':p.ToMM(b.GetDesignSettings().GetBoardThickness()),'applied_thickness_max':.93},indent=2));print(sha,len(parts))
