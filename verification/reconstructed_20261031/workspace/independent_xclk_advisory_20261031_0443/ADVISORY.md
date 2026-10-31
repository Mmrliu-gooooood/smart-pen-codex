# XCLK independent PDN/reference/clock advisory — NOT full acceptance

Pinned initial653a18e7c789027d58f7ab387965d47cf183de0445edb60ed6111700caecc920, then selected **6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08**, against accepted5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433. Own PCB/project snapshots taken before analysis. Selected_delta.json proves exactly three old/three new XCLK F-track replacements for y6.15→6.11 north margin change; all other tracks/vias exact and **all actual filled-plane contour vertices identical**. Retained-loss and new-hole classifications are exactly unchanged. No author files edited.

## Disposition
Proceed to full frozen static review with explicit plane-current-spreading and clock-loading gates. No disconnected actual supply-core/island blocker found. Old power copper preservation does **not** establish unchanged PDN: the adopted driver-side In2 crossing removes a broad right-side AON passage. This is a real geometry trade, not automatically prohibited by a manufacturer zero-projection rule. No fabrication, power, SI, capture, clock-operation or process acceptance is given.

## Actual powered nodes and In2 feed geometry
Independent finite graph retains **AON41/GND94/SENS_VIO12**, including supply entry and current powered pads. AON In2 remains one mainland; current AON-via membership unchanged, inherited(11.9,83.9) outside-plane condition retained. No AON via center lies in removed plane copper. All old GND/AON/VIO tracks/vias, footprints/poses/values and C104 copper are exact.

AON area845.1393417019→840.6893295428mm². Native Boolean loss **4.8955253860mm²**, gain **.4455133025mm²**, net about−4.45001216mm². New clock route cuts right-side spreading through y≈51.05..51.50. At y51.275, baseline filled x intervals are .5..4.973699 and5.076299..11.5; selected leaves only **.5..4.406095**. Across measured y51.05..51.50 the left bridge remains about3.681..4.156mm wide. These exact polygon cross-sections characterize a surviving passage, not a globally proven minimum neck or current/impedance acceptance limit.

Constructive existing-plane corridors were tested between **actual AON vias(9.575,42.2375)** serving U202.1/C203.1 and **(9.575,52.0375)** serving U203.1/2/C205.1. On a bounded .25mm visibility grid spanning x.75..12.25,y40..56, zero-uncovered .3/.5mm corridors exist:
- Baseline10.271039/11.467520mm.
- Selected19.030633/19.237740mm, bypassing the clock clearance on the left and other pre-existing holes below it.
These are constructive filled corridors, not actual current trajectories, globally shortest routes, inductance or prescribed manufacturing widths. A smaller initial search window failed because it excluded the lower detour; that was not an electrical disconnection. Preserve this spreading-path penalty in PDN/transient validation; single-island membership alone is insufficient.

C104 direct supply/GND-return copper and all tested nearest/farther ground corridors are unchanged. Most local C104 AON corridor diagnostics are unchanged; a north .5mm diagnostic improves its already-uncovered area by .0040557111mm² after old source-via changes, and another north diagnostic differs only at≈1e−8mm² Boolean scale. No new C104 return penalty or global PDN-equivalence claim is inferred.

## Retained and new reference attribution
Own **2942 retained projections** find six reports, all **secondary In2AON** below retained In3 conductors:
- CAM_SCL andCAM_SDA .06765mm² each.
- Four overlapping SENS_VIO1V8 segments: individual .019080932666,.1586881258025,.014371471156,.0007338311715mm²; **union-before-subtraction .1690055798825mm²**, not their sum.
No retained dominant-GND projection loss is reported. In3's dominant adjacent ground is In4; In2AON is separately disclosed, not called ground. VIO is a supply conductor: retaining its copper and dominant reference does not waive altered mutual coupling/current spreading from the adjacent AON slot.

Five separate matched-project counterfactuals on653 (NONE, In2tracks, leftvia, rightvia, allnewvias) each verify exact prefill. Removing **only the new In2 clock tracks** restores every major reported patch; removing any/all new vias restores none. NONE restores none. Selected688 matched NONE and In2-track removals repeat the result; exact filled-contour equality justifies transfer of the other causes. Thus this is a **track-clearance slot**, not own-via-only attribution. Small Boolean-order differences on VIO first/last segments (≈3e−9 and4e−10mm²) are retained in outputs; no threshold expansion or global-zero claim. Deleted counterfactual circuits are diagnostics, not candidate repairs.

