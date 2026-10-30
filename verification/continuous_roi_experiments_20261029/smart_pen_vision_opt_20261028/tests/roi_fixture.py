"""Independent grayscale renderer; no calls into firmware or decoder.

Directions are frozen outputs of upstream py-microdots a4_fixed encoder
(source 0f8b569). The original renderer uses offset pitch/6. This renderer
supersamples disks and projects the complete disk, not merely its center.
Images are synthetic, NOT evidence of camera/optics performance.
"""
from dataclasses import dataclass, asdict
import json
import math
from pathlib import Path
import random


@dataclass(frozen=True)
class Render:
    columns: int = 6
    pitch: float = 16.0
    angle: float = 0.0
    tx: float = 32.3
    ty: float = 29.7
    offset: float = 1 / 6
    radius: float = .10
    perspective_x: float = 0.0
    perspective_y: float = 0.0
    noise: int = 0
    seed: int = 8291
    omit: tuple = ()
    width: int = 192
    height: int = 192


def render(directions, spec=Render()):
    """Inverse homography rasterization, 4x4 subpixel disk coverage."""
    angle = math.radians(spec.angle)
    co, si = math.cos(angle), math.sin(angle)
    dots = []
    for index, direction in enumerate(directions):
        if index in spec.omit:
            continue
        dx, dy = ((0, -1), (-1, 0), (1, 0), (0, 1))[direction]
        dots.append((index % spec.columns + dx * spec.offset,
                     index // spec.columns + dy * spec.offset))
    pixels = bytearray([240]) * (spec.width * spec.height)
    # Bound projected disks and inverse-map samples for an actual homography.
    for cx, cy in dots:
        bounds = []
        for dx in (-spec.radius, spec.radius):
            for dy in (-spec.radius, spec.radius):
                x, y = cx + dx, cy + dy
                den = 1 + spec.perspective_x * x + spec.perspective_y * y
                bounds.append((spec.tx + spec.pitch * (co*x-si*y) / den,
                               spec.ty + spec.pitch * (si*x+co*y) / den))
        x0 = max(0, math.floor(min(x for x, _ in bounds)) - 1)
        x1 = min(spec.width, math.ceil(max(x for x, _ in bounds)) + 1)
        y0 = max(0, math.floor(min(y for _, y in bounds)) - 1)
        y1 = min(spec.height, math.ceil(max(y for _, y in bounds)) + 1)
        for iy in range(y0, y1):
            for ix in range(x0, x1):
                count = 0
                for sy in range(4):
                    for sx in range(4):
                        u = (ix + (sx+.5)/4 - spec.tx) / spec.pitch
                        v = (iy + (sy+.5)/4 - spec.ty) / spec.pitch
                        qx, qy = co*u+si*v, -si*u+co*v
                        den = 1 - spec.perspective_x*qx - spec.perspective_y*qy
                        if den <= 0:
                            continue
                        x, y = qx/den, qy/den
                        count += (x-cx)**2 + (y-cy)**2 <= spec.radius**2
                pixels[iy*spec.width+ix] = min(pixels[iy*spec.width+ix], 240-round(210*count/16))
    if spec.noise:
        rng = random.Random(spec.seed)
        for i in range(len(pixels)):
            pixels[i] = min(255, max(0, pixels[i] + rng.randint(-spec.noise, spec.noise)))
    return pixels


def vectors():
    return json.loads((Path(__file__).parent/'fixtures/microdots_vectors.json').read_text())


def save_fixture(directory, name, vector, spec):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    pixels = render(vector['directions'], spec)
    (directory/(name+'.pgm')).write_bytes(
        f'P5\n{spec.width} {spec.height}\n255\n'.encode() + pixels)
    (directory/(name+'.json')).write_text(json.dumps({
        'source': 'upstream 0f8b569 py-microdots a4_fixed frozen vector',
        'synthetic_only': True, 'vector': vector, 'render': asdict(spec)}, indent=2)+'\n')
