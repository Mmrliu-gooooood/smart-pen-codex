# Geometry publication recheck — 2026-10-28

- Source commit: `84476fce1655b299147b2a47089a3f2d25f595de`.
- Parent: `f3baef1a894b75fbf31118c5fffcfeccbcaaabbc`. Source checkout clean.
- Only four source-commit paths are included, plus this recheck and its full log.
- Original upstream checked at `0f8b569176c77dad34aaf83bb008eb118c9f1208`.
- Fresh full host gate: **79 tests passed, zero skips**, 20.416 seconds. Portable C11 checks passed.
- `git diff --check f3baef1 HEAD`: passed.
- Non-failing warning: Starlette TestClient warns that its httpx integration is deprecated.

Command: `python software/verify_host.py --upstream-pc-src <pinned original>/digital_pen_ov5640/pc/src`. Full output is in `axial_tip_geometry_recheck_20261028.log`.

This remains a Python reference geometry model, not target firmware integration or physical pen validation. Camera, radio, physical flash, calibration and true handwriting accuracy remain untested. All NOFAB gates remain.
