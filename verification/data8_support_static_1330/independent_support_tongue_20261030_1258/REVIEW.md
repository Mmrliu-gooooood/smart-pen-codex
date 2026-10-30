# Independent raised-tongue support review

**ACCEPT the raised-tongue corrected_connected derivative at bounded nominal geometry scope. NOT strength, material, preload, printability, actual tool/FPC insertion or process qualification. NOFAB / NO POWER.**

Frozen package manifest130116eb486947539c3ea2e61a9c8b6e84f1b1ff0bc00bc9eb3c690952861605. Only three corrected_connected FCStd/STEP candidates are reviewed; earlier zero-J202-margin proposal is a rejected diagnostic, not an interchangeable accepted option. Baseline is previously reviewed exact dcbd14×99.8mm stepped board/.93mm thickness budget, at unchanged electrical datum.

## Independent saved-CAD findings

Reviewer independently reopens author FCStd, derives coincident full head/board face areas and whole-part J202 distances:
- All three head contacts **.8mm²**, distance0 and no positive solid intersection.
- Each changed base/lower has **.20000000000000018mm** gap to retained full J202 operating envelope.
- Seven changed parts total: valid and single-solid; unchanged saved geometry outside these parts verified, including board+104full installation solids. Six operation Evidence records exactly equal baseline.
- Earlier corrected-connected proposal's actual base/lower gives0mm J202 gap and fails the same≥.2mm acceptance predicate. This is an explicit negative control, without moving/shrinking J202 or board.

## Reproduction and retained interfaces

Independent normal and -O rebuilds reproduce geometric validity, collision and contact outcomes; serialized FCStd hashes naturally differ because saves embed document metadata, so geometry/result comparisons exclude only regenerated candidate file hashes. Frozen originals remain unchanged.

Root overlap is positive:.242mm³ each ACCESS tongue and1.32mm³ bench tongue. All modified parts remain one solid, not floating extensions. Three-context tests find no positive-volume intersection of changed parts with board/full installations or other mechanics. All7×104 whole-part distance checks find no touching installation envelopes.

ACCESS RF lateral finger relocates Z131→119, restoring edge distance0 with no positive board volume intersection. Added secondary catch remains.1mm recessed with.5mm² projected footprint; old structural catch material is preserved. Three primary B contact patches remain.5mm² each, tail toe0 gap. Final front tool and two anchor-channel diagnostic cylinder intersections remain0 before/after. Six operation gates unchanged; these limited channel tests are not physical service qualification.

Free, installed.83/.93 and stop retainer states remain single valid solids and preserve source-state volumes; only intended lateral station relocates. No stiffness/preload/fatigue or dynamic/insertion force claim follows from this geometry.

STEP reopens valid, solidcounts bench164 and ACCESS137 each, residuals approximately−.000005793/−.001299177/−.001082523mm³, within explicit.005mm³ exchange bound. Native BRep determines contact—not STEP tolerance.

## Remaining gates

.2mm J202 separation is nominal exploratory clearance, not a tolerance stack or demonstrated FPC/tool envelope. Inherited ACCESS19 upper-cover/C103 gap.0679812684mm (ACCESS20.5679812684mm) remains unchanged but process-sensitive. Actual materials, print orientation/strength/root stress, assembly tolerance, preload/contact loads, release/tool access, cable insertion/bend, solder/strain-relief and cell qualification remain open. Historical OD19/20 contexts do not qualify15–18mm pen target.97 modeled static refs/104solids plus6operations is103 accounted contracts, not103 qualified installations. No global assembly/electrical safety or powering permission.

## Frozen artifacts SHA256

```
130116eb486947539c3ea2e61a9c8b6e84f1b1ff0bc00bc9eb3c690952861605  assembly_support_tongue_variant_20261030_1251/manifest.json
839adf79c161073fdfa18f6e74e58e81f8d5a8698461ad00c84e8f30faa0ce83  assembly_support_tongue_variant_20261030_1251/README.md
6b2084e0a0126a74a0e256517760e0f1bc9885e340daf99c7bdc2e4372aaf7e0  assembly_support_tongue_variant_20261030_1251/check_inherited_margin.py
c49331935ed31c8facb5839a8f7544edaef928bc95a9b209e6137951065feaf3  assembly_support_tongue_variant_20261030_1251/check_preservation.py
2687a6f378b404d757462976290f0bb32927c1028af4e348ca0ca985ea5ccad8  assembly_support_tongue_variant_20261030_1251/check_preserved_interfaces.py
74859273a1a5ea19994589ed882083ae10aac30336c569b1c0447fe354988467  assembly_support_tongue_variant_20261030_1251/clearances.py
627ab3c0dcbf04bf2e418aca073dce2523f58bd8d64d97542226cbbf3ea1edb1  assembly_support_tongue_variant_20261030_1251/patch_supports.py
04a90f1b6e44d44a8d72490eddc2c64dce335eca3acaae0b99093edd6129efea  assembly_support_tongue_variant_20261030_1251/test_contacts.py
6a6fe6b76e4457577f82b267cb91dba10528d1baa0c92dd2513fa173e1ce6209  assembly_support_tongue_variant_20261030_1251/test_exact_contexts.py
69c8c5a95c5e14d9608c464c01e0fec8afd06ea3bdded84c43a2c671778bc025  assembly_support_tongue_variant_20261030_1251/verify_results.py
c41e308d933d53d88b5c99a283525a47666ee93c3219790e6415723a839577b3  assembly_support_tongue_variant_20261030_1251/corrected_connected/ACCESS19_support_proposal_NOFAB.FCStd
bee72b10fed37b4f91a06662767ad9e83f2b92598f7aefb9a4ae680e9ab1b763  assembly_support_tongue_variant_20261030_1251/corrected_connected/ACCESS19_support_proposal_NOFAB.step
a342ef61f47b1445c002c7786ca3881f2aac872f6f45d1c8c32b6487e7637ddb  assembly_support_tongue_variant_20261030_1251/corrected_connected/ACCESS20_support_proposal_NOFAB.FCStd
43e87b975c92435ae12667e42f6ae43eb1a534759ff667882c33eab411297184  assembly_support_tongue_variant_20261030_1251/corrected_connected/ACCESS20_support_proposal_NOFAB.step
6d19f324779712aad1913a5d6513141d426bfdcc98deccacff08e32ea0e713b0  assembly_support_tongue_variant_20261030_1251/corrected_connected/RevD_BENCH_support_proposal_NOFAB.FCStd
31764cad53e0387fa9f04c8021e1e1fda00c95da2ac6270be6d61e7c75215d7f  assembly_support_tongue_variant_20261030_1251/corrected_connected/RevD_BENCH_support_proposal_NOFAB.step
8c31fd978337a480879d0a88ee3345ae8cf8cb213c177f256ef8e8f5df44a4ee  assembly_support_tongue_variant_20261030_1251/corrected_connected/contact_results.json
7c944252108074a62d65c221992da36ca52fb1ed0f7af34b139e0a09c992c177  assembly_support_tongue_variant_20261030_1251/corrected_connected/exact_context_tests.json
56c3ae7ebaa68a93239262ff6c762c327c524179b257e5ffdb8b7c9fa65ac52f  assembly_support_tongue_variant_20261030_1251/corrected_connected/preservation.json
```

Evidence: independently reopened saved CAD/negative test in independent_saved.py/json; normal rebuilds/contact/preservation/interface/clearance checks; separate sibling optimized replay; normalized result comparison; unchanged frozen hashes.
