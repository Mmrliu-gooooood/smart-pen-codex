# Candidate hardware unknowns — no selected purchase

Preferred investigation: SC031GS DVP because official driver evidence exists; not a replacement approval and not a claim of end-to-end lower cost. Existing SC035HGS stays separate and cannot use SC031GS mode tables.

| Item | Established public evidence | Missing before any profile or order |
|---|---|---|
| AS-video AS-DGSG8A130D7 | Maker advertises SC031GS MONO RAW DVP,8×8mm PCBA; title180fps/table120fps conflict. | Exact actual-SKU pin1/contact face/connector/pin functions; rail inputs and I/O limits; regulators/level shifting/control behavior; complete body/lens/back components/FPC envelope and tolerances; near-focus RAW; sample MOQ/2-unit tax-inclusive price/availability. 8×8 is NOT complete module volume. |
| CH2035AB | Official lens drawing: SC031GS1/6inch; M5.5×0.2; Ø6×3.67mm,TTL4.35mm; manual focus; MOD5mm; IR650nm filter. | Compatibility with actual module holder/flange; focused total height/locking; MOD reference plane; real paper FOV/corners/distortion/tilt/MTF; two-piece cost. Visible-first possible; not assumed850/940nm future lens. |
| SC031GS chip | Official flyer: DVP8/10/12bit,RAW MONO,640×480; chip rails analog2.8/core1.5/IO1.8V. | Finished module input supply/IO tolerance is NOT chip flyer. No universal3.3V permission. |
| Existing SC035HGS30pin | User identifies sensor; supplier states internal supply conversion and incomplete compatibility statements; no extra internal documents available. | Hidden actual wiring/control roles and measurement. Do not repeat broad vendor schematic request; photo and generic24pin reference cannot close this. |

Sources (public reads, no contact):
- https://www.as-video.com/product/sc031gs-vga-global-exposure-subminiature-structure-180fps-mini-dvp-camera-module.html
- https://www.opticslens.com/uploads/CH2035AB.pdf
- https://smartsens.oss-cn-beijing.aliyuncs.com/web/products/SC031GS_V5.0.pdf
Public pages were inspected2026-10-31. No qualified two-unit camera+lens price was found; no full≤CNY760 calculation is possible. Do not count owned modules/lab labor free or reuse old camera price for a new SKU.

Unpowered first: identity/contact orientation/complete dimensions; disconnected adapter continuity and visible supply/ground paths with safe characterized measurement method. These cannot establish hidden IO tolerance, polarity, PCLK or optical performance. No probing unknown powered FPC, random control toggling or lithium trial.

Only after electrical evidence and separate power authorization: actual rails/startup draw; reset/trigger/isolation behavior; XCLK/PCLK/sync and byte order; exact raw VGA/test pattern; then near-focus/tilt/motion and tip calibration. Current question about available safe setup remains unanswered; no fresh question or vendor contact is needed from this audit.
