# Independent minimal SCCB mechanical review

**ACCEPT exact dcbd2e65 only for bounded nominal static-placement and finite exterior-copper/via geometry, with explicit retained-source and endpoint classifications. No SI, electrical/reference, physical-service, process or whole-assembly acceptance. NOFAB / NO POWER.**

Exact PCBdcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697. Native manifestdaf598f9fe33f7bf527182e87f18fcc6856a3362a178905833f4d7c8ca753789 (104files); mechanical package manifestfacf722570210efd941a9bc771e20a231e1068f14582dfa1bd5b922de4900946. Author confirmed freeze before copied execution. Checker verifies217 source manifest files across exact parent8312 and candidate.

## Native contract and placements

All103 stated footprint/pad contracts equal exact parent after only the three specified rigid transforms: R240F(11,70.5),180°; R241F(11.85,73.35),90°; C207F(10.85,65),−90°. Additional independent pad attribute/drill/offset/roundrect comparison finds no changes. Independent native derivation confirms six closed straight Edge.Cuts,14×99.8mm nominal. Four historical CAD source hashes independently match.

Four-context reproduction replaces all three moved bodies simultaneously, preserving full dimensions (R2402.45×.95×.70; R241 rotated.95×2.45×1.45; C207.95×2.45×1.45). No moved-body intersections. Minima R240/R203.55mm, R241/R203.65mm, C207/oppositeU301/C301.93mm. Moving R240+1mm nativeY reproduces R203 overlap.29925mm³ in every context. This is not global assembly proof; unchanged ACCESS/harness uncertainties remain.

## Finite changed copper and explicit exceptions

Independent count:26new tracks =15exterior+11inner, plus5vias. Native finite-width exterior tracks and both-face via discs tested against full retained installation envelopes, provisional U205/C209, Fab graphical bounds and actual courtyard polygons. No undeclared non-target hits; all five discs have no envelope/Fab/courtyard hits. Inner tracks are counted, not falsely modeled as exterior solid bodies. Endpoint-target overlaps remain reported and process-unqualified. Source corner exceptions are restricted to the two exact half-mm B segments, not every AON/GND route or every same-net body.

## Independent zero-new-underbody test

Exact .5mm B corner:(10.9,64.875)→(11.125,65.025)→(12.05,64.875).

Copied native polygon difference reproduces additional area **exactly0** in BOTH full C301 and U301 budgets after subtraction of unexpanded exact8312 B-side same-net tracks/vias. Independent OCC analytic round-cap reconstruction, not reuse of the polygon area calculation, also computes **0.0mm² residual in both**, normally and under -O. No expansion/tolerance buffer was applied to parent copper. Full branch projection is not zero: native polygon areas C301.039832019873/U301.000217537407mm²; independent analytic OCC areas.0398253692225/.000217190802684mm² differ slightly due polygon chord approximation, while both methods agree no newly occupied underbody area. OCC failure threshold1e-10mm² is recorded; computed residuals are exactly0.0.

This accepts only geometric inheritance at those two bodies, not real solder-mask/underside/thermal/seating qualification and not a blanket source exception.

## Deliberate patch and remaining gates

Reference zone definitions are correctly reported **not equal**: declared3V3_AON In2 patch rectangle[11.25,64,12.6,65.8]. Electrical reviewer owns zone refill/reference source-hole exception, local inner jog and C207 decoupling/return trade. No SI or loaded-edge/timing/current claim.

Still open: actual service/probe fixture and datum/runout/force/stroke; J104 and four DNP operational envelopes; target copper/solder/mask/tenting/seating; FPC insertion/bend/tool sweep; J103 strain relief/insulation; material retention, cell and final pen envelope.98 provisional static refs is not103 qualified installations.99.8mm nominal requires finished-outline tolerance to guarantee≤100mm. Prior inherited D0 full OPEN projected overlap remains explicit. No power, manufacture, purchase or source publication.

## Frozen artifact SHA256

```
a91f96dbebdfc4996bba06203994402c09b72414315a88cf8127500b4c7402c7  assembly_sccb_final_review_20261030_1218/README.md
cb7de991b80fd565e93e1b9d17b07f017b9cb9603862778d1757b323ed930217  assembly_sccb_final_review_20261030_1218/geometry_normal.json
cb7de991b80fd565e93e1b9d17b07f017b9cb9603862778d1757b323ed930217  assembly_sccb_final_review_20261030_1218/geometry_results.json
facf722570210efd941a9bc771e20a231e1068f14582dfa1bd5b922de4900946  assembly_sccb_final_review_20261030_1218/manifest.json
cb7de991b80fd565e93e1b9d17b07f017b9cb9603862778d1757b323ed930217  assembly_sccb_final_review_20261030_1218/placement_optimized.log
cb7de991b80fd565e93e1b9d17b07f017b9cb9603862778d1757b323ed930217  assembly_sccb_final_review_20261030_1218/placement_screen.log
feb0d13a956e2955e8733f0213624ae900f78d8ebc07cae83ed66748e4571b7b  assembly_sccb_final_review_20261030_1218/placement_screen.py
44c04d9376f14bbdc4b958da582a206ec50de6f96f0ce005b4f8de2f6eb3c78e  assembly_sccb_final_review_20261030_1218/results.json
44c04d9376f14bbdc4b958da582a206ec50de6f96f0ce005b4f8de2f6eb3c78e  assembly_sccb_final_review_20261030_1218/results_normal.json
c08b2e53fd297934ffe36bf00f901e7ba64154e12e091429335e0fdfcceae5d0  assembly_sccb_final_review_20261030_1218/screen.log
a02073ba8076e650f92e652347abc9044a8f84a66b616d653771975d13bab9c1  assembly_sccb_final_review_20261030_1218/screen.py
e430299900af039b656f06bfe11f83b82f8d5c3aa536d8d6b96127970f2b3299  assembly_sccb_final_review_20261030_1218/screen_optimized.log
75b2d90b73a9ec104e3e9b2fe7d52709720c0e6286d5b60411ac04c71fd8908a  assembly_sccb_final_review_20261030_1218/source_junction.json
54931e87017077b3f5fe5b7b50bfac287c04cbc8b4687343bfed155a1def8bc4  assembly_sccb_final_review_20261030_1218/source_junction.log
55b7103b84e398dd1a6444bb7c36d9bfc3909ca4dabd3ebe3892a78365af07e3  assembly_sccb_final_review_20261030_1218/source_junction.py
0ee66ab31abedf8140c426b0d89d6970af00afcec359c8123f459ecdfabcad71  assembly_sccb_final_review_20261030_1218/verification.json
```

Evidence: copied screen normal/-O results; placement_screen/source_junction reproduction; independent_corner.py normal/-O analytic OCC subtraction; native_extra.py for direct counts/outline/additional contracts/source hashes. Reviewer writes only this separate review directory.
