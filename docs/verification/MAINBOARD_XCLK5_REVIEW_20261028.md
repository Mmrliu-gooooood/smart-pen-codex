# XCLK5 independent connection review

Date: 2026-10-28 UTC. **NOFAB / incomplete board / no clock-frequency qualification.** No new misconnection found within this review's scope. Only the frozen snapshot and explicitly pinned dependencies were read; the moving HREF successor was not reviewed.

## Snapshot and native checks

All **49 manifest entries** and every listed dependency hash matched.

- PCB: `9f9937d894fa52d63c5edebd29d10a9396d6f8463819d4a3714fa2724c9bed49`
- Root schematic: `802118fe50cd78e144e63b0390ec66c3f17d7a436023abdb75f9d766974c1956`
- Manifest: `c8e97a6bfd0ac449721eacde2c1dfac04bd4d0b86fe8c0c81b3e585c1c3944f4`

Fresh source export/ERC reproduced **ERC 0**. Fresh native DRC with parity/all-track-errors reproduced **35 via_dangling + 1 track_dangling, 5 unconnected items and 16 missing-footprint parity issues**. No other violation types were reported. This is not a full DRC or parity pass.

Fresh source endpoint/net/pin-function/type sets match the independently reviewed BACKBIAS6 source: **90 components / 374 endpoints**. All present **74 footprints / 269 padshapes** match source nets, values and DNP. No legacy-net alias tolerance was needed for this board.

## Independent staged geometry/net comparison

Compared actual records by UUID, net, coordinates, layer, width and drill through each hash-pinned dependency, rather than assuming route logs prove intent:

1. BACKBIAS6 → channel preparation changes are confined to **CAM_SDA and GND**: 24 removed/changed and 15 added/changed items. New/moved standard vias are SDA (10.2,23.0) and GND (10.3,25.15) mm. No data-bus net changes occur in this stage.
2. Channel → VIO detour removes ten VIO tracks and adds five VIO tracks totaling **11.118376618 mm on In2.Cu**, with **no added VIO via**. This is a supply route, not an XCLK short bridge. Its altered layer/length cannot be treated as equal electrical resistance or equal PI.
3. Detour → final adds only **152 CAM_XCLK objects** and removes/changes none of the preceding copper: 150 tracks totaling **56.878962825 mm**, plus two **0.60/0.30 mm** vias at **(10.25,9.025)** and **(1.95,49.05) mm**. Actual XCLK tracks are on F/B, not In2. The new copper retains the intended clock net after loading the saved board; it has not been reassigned to VIO.

Track sums include routing branches and are not a propagation-delay extraction.

## Actual connectivity, not net-label equivalence

An independent object-contact graph plus separate actual filled-polygon-island nodes confirms:

- **U101.43 / U203.4 / R221.1** are one physical XCLK component.
- All three SDA pad endpoints remain physically connected.
- Each of **CAM_D0 through CAM_D7** independently connects its MCU and U201 endpoints. The remaining D7 bias gap is not a broken D7 main trunk.
- **27 AON padshapes**, including real J106.2 and PICO supply pins, remain connected across three In2 islands.
- **75 GND padshapes** remain connected through the single In1 GND region.
- **11 VIO padshapes** remain one routed-copper component. No VIO filled plane is implied.

Via-to-plane contact checks use copper-annulus samples and do not join islands solely because they share a net name.

## Remaining limits

The reported In1-reference samples are geometric screening only; this review did **not** independently reproduce the 178/4044 count. Local source/via antipad gaps remain material caveats, not waived coverage. More importantly, **B.Cu's nearest inner layer is In2 power**, not the deeper In1 GND. A continuous In1 polygon is insufficient proof of continuous nearest-layer clock return. Power-island boundaries, decoupling-mediated return, actual stackup, edge rate, via transitions, coupling and termination require dedicated SI/PI analysis and measurement.

No 24 MHz or 72 MHz operation is approved. The newly routed clock is long; prior long RESET and D3 bias branches remain unresolved SI concerns. The approximately 0.2 mm input-neck screen, actual supply current distribution, inner/outer copper thickness and voltage/transient budgets also remain unqualified; unchanged VIO width does not close them.

Five missing connections and sixteen missing source footprints remain real work. Wire-land strain relief/insulation, dual-sided R105/R214 assembly, unknown camera pin mapping, RF, battery safety, final enclosure and cost gates remain open. No source/copper changes, fabrication outputs or physical tests were performed by this review.
