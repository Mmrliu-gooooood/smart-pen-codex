# IMU control seven-gap joint routing study — rejected incomplete / READ ONLY

**No native PCB was generated. Parent `pressure_joint_native_0433` remains unchanged, SHA `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`, 0 violations / 113 unconnected / 0 parity. NO FAB / NO POWER.** The two bounded joint topologies below did not connect all seven gaps. Partial geometry is not an acceptable subsystem delivery.

## Exact source and requested scope

`verify_readonly.py` re-reads the actual parent embedded schematic symbols and native physical pads, not PCB's empty pin-function strings:

- R501/R502 are **10k 1%**, each pad1 remains a separate AON island (2 gaps).
- SCL: U101.10 GPIO5 ↔ U501.1 SCL ↔ R501.2 (2 gaps).
- SDA: U101.11 GPIO6 ↔ U501.4 SDA ↔ R502.2 (2 gaps).
- IRQ: U501.12 INT1 ↔ U101.6 GPIO1 (1 gap).
- No new parts, no source/net/footprint/pad/rule modifications. No long routes on In1/In4. GPIO1 copper is not evidence of a working prewake implementation.

Actual firmware `board_provider_absent.c` still returns NULL. `PICKUP_INT_N` is a name, **not an active-low configuration**: LIS2DW12 reset/default push-pull active-high nonlatched behavior must be configured and tested with actual sleep/wake firmware. Retain the existing official ST LIS2DW12 DS11811 Rev9 and TN0018 Rev8 §3.9/3.10 gates. F-body no pour/through-via and central no-track rule remain; necessary outside-pad fanout is not blanket-forbidden.

## Bounded trials and actual blockers

1. **Existing power copper unchanged.** Blind restoration of all 385 objects of the old 9a03 three signal nets produces 135 geometric findings (132 copper, 2 via/pad, 1 drill-spacing). Existing DVP, SENS rail, new pressure and clock routes have priority. New F/In3/B grid attempts fail IRQ and SCL, while SDA's candidate via is rejected by exact finite-copper review. The grid is a conservative planning aid, not a global impossibility proof.
2. **One complete local AON beam reattachment**, no clock or footprint change. Remove only the F AON objects `13079769-348d-5142-9cb4-1d44ec56a7b8` and `fb1700a3-5c27-5c36-9d84-b9492b46b711`. Proposed .25mm F path `(2.65,79.9) → (2.65,79.1) → (5.72,79.1) → (5.72,80.7)` joins the original core via and right-hand supply branch, with zero finite-copper errors. This is **not** the rejected old y79.9 beam through the clock via. IRQ then has a full physical pad graph U101.6↔U501.12 and zero exact geometric errors in the combined partial model. SCL still fails this joint search after that IRQ route. SDA still has a finite-check failure. Thus **the second topology is also rejected**, despite this partial improvement. Plane/core freshfill was deliberately not attempted on an incomplete seven-gap block.

The two pullup attachments have a clear local model but are not published as a native half-finished subsystem. Important correction from the initial quick probe: there is **no existing AON via at (4.35,85.6) in this parent**. Final trial2 extends R502.1 to actual C503.1/core `(4.35,84.5)`; the trial1 short stub to85.6 is incomplete and must not be reused as a core connection. R501.1's new .60/.30 via would still require actual freshfill/core verification.

### Why the top escape problem is not simply a fabricated courtyard ban

With current source copper, F escape pockets for INT1/SCL are approximately x3.0–5.2, y80.6–81.35 in the conservative .025mm model. `exact_escape.json` separately tests actual .45/.20 annuli against all layers, all physical pads **including same-net**, drill and actual native keepout rules. No tested point in that sampled top window is clear. This finite sampling does **not** prove every continuous position impossible.

At `(3.75,80.75)`, actual obstacles include the SENS_VIO In3 conductor at x3.5 and the **back-side J107.1 copper pad**; at `(4,80.75)` EXTCLK also conflicts. J107 is not ignored merely because IMU sits on the other side. Beam movement alone doesn't solve all three escape paths.

SDA's rejected `(2.35,82.65)` via lies at a nominal .15mm tangent to two AON F segments. The 50nm outside polygon approximation detects a tiny overlap; this is not waived, nor misreported as a large physical short. A later plan must choose real clearance margin and pass exact native rules.

## Model provenance / limits

