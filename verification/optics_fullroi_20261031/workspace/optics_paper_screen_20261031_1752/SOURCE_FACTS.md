# Verified source facts (primary repository code)

Source repository `publication_20261031/target_repo`, published reviewed commit `f92911bc8f8eac4ea02ad2cb0044f60da193151a` (root confirms publication; remote finalcheck belongs uploader). Relative code citations below bind the source, not unverified external sensor facts.

- `firmware/application_idf/main/CMakeLists.txt:3` links roi_opt; `firmware/application/pipeline.c:62–63` calls with priorNULL, so active operation is cold search.
- `firmware/vision/roi_opt.c:136–139`: input16..256; `:53`:≥36 components; `:107–118`: complete observed6×6. `:155–157`: pitch8..32 step.5, angle−60..60 step2, ratio.6..1.4 step.1.
- Same `:88–92`: final normalized major.10..30/minor≤.065, ideal1/6 score. `:22,43–53`: contrast≥60, speckles<3 pixels discarded; edge-touch/area>100/aspect>2 and >128 components reject.
- `firmware/vision/roi_opt.h:30–33`: orthogonal nonuniform, not general affine/shear/homography; angle is image-plane rotation, not physical tilt qualification.
- `verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029/firmware/vision/roi_continuous.c:61–76`: input96..256, central96 crop,80 only if retained count>100; <36 reject, no decode-failure alternate crop. Header`:4–13,40–43`:36..100dots/no resizing/evidence outsidecrop ignored.
- V3 same directory `roi_opt.c:99–111`: relaxed seed limits not final residual contract. `:194–224`:≤5 orthogonal refinement iterations, same search bounds, no projective model.
- `verification/continuous_v3_experiments_20261029/README_ZH.md:9–18`: fractionalFOV36/36, rotation76/96;20 missing-complete-window rejections remain finite synthetic evidence.
- `verification/tilt_projective_experiment_20261030/README_ZH.md:3–9`: V4 NOT_ADOPTED;3quality-contract violations, no replacement of V3/application.
- `verification/reconstructed_20261031/optics/CORRECTIVE_OVERLAY_ZH.md` and `CODESIGN_VALIDATION_ZH.md`: user-corrected paper/optics co-design precedence, visible-first then separateIR gates. Neither historical.3mm/5–7mm nor current testpaper values freeze finalgeometry.

No Internet-derived sensor/model/availability claim is used in this screen; all physical camera/lens properties remain variables or unknowns. SOURCE_HASHES.json binds exact inspected source bytes. Model equations are declared ideal pinhole assumptions, not measured device properties.
