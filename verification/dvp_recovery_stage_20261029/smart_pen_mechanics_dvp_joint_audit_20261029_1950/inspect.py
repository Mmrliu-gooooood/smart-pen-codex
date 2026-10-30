import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,pcbnew as p
W=Path(__file__).resolve().parent.parent;H=W/'smart_pen_next_20261028';M=W/'smart_pen_mechanics_next_20261028/mechanical'
a=p.LoadBoard(str(H/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(H/'hardware/dvp_rotated_group_placement_1835/native/mainboard_revD.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()}
for r,x,y,flip in [('R225',4.5,43.3,True),('R226',7.5,44,True),('R227',10.5,44,True),('R206',9,47,True),('J105',2,77.5,False),('J107',2.7,84,True)]:
 f=fs[r]
 if flip:f.Flip(f.GetPosition(),False)
 f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)))
 if r.startswith('R'):f.SetOrientationDegrees(0)
def snap(b):return{f.GetReference():dict(x=f.GetPosition().x/1e6,y=f.GetPosition().y/1e6,angle=f.GetOrientationDegrees(),side=f.GetLayerName())for f in b.GetFootprints()}
x=snap(a);y=snap(b);delta={r:dict(old=x[r],new=y[r])for r in x if x[r]!=y[r]}
d=A.openDocument(str(M/'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD19_t0p93_NOFAB.FCStd'));S={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')}
for r,row in delta.items():
 keys=[k for k in S if k.startswith('REF_CTX_'+r) and (k=='REF_CTX_'+r or k[len('REF_CTX_'+r):][0] in '._')]
 row['shapes']={k:[S[k].BoundBox.XMin,S[k].BoundBox.YMin,S[k].BoundBox.ZMin,S[k].BoundBox.XMax,S[k].BoundBox.YMax,S[k].BoundBox.ZMax]for k in keys}
print(json.dumps(delta,indent=2));(Path(__file__).parent/'delta.json').write_text(json.dumps(delta,indent=2)+'\n')
