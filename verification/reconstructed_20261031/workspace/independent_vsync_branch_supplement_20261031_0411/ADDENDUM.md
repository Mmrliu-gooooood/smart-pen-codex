# VSYNC advisory correction and actual unshared bias arm

Exact candidate **5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433**, unchanged. This separate supplement corrects/extends frozen0357 advisory manifest ce2793ff59040c00a5251af6eae98cde28609c97b1d8a081db2cfe2b372fad1f; that package is not edited. **Advisory only, no full acceptance.**

## Layer correction
The frozen ADVISORY source-loss bullet incorrectly calls PCLK/HREF tracks F/In1. Actual native UUIDs **c38d278c-7993-48f5-8f50-9015d1a9bfef** (PCLK) and **14953b42-2271-42fb-8b2f-59304193614f** (HREF) are **In2.Cu→adjacent In1.Cu GND**, not F.Cu. Their losses .0007125011615/.000661924169mm² and attribution to new VSYNC source via(6.4,14.9) are unchanged. Original native/reference JSON was correct; this corrects prose only. In2 is the mixed-AON layer occupied by these retained signal tracks, not a ground plane.

## Actual unshared R219 arm
Rebuilt the actual centerline/via-connector graph and inspected node paths, rather than relying solely on the three-distance formula. The R219 path first meets the U202.5↔U101.22 functional trunk at **In3.Cu(11.25,28.9)**, the shared VSYNC through-via **2de832fa-7f74-4a4c-9613-977a6a4e8f09**. After contracting coincident zero-length vertices, removal of this junction separates R219 from **both** functional terminals: the junction is an articulation, not an arbitrary point chosen from overlapping shortest paths.

The actual unshared bias arm from **R219.1 B.Cu(5.375,39.5)** to that junction is **19.5453584876mm planar centerline**. It runs B.Cu→its private via **93472d3d-4116-4706-9c37-1fe35256b7a2 at(3.875,38.275)**→In3.Cu→shared junction. Thus **one private layer transition**, excluding the shared junction's vertical barrel and all vertical electrical delay. Full node sequence is recorded in branch.json.

The earlier **40.9704983539mm U202.5→R219.1** includes shared functional-trunk routing and is not the unshared arm. U101.22→U202.5 is40.7814164962mm; U101.22→R219.1 is38.9016351176mm. The derived tree-distance arm19.5453584876 agrees with the direct graph measurement, but the graph/articulation test is the evidence establishing the branch. Total network conductor length must likewise not be called branch length.

This is a roughly19.55mm high-resistance-loaded side branch ending in the existing **100kΩ** bias resistor, not a resistively matched termination or a literal open circuit. Its capacitance, via discontinuity and reflections/coupling can affect the functional VSYNC edge. Actual driver rise/fall, stackup, receiver thresholds and branch loading must be modeled/measured before timing or signal-integrity acceptance; no universal length limit or reflection magnitude is invented. The bounded shorter-junction trial's specific PCLK/GND collisions do not prove global impossibility, but this supplement requests no new geometry or research.

## Precision clarification retained
D3 loss uses overlapping track UUIDs. Independent union-before-subtraction≈2.07732665e−5mm² per plane; author union-after-subtraction≈2.07766905e−5mm². D6 individual9.163e−9, independent union-first1.44525e−8, author post-union0 reflect operation-order precision, not a newly demonstrated physical zero. Earlier matched-NONE D3 Boolean floor remains explicit. These are geometry diagnostics, not calibrated electrical tolerances.

NOFAB / NO POWER / providerNULL / JP201/202/JP301 OPEN. No source/native/frozen-advisory changes. Full acceptance awaits the immutable author package and independent review.
