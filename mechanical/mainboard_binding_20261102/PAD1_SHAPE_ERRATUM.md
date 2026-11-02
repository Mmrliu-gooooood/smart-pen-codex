# Documentation correction — J107.1 rectangular pad

Applies to frozen review `independent_interface_mechanics_20261102_0624/manifest.json`, SHA256 `3ac35318f5a0b6407a1fcf51737808a5c618defb088ff986ccbb26032419e94b` (15 payload files). The original frozen files remain unchanged.

The REVIEW.md statement implying EN1 has a rounded corner of radius .375mm is incorrect. **J107.1 / EN1 is a rectangular (`PAD_SHAPE_RECT`) 1.5×2mm pad in both parent24 and candidate617a. It has no active corner radius.** `GetRoundRectCornerRadius()` returns stored .375mm metadata, but that setting is inactive for RECT and cannot justify corner clearance. J107.2 / EN2 and J107.3 / GND are genuinely rounded rectangles with active .05mm corner radius.

The original geometry implementation used KiCad's native `TransformShapeToPolygon`, not a manually constructed rounded rectangle. This separate check verifies actual parent and candidate EN1 polygons each have exactly4 vertices and area3.000000mm²; the actual RECT geometry was respected. Original shape invariance check also compares native shape enums. Thus this is a documentation correction, not an invalidated clearance calculation; saved full installation budgets and scene remain unchanged. EN1 still has no authorized terminal neck. EN2/GND owner-ring classifications remain unchanged.

Replay `/usr/bin/python3 check.py`. Only dependencies: parent24 native, candidate617a native, original frozen review.py and manifest.json, at paths recorded in results.json/script. No PCB or old review files were modified.
