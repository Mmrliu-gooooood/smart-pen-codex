# SENS external-reference tree: two bounded rejected proposals

**Read-only planning / NOFAB / NOPOWER.** Base PCB remains `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c`, actual native DRC still **0/149/0**. No candidate copper was added to a board or saved. Neither proposal is ready to materialize.

## Source audit

Exported actual same-basename schematic netlist has exactly **12 physical nodes**, matching every native SENS pad: J202.23; U201.23/24; U202.16; U203.16; U204.1; C202.1/C204.1/C206.1/C208.1; R242.2/R243.2. No separate TP exists on this net. Exact pinfunction, pintype, value, footprint, UUID, coordinates and actual layer membership are in `evidence.json` and `comparison.json`. The connector symbol calls J202.23 **passive**, not power_out: its external head-reference **input role is the design contract**, not an inferred on-board regulator. No AON tie, added regulator or external camera voltage assumption.

AXC VCCB is SENS; TCA **VCCA** is SENS. Four existing local bypass islands are retained. Two SCCB pullups are included, not forgotten. The entire 12-pad tree is conceptually connected in both models when obstacles are ignored; actual clearance failure makes both unusable.

## Exactly two topologies, no grid or micro-offset search

**A — old lower feeder plus In3 central spine.** 47 old9a03 lower source-to-pullup objects are extracted exactly by UUID, with original0.25/0.3mm widths. New local cap accesses and a0.25mm In3 x=6.5 spine join four local groups and the pullups. Total61 proposed objects, **11 blocked edges**. Old feeder now collides with J107.3 and EXTCLK/HREF/VSYNC/PCLK; spine crosses existing GND/DVP/clock/CAM control copper. Old working geometry cannot be blindly reused after intervening placements/routes.

**B — In3 lower fanout and B-layer upper zigzag chain.** A source-side B escape, through transition, In3 lower fanout, four local access vias and a B zigzag upper chain. Total25 objects, **6 blocked edges**. Source via (4.5,91.2) hits J202.17/18; lower spine crosses CAM control; upper B spans intersect clock/timing signals, AON and back-side pads; R243 access via (11.325,75) intersects existing In2 switched-camera supply.

All new tracks are0.25mm, no narrow rescue traces; local frozen links remain0.3/0.254mm. Via0.60/0.30mm is unchanged. These are geometry choices, not ampacity/electrical guarantees. `comparison.json` contains every exact proposed coordinate and every collision. `cutsets.json` gives exact blocked edges and obstacle UUID/net/layer/copper bounding box. This is a **candidate-specific collision cut list**, not a global minimum-cut proof and not permission to delete these obstacles. Further routing should change topology around these documented barriers, not nudge the earlier18 failed left trunks.

## Checks and limitations

Actual finite native copper/pads/vias are checked at0.15mm foreign-copper spacing,0.25mm hole-hole and edge spacing, active actual-layer keepouts, plus every via annulus versus **all pad copper layers including same net**. Same-net candidate connectivity uses finite copper with hole disks removed. Neither tree has thin-feed or missing-pad connectivity disguised by ideal graph edges.

Return-risk comparison uses guarded one-shot rawnative Unfracture, then only subtracts nominal new foreign-via clearance disks from current GND fills. A predicts main-plane potential loss3.699502mm² and small-plane0.043612mm² per corresponding layer; B5.064418/0.255884mm². Each resulting0.25mm-eroded polygon remains one component and no previous signal projection is lost above the numerical reporting threshold. **This is not fresh-filled native evidence**, and cannot certify real return shape, thermal changes or plane islands. Since both geometries already fail clearance, saving or filling either as a candidate would be misleading; exact post-fill/full DRC/parity would be mandatory after a geometrically feasible redesign.

Backpower, external-reference sequencing, actual head level, load budget, current capacity, cap effective value and board manufacturing remain unknown/unqualified. No powered or camera test, native editing, GitHub publication or manufacturing occurred.
