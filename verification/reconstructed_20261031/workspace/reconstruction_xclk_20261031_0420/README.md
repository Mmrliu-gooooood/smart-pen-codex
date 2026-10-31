# XCLK two-closure research candidate — NOFAB / NO POWER

## Exact selected artifact
- `final_candidate/mainboard_revD.kicad_pcb`: **6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08**.
- Parent accepted5f: **5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433**, actual0/43/0. Parent private checkpoint was roundtrip verified before this NEW stage.
- Fresh KiCad9.0.2 all-track/schematic-parity DRC: **0/41/0**. This is a bounded static candidate for independent review, not clock, capture, SI, PDN, assembly or fabrication approval.

Only CAM_XCLK merges: `[U101.43]`, `[U203.4]`, `[R221.1]` become one physical component. Every other pad partition is unchanged, including all eight data, SCCB and three receive MCU links; cores remain GND94/AON41/SENS_VIO12. All103 footprint/pad/value/pose contracts, full104 budgets, actual14×99.8mm outline/fullRF, stackup and design rules remain unchanged. No pre-existing GND/AON/VIO copper or USB geometry changed. **This does not mean unchanged PDN: new In2 signal clearance changes AON plane material/current spreading.** JP201/202/301 remain OPEN; providerNULL; no physical power or sensor attachment.

## Circuit and exact copper scope
U101 SiP43 is GPIO38/VDD3P3_CPU, intended peripheral push-pull clock output. U203 is SN74AXC4T245PWR: DIR2/3=AON, VCCA1=AON3.3, VCCB16=SENS_VIO1.8, OE14/15=CAM_ISO_OE_N. Enabled direction is A→B: pin4 1A1 input to pin13 1B1 output. R221 is **physically B.Cu-mounted100k1% bias on the MCU-output/U203 A-input net**, not a translator B-port load. The inherited separately buffered SENS_EXTCLK core already joins U203.13/J202.18; R235 remains isolated.

Added259 tracks/6 through-vias; removed76 old tracks/1 old via. Every retained old copper object is exact. All new signals .15mm, all new vias .45/.20; no hidden FineSignal127 rule lowering, microvia or filled/capped-hole assumption.

| Net | Removed conductor | Added conductor | Interpretation |
|---|---:|---:|---|
| CAM_XCLK | none |71.4115667874mm total,207 tracks/6vias|Includes main route and bias network, not one endpoint length|
| CAM_SCL |9.7000776800mm F|10.4746183625mm F|North source reroute, +.7745406825mm; entire original pad core restored|
| CAM_SDA |10.4759706598mm F|11.1882939922mm F|North source reroute, +.7123233324mm; entire original pad core restored|
| CAM_IO_EN |4.8318199525mm F/In3 plus one via|4.1482097069mm B|Existing sourcevia6.875/5.775 joins existing B trunk through7/6.1→10.8/6.1. R107100k original pad-to-via branch explicitly retained; all three terminals remain connected|

New clock layers: F19.2527572757mm, B9.5538582233mm, In3 33.4043416229mm, **In2 9.2006096654mm**. In2 use is confined to the declared driver-side window x3..13.4/y49.8..52.2. Native `copper_metrics.json` and `final_verification.json` give exact UUIDs/coordinates. 142 clock segments are under.05mm and168 under.1mm; minimum.025mm. Exact integer collinear-adjacency screen finds zero mergeable pairs. No non-collinear smoothing was used to hide clearance/reference changes; inherited duplicate geometry elsewhere is not a claim of global uniqueness.

## Actual clock geometry — not timing qualification
Primary `clock_centerline.json` and independent branch articulation:
- MCU43→U203.4 **63.8877969365mm, five layer changes**.
- U203.4→R221.1 **13.0759776311mm**, not the pure branch length.
- **True unshared R221 arm7.5134776311mm**, branching at shared via(3.4,50.5), with one private via and100k load, not matched termination.
- Inherited separate U203.13→J202.18 output **47.9419586060mm/three changes**, unchanged.

Vertical barrel delay is excluded. Do not sum input/output as one unbuffered line or match XCLK length directly to returned PCLK. Unknown sensor phase/ratio/setup/hold and clock conversion remain open. Earlier finite-contact shortcut graph diagnostics give a different shorter geometric metric and are excluded from the frozen allowlist; they are not substituted for these nominal centerline numbers.

