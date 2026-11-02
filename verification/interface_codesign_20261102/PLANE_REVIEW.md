# Independent interface co-design plane/reference audit

## Decision scope
Candidate 617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5 versus accepted private PCB24 dcaaafa93bde51e58a96d9443cb77031773fc42a16ad3db20210b53f0394b052. The tested plane island, fixed-region corridor, retained-reference and capacitor-pad invariants show no regression. New signal reference gaps remain near layer-transition vias and are quantified below, not waived as zero. This is a narrow static geometry result, NOT native DRC/body acceptance, pad/barrel ampacity, IR drop, SI/impedance, fabrication or power-up approval.

## Binding and method
Own complete native projects; dependency_contract.json separately binds parent52 and candidate53 non-PCB dependencies. Only schematic/usb_entry.kicad_sch changes; only GateStudy.pretty/J107_DistributedWireLands3_NOFAB.kicad_mod added. Other51 original dependencies identical. New J107 pad geometry and schematic are reviewed separately; this audit does not pretend those are unchanged. Both matched-project refills reproduce native PCB bytes exactly.

Replay with /usr/bin/python3 (KiCad bindings): binding.py, audit.py, neck.py, capacitors.py, reference_detail.py, new_endpoint_gaps.py, negative_geometry.py. Repeat each substantive report with -O. Native finite polygon approximation50nm; native fractured fill is unfractured only once with guarded area preservation. Independent GEOS ring/area and hole tests, corridor/barrier and omitted-hole negative fixtures included. GEOS erosion64 segments/quadrant,15 bisections gives0.0001220703125 mm diameter brackets. These numerical settings are not manufacturing tolerances.

## Actual filled planes
Each of In1 GND/In2 AON/In4 GND remains one connected island.
- In1/In4 GND each lost0.857227035278 mm²; gained5e-13 mm² numerical residue.
- In2 AON lost0.576852483019 mm²; gained6.171266797438 mm².
This is measured versus matched24 fill, not historical different fills. Compared qualitatively with discarded maze candidates, only two new USB vias and no new PICKUP via are imported; old y48 and y75 bottleneck regressions are absent. Area totals alone do not establish PDN quality.

## Retained and moved reference
All3895 retained track/reference projections were checked, with both In2 and In4 for In3 copper. Count differs from3912 in earlier maze because this design removes the full old ILLUM In2 chain. Native50nm Boolean method gives ZERO positive retained reference-loss rows. Author's separately reported matched Boolean noise≤2.2e-8 mm² is not erased or converted into a physical accuracy claim. Clock and STRAP detailed checks show no new loss on either side; unchanged pre-existing endpoint gaps remain where present. audit.json contains every new finite-track projection and per-net reference unions.

New copper union uncovered areas:
- GND B→In4:0 of2.247462475878 mm², fully referenced.
- ILLUM B→In4:0.152683575916 of2.447653134985 mm².
- USB_EN2 F→In1:0.064972997196 of0.8818151409685 mm².
- USB_EN2 B→In4:0.0649464868615 of1.0128813492525 mm².
- USB_EN2 In3→In4 and In2:0.1299765725265 of1.5494039973225 mm² each.

new_endpoint_gaps.py subtracts all SAME-net via copper envelopes expanded0.1505mm from these actual uncovered polygons. Small residuals remain and are explicitly retained: ILLUM0.0004762336555 mm²; USB F0.0001829102495/B0.00015668962/In3 each0.000396696682 mm². Residual vertices lie no farther than0.162363534 mm (ILLUM) or0.153740369 mm (USB) beyond nearest same-net via copper radius. This locates the measured residuals at via-gap edges, not a blanket assertion that every gap is exactly an ideal circle or electrically harmless. New union projection areas independently agree with audit.py. Full source via UUIDs/coordinates are included.

Native stack In3→In2 dielectric0.2028 mm; In3→In4 0.13 mm; dielectric properties UNQUALIFIED. No field solver or measured stack qualification was performed.

## Identical fixed-port corridor tests
Source window[10.5,82.7,13.2,85.1] includes J106.2 AON via(11.9,83.9). All target windows are in neck.json; U201 includes AON via(10.975,30.2375). These are finite regional plane connections, NOT thermal spoke/barrel/pad-to-pad current capacity.

Lower bounds (upper bound adds0.0001220703125 mm):
- Both GND planes source→MCU:1.9796142578125 unchanged.
- Both GND planes source→U201/U202/U203:2.5325927734375 unchanged.
- AON source→MCU improves0.857177734375→1.1494140625.
- AON source→U201/U202/U203:1.1494140625 unchanged.
No narrower path than24 is found by these fixed-window morphological metrics. These metrics do not establish other arbitrary paths or replace PDN qualification.

## Capacitors and boundary
36 actual supply/GND pads across18 supply capacitors, including C302 CAM_3V3_PRELINK, preserve finite terminal connectivity and checked ground-reference projections without loss. Complete all103 GND connectivity belongs to the independent ECAD review, not claimed from this subset. New J107 body/wire envelopes belong to MCAD review. Nothing in old accepted24 or either frozen HOLD package was changed.
