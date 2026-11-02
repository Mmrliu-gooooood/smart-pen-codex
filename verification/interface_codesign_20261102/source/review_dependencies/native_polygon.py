"""One-shot conversion ONLY for raw native KiCad fractured fill, not a general normalizer."""
import pcbnew as p

def native_fractured_once(raw):
    # Caller must obtain this from the fixed native PCB GetFilledPolysList;
    # a Boolean output or a previously normalized polygon is NOT an input.
    if any(raw.HoleCount(i) for i in range(raw.OutlineCount())):
        raise RuntimeError('Already has explicit holes: Unfracture is NOT idempotent; refuse')
    out=p.SHAPE_POLY_SET(raw)
    out.Unfracture()
    added=p.SHAPE_POLY_SET();added.BooleanSubtract(out,raw)
    removed=p.SHAPE_POLY_SET();removed.BooleanSubtract(raw,out)
    # Numerical research guard, not an engineering clearance tolerance.
    if added.Area()/1e12>1e-4 or removed.Area()/1e12>1e-4:
        raise RuntimeError('One-shot native representation conversion changed material area')
    return out
