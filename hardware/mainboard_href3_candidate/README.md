# HREF3 partial mainboard candidate — NOFAB

Date: 2026-10-28 UTC. This is a distinct successor to BIAS4, not the full pen or a manufacturing release. The frozen XCLK5/BIAS4 boards are unchanged.

## Result and source identity

The native schematic is byte-for-byte unchanged from BIAS4: 90 entities, 374 pin endpoints. There are 74 PCB footprints / 269 pad shapes. Only R220, the same 100 kΩ 1% 0603 HREF-to-GND bias, moves from F.Cu to B.Cu. Its pad 1 is (1.200,45.000) mm and pad 2 is (2.850,45.000) mm; centre (2.025,45.000) mm. No value, net, footprint identity, symbol path or component count is changed.

Native ERC is zero. Full native DRC using all severities, all track errors, schematic parity and `--exit-code-violations` returns **5**, not success: **3 unconnected items, 34 dangling-via warnings, 3 dangling-track warnings and 16 missing-footprint parity issues**. Other geometry checks are zero. The additional dangling track is the previous R220 ground stub, explicitly retained. No missing components are hidden or marked offboard merely to quiet parity.

The three missing connections are HREF's main MCU-to-translator connection, CAM_PWDN_UART_RX (TRIG semantic) main connection and RF_SIP. Completing a bias branch is not completing the HREF signal chain.

## Physical delta and bounds

Every BIAS4 track/via is retained unchanged. The additional HREF branch totals 3.222056 mm and uses one standard 0.6/0.3 mm through via at (1.950,46.525) mm. The new R220 ground route totals 2.033148 mm, is 0.15 mm wide and uses one standard 0.6/0.3 mm via at (1.925,43.350) mm. The HREF branch is 0.127 mm; no new fine-via exception is introduced. See `route_delta.json` for exact UUID/net/geometry.

Native local copper plus separate actual filled polygon islands confirms U202.6 and R220.1 joined, with U101.23 still separate. All 27 AON, 75 GND and 11 VIO pad endpoints remain connected. This is connectivity evidence only, not current capacity, return-path impedance, EMI or waveform qualification. Added vias change filled copper contours despite every old track/via being retained.

The B-side 0603 addition changes the mechanical envelope at y=45 mm. Use an explicitly conditional 1.0 mm body + 0.15 mm solder envelope until an actual part/tolerance stack is qualified. Existing enclosure checks do not automatically cover this change. Existing B-side copper/via features beneath or near the new component courtyard require assembly and solder-mask review; courtyard non-overlap is not a soldering-process qualification. The grid-derived small staircase segments still require layout cleanup after connectivity is settled; no claim of production-quality routing is made. Mechanical fit, solderability, assembly access and component procurement remain open.

## Verification and rejection behavior

`check_delta_graph.py` passes both normal and optimized Python with explicit exceptions. The expected-new-net contracts preserve literal intended net names independently from saved board readback. `guard_proof/proof.json` covers good, wrong-net, empty, missing-UUID and duplicate-UUID cases in both Python modes. Each bad case stops before a subsequent DRC invocation. Each good case reaches DRC, whose expected exit is 5 for this known incomplete board; a good guard is not zero DRC.

Both routing generators also ran under optimized Python in a separate output. `reproduction` retains scripts/logs as provenance: they require the BIAS4/native candidate files and existing fine-process contract at their recorded locations, not a self-contained install script. Failed placement/routing trials are not the authoritative board.

No camera or battery has been powered, no flash/eFuse changed, no commissioning bridge closed, no Gerber release or purchase occurred. The full power, camera pin mapping/timing, USB/RF, 16 footprint integrations, battery/NTC, enclosure, accuracy, endurance and cost gates remain open.