## PDN/reference trade — real and explicit
Independent selected688 advisory `../independent_xclk_advisory_20261031_0443`, manifest **4c67af04e881ea1d51d14e52d6d2931f6140e5e5049d7124b01fe032bbc2181f** (63files), is bound in `advisory_dependencies.json`.
- AON In2 stays one mainland with unchanged current-via membership and physical AON41 core. Its area845.1393417019→840.6893295428mm²; loss4.8955253860/gain.4455133025mm², net−4.45001216mm².
- Right-side AON spreading near y51.05..51.50 is cut. At y51.275 only x.5..4.406095 remains versus two broad baseline intervals. Measured left passage3.681..4.156mm is a cross-section, not a global minimum-neck or current limit.
- Constructive actual-anchor .3/.5mm filled corridors from AONvia9.575/42.2375 to9.575/52.0375 lengthen from10.271039/11.467520 to19.030633/19.237740mm. These are geometric bypasses, not actual current trajectories/impedance qualification. C104 copper and tested ground-return corridors are unchanged.
-2942 retained projections: six reports, all secondary In2AON under In3. CAM_SCL/SDA .06765mm² each; overlapping VIO reports have independent union-before-subtraction .1690055798825mm², not their sum. No retained dominant-GND loss is reported by this model. Matched counterfactuals attribute these to **new In2 tracks**, not own-via-only holes. Boolean-order differences of roughly3e−9/4e−10mm² remain disclosed.
- New XCLK foreign-only dominant-ground hole unions: In2→In1 .000006444921mm²; In3→In4 .000016321852mm². Shared-hole coupling remains an engineering condition; no invented both-plane-zero criterion or harmlessness proof.

## Full-body and process margins
Independent exact688 whole screen: no NEW nonterminal full-body/Fab intrusion, all six vias outside full bodies/Fab, explicit native keepouts clear. Only five actual pad-ended escapes: U10143/44/45,U2034,R2211. Ordinary courtyard passages are separately enumerated by mechanics, not blanket assembly approval.

A bounded north refinement replaces three XCLK F tracks, y6.15→6.11. Full U1017.5mm installation-budget gap improves .025→**.065mm**; nominal gap to the datasheet maximum7.1mm physical body is .265mm. This is not manufacturing tolerance qualification or permission to shrink the full budget. Coordinated SCL shift failed SDA clearance; y6.10 clock trial failed finite clearance; neither was adopted. All filled-plane contour vertices are exactly unchanged653→688. Other explicit nominal via/full gaps remain R221 .15mm, R232 .188823634mm and U101 .2mm. No uniform.2mm margin claim, supplier tenting/filling approval or qualified operation/tool envelope is inferred. Saved CAD remains earlier d855-bound but geometrically applicable because all poses/budgets are unchanged; it is not silently relabeled a new saved CAD version.

## Bounded search and validation
Initial three north route orders and driver searches were finite-grid studies, not global impossibility proofs. A source CAM_IO_EN replacement freed the joint source corridor without power or pose changes. Local R221/U203 join was routed before the long clock trunk. Driver connected-component evidence touched early artificial Y boundaries; ordinary layers were expanded to the actual tail before a bounded In2 crossing was evaluated. `boundary_flag_regression.py` makes this warning explicit; no-touch still is not a continuous/global proof. An initial IO_EN diagnostic accidentally disconnected R107 and was rejected by the all-net physical prefilter, then corrected before this selected topology.

Final evidence:310 native/physical checks normal/-O; finite265 added objects;23 source-role checks; six actual PCB_TRACK-wrapped-via regression fixtures; all103/full104 geometry contracts; fresh0/41/0 and byte-identical normal/-O refill; six physical cuts normal/-O; twelve saved-project negative DRCs; exact raw replay/inverse. Cuts0..4 each produce1/42/0 track-dangling; IO_EN bridge cut5 correctly produces2/42/0 (via+track dangling). Intentional negative fixtures are not adoptable boards. Rejected, unselected and planning native boards/UI/cache files are excluded from the frozen allowlist.

## Mandatory unresolved gates
Actual sensor identity/clock voltage/frequency/duty/high-low widths/jitter/startup/reset, firmware revision/source/divider/mux/drive/idle/bootloader behavior, loaded MCU/buffer VOH/VOL and pulse distortion/overshoot/ringing, dynamic OE/rail/reset ordering, AON transient/current-spreading validation, SCCB RC/load/JTAG/open-drain/VOL, GPIO42 CAM_IO_EN debug ownership, manufacturing stackup/impedance/tenting and actual physical assembly remain unqualified. **No20MHz presumption.** Current41 unconnected items and unknown sensor-side/power/control work remain; count reduction is not functional capture.

Primary sources: [TI AXC4T245 SCES877B](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), [PICO-1 v1.2](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf), [ESP-IDF GPIO startup warning](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html), [official S3-specific LCD_CAM clock implementation](https://raw.githubusercontent.com/espressif/esp32-camera/master/target/esp32s3/ll_cam.c). Generic LEDC code alone does not establish selected S3 firmware behavior; moving master is not a pinned production firmware contract.
