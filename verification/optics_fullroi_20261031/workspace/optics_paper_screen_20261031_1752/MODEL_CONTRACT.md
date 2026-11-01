# Synthetic model and screening contract

Coordinates: paper point (x,y), optical-axis/plane intersection at camera depth D. Paper rotates about camera x axis by t (angle from plane normal to optical axis). Ideal pinhole projection:

`Z = D + y sin(t); u=f_px x/Z; v=f_px y cos(t)/Z`.

`J = [[f/Z, -f x sin(t)/Z²], [0, f D cos(t)/Z²]]`.

D is optical-axis distance from projection center, NOT normal height (D cos t), lens-front working distance or lens minimum focus distance. f_px is calibrated projection scale in pixel units, NOT specified real EFL or a selected lens. No physical sensor facts assumed.

For a selected centered6×6 lattice, centers span5p. Worst axis displacementδ and radiusd/2 give square half extent `h=2.5p+δ+d/2`. Project all four outer square corners; positive-depth homography maps this convex enclosure into a quadrilateral, enclosing every dot in this conservative setup. Failure of enclosure is NOT proof every actual codeword is clipped. This does NOT guarantee arbitrary lattice phase/window availability; additional half-cell-or-more phase/placement and occlusion margins require separate tests. In-plane rotation fixed0, camera fx=fy, principal point centered; no skew/distortion, defocus, finite aperture, rolling shutter or occlusion modeled.

Jacobian sampled at3×3 enclosure positions. Largest singular value computes a local worst-direction translational blur estimate `sigma_max*v*t_exp`. It is a local first-order estimate, not exact integrated motion for large motion; rotational motion absent. Min/max sampling not a proven global extremum for all unspecified optics. Pixel blur limit1, dot minor2px, nonorthogonality0.05, pitch spread10% are explicit ENGINEERING PROXIES, NOT decoder contracts or calibrated thresholds. Vary them before any design choice.

Grid rationale (exploratory, not availability): pitch .15/.3/.6/1/2/3.527778mm spans small/medium/current visible-paper control; d/p .12/.2/.3/.4 probes pixel detectability and merging; δ/p .10/1/6/.25/.30/.35 spans actual residual boundaries plus out-of-contract control. D5/10/20/40mm spans near-tip hypothesis distances; f_px250/500/1000 separates magnification from physical unknown sensor/lens. Tilt0/15/30/45/60 probes mild through large perspective. These are not ergonomic/print-process accepted ranges.

Fixed speed100mm/s and exposure100us are sensitivity reference values, not measured writing speed/exposure. Exposure bound scales inversely with speed. For15px/.3mm at100mm/s, scale50px/mm gives1px blur at200us; at500mm/s,40us. To discuss frame spacing independently: distance v/F, e.g.100mm/s at60fps=1.667mm/frame; no overlap guarantee or fps qualification. Absolute independent decoding need not require frame overlap, but path/pressure timestamp sampling and dropouts still need acceptance criteria. XCLK/PCLK and exposure register-to-time mappings remain unqualified and are not inferred here.

Model classification:
- INVALID_DEPTH: assumed full enclosure crosses camera plane; meaningless planar window for this geometry.
- SCREEN_REJECT: any conservative geometric/support contract fails. Positively spaced dots alone never prove decoding.
- MODEL_RISK: support checks pass, at least one explicit engineering proxy fails.
- MODEL_RETAIN_NOT_QUALIFIED: no modeled screen flag; not decoder, lens, printing, physical nib or IR acceptance.

V3 comparisons use96 and80 as geometric crop sizes ONLY. Actual V3 selects80 only when96 retained count>100; script does not execute that selection and cannot call80 an alternate rescue crop. Physical dot image area, contrast, connected-component count and actual codeword identity need raster/code tests rather than this geometry-only pass.

Numerical safety domain (not physical acceptance): projection requires finite inputs, D/f in[1e−6,1e6], |x|/|y|≤1e6 and depth≥1e−9; speed/exposure in[0,1e6]. Out-of-domain values raise ValueError rather than interpreting underflow as geometry. The published sweep is far inside these limits.
