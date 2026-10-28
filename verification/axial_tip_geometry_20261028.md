# Axial tip reference verification — 2026-10-28

Baseline: `f3baef1a894b75fbf31118c5fffcfeccbcaaabbc`.

- Focused geometry discovery: **15 tests PASS**, including 8 unchanged rigid-tip tests.
- Full `software/verify_host.py --upstream-pc-src <original pc/src>` gate:
  **79 tests PASS, 0 skips**; portable C11 checks PASS. Final run: 23.366 s.
- `git diff --check`: PASS.
- Reused prepared host virtualenv and original upstream `digital_pen_ov5640/pc/src`.
- New seeded tests exercise 200 compound rigid rotations with an oblique axis,
  signed travel, both plane orientations, closed bounds, no clamping, D1 ideal
  lateral projections, malformed/nonfinite/overflow inputs and fail-closed cases.

This is Python reference algebra only. No target-firmware implementation or
integration was added. No real pose/calibration/contact-travel measurements,
radio/camera/physical flash, flex/play qualification or system accuracy evidence
is implied. Existing hardware and release gates remain unchanged.
