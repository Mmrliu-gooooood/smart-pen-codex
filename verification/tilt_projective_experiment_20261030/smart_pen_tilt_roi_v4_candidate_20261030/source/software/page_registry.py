"""Provisioned section/page mapping; does not discover arbitrary paper IDs."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Page:
    page_id: int
    section_u: int
    section_v: int
    width_cells: int
    height_cells: int
    spacing_um: float

class Registry:
    def __init__(self, pages):
        self.by_section = {}
        ids = set()
        for p in pages:
            if not isinstance(p, Page):
                raise ValueError('expected provisioned Page')
            for value, lo, hi in [(p.page_id, 1, 2**32-1),
                                  (p.section_u, 0, 62), (p.section_v, 0, 62),
                                  (p.width_cells, 6, 4096), (p.height_cells, 6, 4096)]:
                if type(value) is not int or not lo <= value <= hi:
                    raise ValueError('noncanonical page manifest')
            if type(p.spacing_um) not in (int, float) or not math.isfinite(p.spacing_um) or p.spacing_um <= 0:
                raise ValueError('invalid physical spacing')
            key = (p.section_u, p.section_v)
            if key in self.by_section or p.page_id in ids:
                raise ValueError('duplicate page ID or physically ambiguous section')
            self.by_section[key] = p
            ids.add(p.page_id)

    def resolve(self, section_u, section_v):
        # Never reduce unknown/out-of-range values modulo63 silently.
        if type(section_u) is not int or type(section_v) is not int:
            raise ValueError('invalid section')
        try:
            return self.by_section[(section_u, section_v)]
        except KeyError as exc:
            raise ValueError('unknown section: do not emit VALID coordinates') from exc
