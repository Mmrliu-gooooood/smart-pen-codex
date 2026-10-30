import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/pen_width14_extract'
import pcbnew as p
R=Path(__file__).resolve().parent;src=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_width14_preplacement/mainboard_revD.kicad_pcb')
raw=src.read_bytes();sha=hashlib.sha256(raw).hexdigest()
if sha!='f27cd35dcaf51fd33078b60a7029f6f63fba9c58f1d2791488e8a1721330080c':raise RuntimeError('Native input changed; coordinate authority must be rechecked')
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
 if ref=='AE101':a,c,bb,dd=8.6,-5.3,10.4,-1.9 # max ceramic1.8x3.4; pad envelope independently checked below
 parts.append(dict(ref=ref,footprint=name,side='B' if f.GetLayer()==p.B_Cu else 'F',dnp=f.IsDNP(),bounds=[a,c,bb,dd],height_total=ht,height_basis=basis))
(R/'input.json').write_text(json.dumps({'source':str(src),'sha256':sha,'parts':parts,'count':len(parts),'native_thickness_attribute':p.ToMM(b.GetDesignSettings().GetBoardThickness()),'applied_thickness_max':.93},indent=2));print(sha,len(parts))
