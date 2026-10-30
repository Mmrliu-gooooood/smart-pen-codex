"""Nominal support correction on caller-owned exact-outline derivative only.
No source save; caller must verify current contracts, states, and independent review.
"""
import sys,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part
V=A.Vector
B=2.264793176328504
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'smart_pen_mechanics_next_20261028/mechanical/compliant_retainer_longarc_0415/access_revision/retainer_geometry.py'
def box(a,b,c,d,e,f): return Part.makeBox(b-a,d-c,f-e,V(a,c,e))
def corrected_frame(thickness=.93,free=False,stop=False):
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!='94970d4bf82bc90afc1b31d83b610a4fc4320626fd57b238414c80d6ba034499': raise RuntimeError('frozen retainer source hash changed')
    code=SOURCE.read_text()
    old='for z in [45,131]:'
    if code.count(old)!=1: raise RuntimeError('source lateral-loop signature changed')
    ns={'__name__':'support_derivative_geometry'}
    exec(compile(code.replace(old,'for z in [45,119]:'),str(SOURCE),'exec'),ns)
    return ns['retainer'](thickness,free,stop)
def apply(doc, context, thickness=.93):
    O={o.Label:o for o in doc.Objects if hasattr(o,'Shape')}
    changes=[]
    if context.startswith('ACCESS'):
        lo=O['Lower_common_datum_STUDY'].Shape.copy()
        up=O['Upper_nonlocating_cover_STUDY'].Shape.copy()
        # Additional source-sized pockets only; preserve historical voids rather than invent fill.
        pockets=[box(7.1,8.05,B+.165,3.1,112.6,119.7),
                 box(7.3,7.9,B+.165,4.3,112.6,113.4),
                 box(7.6,8.05,B+.165,4.5,118.3,119.7)]
        for p in pockets: lo=lo.cut(p); up=up.cut(p)
        up=up.cut(box(6.65,7.9,3.4,4.5,110.5,119.7))
        # Retain old catch/structural junction: cutting it detaches a historical root
        # fragment (0.45 mm3). It no longer supports the RF-step board.
        # Add the same recessed secondary catch at the new lateral station.
        od=19 if '19' in context else 20
        outer=Part.makeCylinder(od/2,164,V(0,0,28))
        lo=lo.fuse(box(6.75,od/2,B-.8,B-.1,118,120).common(outer))
        # Same datum height and inward X extent; only extend axial face 1.7 mm.
        lo=lo.fuse(box(-7.2,-5,B+.2,B+.6,31.5,33.7))
        O['Lower_common_datum_STUDY'].Shape=lo
        O['Upper_nonlocating_cover_STUDY'].Shape=up
        O['COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'].Shape=corrected_frame(thickness)
        changes=['Lower_common_datum_STUDY','Upper_nonlocating_cover_STUDY','COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED']
    elif context=='RevD_BENCH':
        labels=[k for k in O if 'Common_base' in k]
        if len(labels)!=1: raise RuntimeError('cannot identify unique common base: '+str(labels))
        k=labels[0]
        O[k].Shape=O[k].Shape.fuse(box(-7.2,-5,B+.2,B+.6,30.5,33.7))
        changes=[k]
    else: raise ValueError('No retained board support modeled for '+context)
    doc.recompute()
    return changes
