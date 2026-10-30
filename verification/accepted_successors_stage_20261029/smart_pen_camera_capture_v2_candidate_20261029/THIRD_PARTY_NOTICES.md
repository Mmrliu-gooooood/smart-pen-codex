# Public-source and frozen-header notices

- `third_party/esp32-camera` is the official Espressif repository at
  `f37e65608f709bd94846dee01d947f02ae07c0b0`, with only the differences recorded in
  `verification/esp32-camera.patch`. Its original root `LICENSE` (Apache-2.0)
  and all per-file notices are retained. Files derived from OpenMV retain their
  MIT notices; the MIT permission text is included below. This candidate's
  minimal component wrapper only supports IDF5.4/new SCCB/ESP32-S3/SC031GS.
- `frozen/` contains byte-identical header dependencies from the user's existing
  `smart_pen_app_pipeline_20261028/firmware`; hashes and paths are listed in
  `verification/frozen_headers.json`. No broader ownership/license claim is made.
- No private vendor datasheet, INI/register table, drawing, photograph or video
  is included. Public Espressif SC031GS tables are not the user's private SC035HGS files.

## MIT notice for OpenMV-derived files

Copyright (c) 2013/2014 Ibrahim Abdelkader <i.abdalkader@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## v2 local test provenance

The driver-chain/HAL/backend/core-extended tests and narrow driver stubs were
adapted from the locally produced `smart_pen_camera_capture_review_20261029`
review fixtures, then independently run for this v2 implementation. No claim
of a completed independent v2 review is made.