- Grid trials use only F/In3/B. The imported routing model has additional conservative restrictions: .335mm same-net-pad via avoidance, MEMS-body via margin .31mm, right-side via corridor reservation, .012mm central-body screening expansion, and conservative pad rectangles. Trial1 track clearance model=.150mm; trial2=.152mm to avoid numerical tangency. Actual finite review is independent of these model heuristics. A failed search can be false-negative; it is not proof of impossible layout.
- `grid_joint_trial*.json` records the two search outcomes; `trial2_parts.json` contains **partial, non-native model geometry only**. `verify_readonly.py` checks this partial joint model and its actual IRQ pad graph, selected source functions, all seven base gaps, unchanged parent SHA, and absent firmware provider. Normal/-O results agree. That agreement does not validate a complete route or native DRC.
- Search binary/intermediate multi-MB grids are transient and not allowlisted. First and second runs originally reused transient cpp filenames; recorded paths/outcomes remain, but those transient files are **not claimed as immutable replay evidence**. Source scripts are included; compile `grid_astar.cpp` locally if rerunning. Do not modify the frozen evidence folder in place to replay.
- No freshfill, new ERC/DRC, native cuts, native replay or manufacturing qualification was claimed, since no new native candidate met the seven-gap gate.
- Parent pressure's merged BOOT/NIB reference hole (1.341×.951mm), underbody vias, clock/J107 harness/DFM, MEMS stress, battery/charging gates stay open. JP301 OPEN. Unknown camera unpowered.

## Electrical timing still unqualified

Use existing `docs/electronics/imu_i2c_timing_budget`: NXP UM10204 Rev7 Table11/§7.1 gives `tr≈0.8473 Rp Cb`; with 10.1k maximum initial resistance, theoretical total Cb limits are116.85pF at100kHz or35.06pF at400kHz before temperature/age/probe margin. **Actual Cb is unknown**. 100kHz is only a future controlled-test starting point, not a pass. Do not add a battery/MAX bus or new pullup values. IRQ wake polarity, latching/clearing, repeated wake and first-stroke recovery need actual firmware and measurements.

## Proposed next bounded scope (not executed)

A dedicated **joint local three-signal fanout** study should reserve simultaneous escape channels before long routing. If it cannot succeed with this AON reconnection and fixed footprints, request/define a versioned joint IMU/local-cap/J107 placement study preserving complete IMU14 power/ground, actual J107 wire budgets, clock reference, all existing full chains, and realistic MEMS keepouts. Do not keep shuffling the beam or deleting other nets until a grid happens to pass.

## Added local-only domain diagnosis (no further long-route search)

`local_domains.py` evaluates F connectivity **inside explicit small boxes** (MEMS x1..6/y78..84; MCU x.4..5.5/y7.5..13.5), before and after the greedy IRQ, with the complete proposed AON replacement included. It then independently checks suggested .45/.20 vias against actual all-layer finite copper/pads/rules. It is deliberately not another full-board routing trial.

| End | Before greedy IRQ | After greedy IRQ |
|---|---|---|
| U501.12 INT1 | 23 exact-clear sampled ports, common representative(4.7,80.125) | Already occupies that shared port; no independent new port in sample |
| U501.1 SCL | Same23 exact-clear sampled ports | 0 sampled ports |
| U501.4 SDA | 9 exact-clear sampled ports, representative(2.375,82.675) | Same9 |
| U101.6 GPIO1 | Multiple local exits, e.g.(3.275,8.9) | Multiple remaining exits |
| U101.10 GPIO5 | Multiple exits | e.g.(2.575,13.1),(1.55,13.3) remain |
| U101.11 GPIO6 | Multiple exits | Same two representative sites remain, not simultaneous allocation |

**This establishes IRQ-first consumption as a relevant cause of SCL failure**, rather than a fixed pad cutset or proof that IMU must rotate. The INT1/SCL sampled shared port cloud has diameter0.201556mm; two different-net .45mm vias need at least0.600mm center separation for the .15mm copper clearance. Therefore merely swapping the greedy order cannot place two vias **inside this sampled cloud**. A coherent next step is to widen/add a second local escape domain, or find another valid local topology outside this conservative model, before allocating long routes. Continuous global impossibility is not established, because grid/rectangle/extra keepout margins are conservative.

SDA needs only a small modeled dogleg/port displacement candidate from `(2.35,82.65)` to `(2.375,82.675)` (0.03536mm displacement); the latter passes exact via checks. Offending original AON objects at the rejected point are:
- `01e979d6-31d7-5992-84c5-bfd9fd837a3e`, F .25mm `(2.65,82.25)→(3.2375,82.25)`;
- `28c688f6-bde0-5b65-9310-3f46a5f6dd52`, F .25mm `(2.65,81.75)→(2.65,82.25)`.

This shifted **via alone** is not a completed SDA path; exact fanout segments and all simultaneous nets still need testing. Listed candidate ports for different nets are alternatives, not a promise they all fit together. Neither a new firmware wake configuration nor a fabrication file was produced.
