import pcbnew,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3];rows=[]
for mod,name in [('power_core_layout_candidate','power_core_NOFAB.kicad_pcb'),('power_integrated_layout_14x45','power_integrated_study.kicad_pcb')]:
 p=root/'hardware'/mod/name;b=pcbnew.LoadBoard(str(p));pts=[]
 for s in b.GetDrawings():
  if s.GetLayer()==pcbnew.Edge_Cuts:
   for pt in (s.GetStart(),s.GetEnd()):pts.append((pt.x/1e6,pt.y/1e6))
 if not pts:raise ValueError('No native outline')
 w=max(x[0] for x in pts)-min(x[0] for x in pts);h=max(x[1] for x in pts)-min(x[1] for x in pts);fs=list(b.GetFootprints())
 rows.append(dict(module=mod,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),footprints=len(fs),ICs=[f.GetReference() for f in fs if f.GetReference().startswith('U')],width=w,height=h,area=w*h,refs=sorted(f.GetReference() for f in fs)))
print(json.dumps(rows,indent=2))
