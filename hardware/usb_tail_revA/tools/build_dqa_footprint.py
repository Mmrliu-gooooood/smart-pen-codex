#!/usr/bin/env python3
from pathlib import Path
D=Path(__file__).resolve().parents[1];name='TI_DQA0010A_USON10_OfficialLandpattern';s=[f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr "TI DQA0010A land pattern 4220328/A 12/2015; TPD4E05U06 RevO page29; package lot still requires qualification") (attr smd)', '(property "Reference" "U?" (at 0 -1.8 0) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12))))','(property "Value" "TPD4E05U06DQAR" (at 0 1.8 0) (layer "F.Fab") (effects (font (size .6 .6) (thickness .1))))','(fp_rect (start -.5 -1.25) (end .5 1.25) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))','(fp_rect (start -.95 -1.5) (end .95 1.5) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))','(fp_circle (center -.85 -1.35) (end -.78 -1.35) (stroke (width .12) (type default)) (fill none) (layer "F.SilkS"))']
for n in range(1,11):
 x=-.4175 if n<=5 else .4175;y=(n-3)*.5 if n<=5 else (8-n)*.5;h=.4 if n in [3,8] else .2
 s.append(f'(pad "{n}" smd roundrect (at {x} {y}) (size .565 {h}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio {.05/h}) (solder_mask_margin .025))')
s.append(')');(D/'SmartPen.pretty'/(name+'.kicad_mod')).write_text('\n'.join(s));print('DQA0010A official-derived copper; mask.025/courtyard are candidate additions')
