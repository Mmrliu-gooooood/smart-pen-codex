# V3 comparison verification-scope correction

Supersedes only README_ZH.md paragraph containing “workspace边界按回放脚本核查” in frozen `optics_v3_comparison_20261031_1759`, MANIFEST SHA256 `3e1b8b27b3862985b93d994eefcc6eabfd32ed7a885712cc5a5c779296a01bcc`.

Replacement: the70-image replay checks workspace/result **ABI sizes and allocation sizes** (32640B/192B). It does NOT install workspace canary guards, perform a dedicated bounds-memory proof, or run sanitizers. Direct-vs-trace outputs and failure-result unchanged checks do not establish absence of out-of-bounds writes. The separate quick13 tests have their own declared scope and must not be silently attributed to the70-image replay.

Per-image counts, bytes and all frozen logs are unchanged. No new memory-safety qualification is claimed. Subsequent implementation must add explicit guarded-buffer and sanitizer tests where supported, separately recording executed scope.
