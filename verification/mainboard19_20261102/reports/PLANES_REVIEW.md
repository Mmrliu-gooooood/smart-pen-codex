# R230 final independent planes and actual GND conductor review

Finalcandidate f7632bf6296ba212ec59e54edb1dfdb91995f6f4f071a3d9505b6638f3fbf416 versus acceptedparent1639b8db38415f0466c13334add7cd4bfe6708b0caa232e8b1e79a7044fdf8e7. Narrow static review; NOFAB/NOPOWER. Does not approve R233 or any other candidate. Native DRC/clearance, all-net partitions, raw footprint/move/body contract are separately reviewed.

## Final binding and clean replay
All53 non-PCB project dependencies identical and hashed. Final candidate is independently shown to differ from provisional4ab628 ONLY in J107 B.SilkS usertext"1 EN1", UUID7bdd4403-e4fa-4ba6-b02d-6a4a325e4f85, localcoordinate(-1.18,4.05,0)→(1.2,4.05,0); every other native byte including copper/zones identical. Exactdiff/rebind JSON retained. This is not a blind hash substitution: final actual native is reloaded/refilled and tested in normal,-O and isolatedclean project copies.
Replay /usr/bin/python3 binding.py,audit.py,neck.py,capacitors.py,ground_proof.py,new_endpoint_gaps.py,negative_geometry.py. clean_replay uses own complete project copies/separate KiCad config. Six substantive report pairs compare normal/-O/clean exactly in replay_comparison.json. Native finite geometry50nm (ground graph uses conservative250nm and explicit drill subtraction); GEOS independently verifies holes/area. Native fills unfractured once with area guard. Known barrier/corridor and omitted-hole negatives retained.

## Plane/reference invariants
Both parent and final matched-project refills reproduce native bytes exactly. All three actual planes In1GND/In2AON/In4GND have symmetricdifferencearea0, no added/lost material, unchangedhole counts, oneislandeach. No new vias or inferred antipad changes. All3962 retained track/reference projections have0 positive loss in this native method, including both side references of In3 copper. All36 supply/GND capacitor pads preserve finite connectivity and checked reference projections. No current/IR/thermal claim follows from area equality.

All12 fixed regional corridor brackets unchangedparent: GND→MCU1.9796142578125..1.979736328125mm; GND→U201/U202/U2032.5325927734375..2.53271484375; AON→allfour1.1494140625..1.1495361328125. Explicit source/targets in neck.json; same source window[10.5,82.7,13.2,85.1], includesJ106.2via(11.9,83.9). GEOS64segments/quadrant,15bisections. These are regional plane paths, not actual pad/thermal/barrel ampacity.

## Required actual ground-conductor proof
New ground connection uses OLDvia ba18b306-28c3-5779-ae4b-c94f55c9ad42 at(1.5,33.725); removed old1.1mmGNDleaf leaves OLDvia74ea5a95-f920-42ac-8f11-46f056a91d64 at(11.1,32.325) present.
Finite graph explicitly intersects physical pad/track/via-annulus/filled-zone shapes across layers. Via drill discs are subtracted; it does NOT connect objects just because their net names match. Both targetvias and R230groundpad are in the same finite component with U101.57 coreground witnesses (full list in ground_proof.json). Each targetvia annulus intersects actual In1 and In4 single-ground-plane copper by0.12742847897mm² perplane. This separately confirms actual contact with the filled ground core, not merely equalGND labels.
Negativefixture keeps GND names and targetvia marker identities but replaces targetvia finite shapes byempty: each target disconnects fromR230. Graph correctly rejects name-only connectivity. Shared via object models plated barrel interlayer connectivity; no barrel manufacturing/ampacity or IR qualification implied.

## All eight new B tracks and endpoint reference
New GND B union2.0081526480585mm² is entirely referenced byactualIn4 GND, uncovered0.
New SENS_D6 B union0.6505395077215mm² has uncovered0.10908327511mm². Do not sum overlapping individual segment gaps0.0742236446265+0.05662880494: finite union is the stated smaller value. The two approach segments not touching the sourcevia have0 uncovered.
Allgap vertices lie within0.378740706281mm of SAMEoldSENS_D6via(3.725,39.3). Subtracting ownvia copper+.1505mm leaves0.0001973691655mm², maxvertexdistancebeyondviacopper.153740706281mm. These positive native polygon-edge residuals are retained, not calledzero; no distant foreign-antipad or midspan primary-ground gap found. Parentfilledplanes identical, so gaps arise from new track projection over existing local sourcevia aperture, not destroyed old plane material. ExactsourceUUIDs/coordinates/polygons saved.

Preserve NOFAB/NOPOWER and unqualified stack/SI/PDN/current conditions. No body clearance, completeCAMBUS or other route approval is implied by this plane/GND-only review.