New XCLK foreign-only dominant-ground hole unions: **In2→In1 .000006444921mm²** at the merged SENS_HREF/VSYNC/PCLK via hole; **In3→In4 .000016321852mm²**, two8.160926e−6 grazes at AONvia(10.325,21) and ILLUM_STROBEvia(10.25,9.8). New F/B clock and rerouted SCCB/CAM_IO_EN rows have no foreign-only union in this test. All reported new uncovered projections lie in actual holes, not outside filled-plane boundaries. Shared own/foreign holes remain coupling conditions, not harmlessness proofs.

## Clock path, bias branch and domain
Actual intended route: **U101 SiP43 GPIO38/VDD3P3_CPU→U203.4(1A1)**, DIRpins2/3 high on AON, VCCA1=AON3.3, VCCB16=SENS_VIO1.8, OE14/15=CAM_ISO_OE_N. U203.13(1B1) drives existing SENS_EXTCLK toJ202.18. R221 is physically B.Cu-mounted100k bias on the **3.3V A-input net**, not a B-port1.8V load simply because of board side. Actual mux excludes unintended FSPIWP/SUBSPIWP ownership. Intended clock generation is peripheral/push-pull output, not borrowed SCCB open-drain configuration. [TI AXC4T245](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), [Espressif PICO-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf).

Own selected terminal centerline geometry:
- MCU43→U203.4 **63.8877969365mm,5 layer changes**, initial65363.8125446717 (+.0752522648mm).
- U203.4→R221.1 **13.0759776311mm**, not pure branch length.
- Actual **unshared R221 arm7.5134776311mm**, verified articulation at sharedvia(3.4,50.5); branch includes a private via and high-resistance load, not matched termination.
- Existing separate buffered output U203.13→J202.18 **47.9419586060mm,3 changes**, unchanged.
The graph uses same-layer centerline intersections and short via-center connectors; vertical barrel delay excluded. Do not substitute the separately labeled finite-contact shortcut metric for these centerline numbers. Nor sum input/output lengths as one unbuffered line or directly length-match XCLK to PCLK: an unknown sensor generates returned PCLK/data from its reference clock, with unknown phase/ratio/timing.

## Startup, frequency and waveform gates
**No sensor vendor/frequency is established;20MHz is NOT presumed valid.** Required before operation: identify sensor and its XCLK voltage/frequency/duty/high-low-width/jitter/startup/reset requirements; select actual firmware clock source/divider and quantify achievable error; inspect bootloader/application GPIO38 mux/drive/idle state; sequence clock/OE/rails/reset per that sensor without runt pulses; verify loaded MCU VOH/VOL into U203 A input and U2031.8V output versus sensor VIH/VIL over rails/load/PVT, overshoot/undershoot, branch ringing and translated pulse/duty distortion. Buffer propagation and return capture timing remain unqualified. Unknown frame rate does not waive fast-edge analysis.

Official GPIO guidance warns startup code can alter default configuration: [ESP-IDF GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html). The generic esp32-camera target/xclk.c uses configurable LEDC, but the **S3-specific driver overrides XCLK through LCD_CAM**: [official S3 ll_cam.c](https://raw.githubusercontent.com/espressif/esp32-camera/master/target/esp32s3/ll_cam.c). Neither source proves this board's actual firmware configuration or a safe default frequency. Pin the eventual firmware revision and sensor contract; do not treat a moving master example as qualification.

## Actionable bounded disposition
The surviving broad left passage and tested actual-anchor bypass support continued bounded static review, not a demand to eliminate every secondary-plane overlap. If PDN/clock waveform evidence later rejects the detour, investigate a locally checked alternate crossing/return attachment preserving a direct AON bridge; no such repair is preapproved here and no added stitch is assumed feasible. Re-run whole-net finite/current-core/reference/mechanical checks for any change. The north F-only margin successor is the selected exact specimen; filled-plane evidence is unchanged.

NOFAB / NO POWER / providerNULL / JP201/JP202/JP301 OPEN. No remote/source edits; eventual full acceptance requires immutable author and independent native/physical/negative/replay/mechanical review.
