"""Independent centered anisotropic/projective Gray8 fixture rasterizer.

Synthetic only. Uses frozen original Python paper encoder directions, not C.
No center/scale/angle/true coordinates are sent to the production decoder.
"""
from dataclasses import dataclass
import math
import random
from roi_fixture import vectors

@dataclass(frozen=True)
class Render:
    columns: int = 6
    pitch: float = 18.0
    scale_y: float = 1.0
    angle: float = 0.0
    tx: float = 128.35
    ty: float = 127.65
    offset: float = 1/6
    radius: float = .10
    perspective_x: float = 0.0
    perspective_y: float = 0.0
    shear: float = 0.0
    noise: int = 0
    seed: int = 7241
    omit: tuple = ()
    width: int = 256
    height: int = 256


def render(directions, spec=Render()):
    co, si = math.cos(math.radians(spec.angle)), math.sin(math.radians(spec.angle))
    rows = len(directions)//spec.columns
    def project(x, y):
        denominator = 1+spec.perspective_x*x+spec.perspective_y*y
        xx, yy = x+spec.shear*y, y*spec.scale_y
        return (spec.tx+spec.pitch*(co*xx-si*yy)/denominator,
                spec.ty+spec.pitch*(si*xx+co*yy)/denominator)
    pixels = bytearray([240])*(spec.width*spec.height)
    for index, direction in enumerate(directions):
        if index in spec.omit:
            continue
        dx, dy = ((0,-1),(-1,0),(1,0),(0,1))[direction]
        cx = index%spec.columns-(spec.columns-1)/2+dx*spec.offset
        cy = index//spec.columns-(rows-1)/2+dy*spec.offset
        bounds = [project(cx+x, cy+y) for x in (-spec.radius,spec.radius)
                  for y in (-spec.radius,spec.radius)]
        x0 = max(0, math.floor(min(x for x,y in bounds))-1)
        x1 = min(spec.width, math.ceil(max(x for x,y in bounds))+1)
        y0 = max(0, math.floor(min(y for x,y in bounds))-1)
        y1 = min(spec.height, math.ceil(max(y for x,y in bounds))+1)
        for iy in range(y0,y1):
            for ix in range(x0,x1):
                coverage=0
                for sy in range(4):
                    for sx in range(4):
                        u=(ix+(sx+.5)/4-spec.tx)/spec.pitch
                        v=(iy+(sy+.5)/4-spec.ty)/spec.pitch
                        qy=(-si*u+co*v)/spec.scale_y
                        qx=co*u+si*v-spec.shear*qy
                        denominator=1-spec.perspective_x*qx-spec.perspective_y*qy
                        if denominator<=0:
                            continue
                        x,y=qx/denominator,qy/denominator
                        coverage+=(x-cx)**2+(y-cy)**2<=spec.radius**2
                pixels[iy*spec.width+ix]=min(pixels[iy*spec.width+ix],240-round(210*coverage/16))
    if spec.noise:
        rng=random.Random(spec.seed)
        for i in range(len(pixels)):
            pixels[i]=min(255,max(0,pixels[i]+rng.randint(-spec.noise,spec.noise)))
    return pixels
