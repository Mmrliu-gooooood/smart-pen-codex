# Metadata erratum — preceding frozen synthetic screen

This note supersedes only the metadata clauses below in `optics_paper_screen_20261031_1752`, whose final MANIFEST SHA256 is `42fa3e57cc9f9750a8d1daa4383974869ef9577d6581b8055ed7a66584990396`. Original files, image bytes, per-case results and run logs remain unchanged.

1. The18 affine controls use fixed normalized displacement **δ/p=1/6**, not varied .03/.05/.075mm. Under the explicitly synthetic .3mm pitch convention, displacement is fixed .05mm. Variable .10/1/6/.25 displacement belongs to the45 primary tilt/offset cases only. The repeated generic controls_summary.limits sentence claiming varying offset is obsolete.
2. Empty `by_tilt` / `by_offset` objects in controls_summary are unused aggregation-template fields, not missing runs or measured physical-tilt groups. Use the18 per-case `controls_results.json` entries and explicit affine axis-ratio/pitch fields. The controls are nonprojective anisotropy, not physical camera-tilt data.

Independent review reproduced all70 PGM hashes and decoder outcomes. These metadata corrections do not change22correct/0wrong/48rejected across70 images, nor validate actual optics. Final source code and image-byte provenance continue to be the bound original manifest; this successor note does not pretend to have the same hash as changed originals.
