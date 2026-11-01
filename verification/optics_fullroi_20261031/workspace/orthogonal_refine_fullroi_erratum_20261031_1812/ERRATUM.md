# Regression-oracle scope correction

Binds frozen `orthogonal_refine_fullroi_candidate_20261031_1806/MANIFEST.json`, SHA256 `3c32b7b5533673e36c757f721b962fc8d1c5b5596f8ce7b430af6eb2f412592b`. Originalsource/results/logs remain unchanged.

Replace the overly broad README wording that all478 “correct” classifications bind a conservative full-dot projected-square support oracle:

- The **70 isolated probe branch** checks returned (x,y) and36direction symbols against the frozen code; its `full_input_support` field is None. Author replay does NOT execute the full-dot support oracle for that branch.
- The **408 historical branch** additionally executes the conservative projected full-dot-square support oracle and forbidden-negative gate. This does not supply a complete fitted transform from the candidate; originalV3 transform-error qualification remains outside this result-only wrapper.
- Any further independent support checks are NEW reviewer evidence and must be attributed separately, not retroactively described as author-run tests.

Acceptance/rejection counts and actualsource behavior are unaffected. Correctsymbol acceptance is not physicaltip accuracy or a general geometric support guarantee.
