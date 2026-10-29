# 14 × 45 mm integrated power: independent connectivity review

Date: 2026-10-28 UTC. **NOFAB remains.** No new source-projection, pad-net or routed-connectivity defect was found within the scope below. Passing these checks does not establish temperature-window noise immunity or safe charging.

## Frozen snapshot

All **104 manifest-listed files** matched their recorded hashes. Failed experiments and the 12 mm comparison board were not treated as the authoritative result.

- Manifest SHA-256: `75aa10fe0d7d974b7a500a4c37e4a5966b766c92cddd6cfcef8718a9f009cd3b`
- Authoritative `power_integrated_study.kicad_pcb`: `5c5764e7576c9461464c12da3531410e63ef4db32a28a67a5fa6125ef0b92014`
- Original core comparison PCB: `7a7013b4371401595b2ffcc8569bbe2b2bf0ce828f567d530ec3ab6a0b755b1f`

Fresh KiCad native XML export and all-severity ERC reproduced **0 errors/warnings**. Fresh native DRC with schematic parity and all-track-errors reproduced **0 violations, 0 unconnected items and 0 parity issues**.

## Source, defaults and core preservation

- Independent comparison against the previously independently exported unified source, applying only the documented integrated-board projection, matched **52 entities / 150 pin endpoints / 32 nets**. Actual **50 footprints / 146 padshapes** match source values, net assignments and DNP.
- Native attributes confirm **only RT101 and RT102 are offboard**, both still in BOM. Every other entity remains on-board; no temperature-control IC/passive is hidden to obtain a clean board. The two candidate NTCs and their protected-GND returns remain distinct measuring chains.
- **JP1 is the sole native/XML/PCB DNP**, with separate CHARGE_DISABLE and CE_PERMISSION_INTERNAL nets. R6 remains the local VBUS-to-CE pull-up. Neither net naming nor complete routing joins across the intended OPEN jumper. No direct parallel CE-to-ground bypass was found.
- Geometry/net multiset comparison against the original core confirms **182 original track/via items retained**. Exactly **eight original items are absent**, all in the obsolete external CE branch: six tracks and two vias, including the explicitly authorized former escape via at **(9.1,17.05) mm**. This comparison checks actual geometry, not just UUID existence. Original SW/FB and power-route geometry remains represented.
- This is not “all copper unchanged”: the board outline, new thermal routing and filled polygons differ. No qualification is inherited merely from preserving the original core tracks.

## Actual routed connectivity and returns

An independent graph used KiCad's actual local pad/track/via contacts plus separate nodes for each **actual filled polygon island**. Via-to-fill contacts were sampled in the copper annulus, rather than assuming a drill center is copper. It did not equate disconnected same-net islands.

All **25 multi-pad electrical nets** form connected components. In particular:

- **GND: 44 actual padshapes connected**, including all nine B.Cu fill islands and the single In1 GND region. The nine B-side islands are not nine isolated electrical grounds in this snapshot.
- C101 at **(12.5,20.7) mm** has its GND pad connected; **U104.3** also reaches the real ground network. These are actual routes/contacts, not merely matching net names.
- U106 REF force/sense ground pins and force/sense output pins remain correctly assigned and electrically connected. Comparator returns, NTC return, REF_EXC, HOT_SENSE, COLD_SENSE, both reference-supervision dividers and THERM_OK all pass the same physical-connectivity check.
- SYS_RAW has one filled In2 region; the retained core and newly connected low-power VBUS branch are electrically complete. This does not qualify branch voltage drop, loop inductance or current capacity.

## DSE repair and layout boundary

The DSE library hash is the previously independently verified repaired footprint:
`3752b8d0cbb22f05065d41bec052df230ed4ffa2c47811046b4097627a91320a`.
The actual board U102 retains copper-only numbered pads 1–3 and, after B-side placement, **six filled rectangles plus twelve filled circles on each of B.Mask and B.Paste**. Thus the explicit R0.05 aperture construction is present on the board, not only in an unused library. Nominal geometry does not qualify stencil release, mask registration or assembly tolerance.

The actual placement overview was inspected: the precision comparator/NTC/reference circuitry is primarily in the lower axial section, away from the core switcher section; preserved SW/inductor geometry has not been relocated into the precision network. This is a useful placement separation, **not an independently quantified coupling/noise margin**. Long low-power supply/control routes, shared ground impedance, the sense-input routing and two external sensor harnesses can still introduce errors. Connected force/sense pins do not by themselves prove Kelvin-quality routing or sufficiently small ground error.

## Explicit remaining gates

The approximately **1.17 mV conditional static temperature-recovery margin is not a measured interference allowance**. No switching-noise, leakage, thermoelectric, ground-shift, reference-transient or harness-coupling budget was closed by this review. Validate real sensor installation/self-heating, open/short faults, brownout/ramp behavior and CE transitions before any commissioning bridge is closed.

Also open: BQ RGT package-revision/purchased-part compatibility, EP paste/via-in-pad processing, effective MLCC capacitance, inductor peak/fault/temperature behavior, USB pre-enumeration startup current, protected-cell ratings, charger thermal behavior, double-sided assembly and the full pen envelope/cost. The 14 mm width is a distinct mechanical candidate, not automatic proof of an 18 mm pen fit.

No source or copper was modified. No charging, physical tests, production files or manufacturing release were performed or inferred.

## Post-review clarification — 2026-10-28

Subsequent path analysis reported in `power14_vbus_paths` identifies parallel new fine VBUS routes between nodes of the original core trunk. Therefore the phrase “low-power VBUS branch” above describes its intended consumer, **not proof that every new 0.15 mm segment carries only temperature-control current**. A conditional resistor-network model reports up to 0.323 A/A of normalized BQ input current in an added segment, with idealized zero-resistance vias/pads; this reviewer has not independently reproduced that model. It is not a USB current authorization or measured operating current. Actual current partition, via/pad resistance and fine-track thermal/voltage-drop qualification must remain open. This clarification does not identify an open circuit or short and does not modify the frozen board.
