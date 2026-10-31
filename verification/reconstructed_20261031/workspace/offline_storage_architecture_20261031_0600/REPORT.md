# Smart-pen offline storage — read-only architecture study
Date: 2026-10-31 UTC. Status: PROPOSAL ONLY / NO ADOPTION / NO FAB / NO POWER.
No source firmware, PCB, purchase, supplier contact or external publication changed. This separate report is an authorized local artifact.

## Scope and conclusion
User priority: coordinate accuracy and safety > size > runtime; CNY760 for two complete pens, excluding shipping but including camera/lens, electronics, batteries, PCB/FPC, assembly, shells and refills. No free laboratory/assembly assumption. Approximately 24 cumulative hours of effective writing is a cost-prioritized target, not an unconditional hard minimum. The existing 17.6-minute ceiling is not declared acceptable or a silent replacement for that target.

Internal 8 MiB cannot guarantee 24h by lossless compression. External storage needs a real pin-plan change. A 512 MiB-class architecture can provide a defensible bounded envelope without relying on compression, but the researched current Winbond part has no verified immediately available two-piece supply and no accepted all-in cost. Do not adopt it.

## Active versus archived baseline
See source_hashes.json for exact paths, SHA256 and scope. Active root firmware uses pen_sample48 wire packets in64-byte NOR slots; default recording disabled and board provider NULL. Archived BLE transport frozen store.c/store.h hashes exactly equal active versions. Full recovered verification-tree searches found no alternate compact/NAND store. Archived profile8/capacity.json already records the same63,488-slot/32-session limits and no guaranteed positive duration under unlimited failures.

Important integration correction: preserve archived accepted PC receiver v2 under verification/ble_pc_and_mode_stage_20261029/smart_pen_pc_receiver_v2_candidate_20261029. It uses exact20B ACK after committed raw48B, SQLite DELETE+synchronous=EXTRA, schema-trigger protection, and corrected fragment deadlines. Root software/pen_bridge.py WAL/FULL is older and must not replace these improvements. Archived camera capture v2 is a separate disabled successor, not evidence of active integrated camera/storage hardware.

## Verified storage and semantics
Optional flash8: nvs0x9000/0x6000; otadata0xf000/0x2000; phy0x11000/0x1000; ota_0 0x20000/0x200000; ota_1 0x220000/0x200000; pen_records0x420000/0x3e0000. Log=4,063,232B=3.875MiB=63,488slots. At60 records/s:1058.133s=17.6356min; controls and torn slots reduce this. OTA slots remain2MiB each.

48B transport fields: header/version/flags4, device4, session8, sequence4, timestamp_us8, page4, x_um/y_um8, confidence2, reserved2, CRC4. Storage adds ACK body8, ACK commit4 and data commit4. Coordinates are exact signed32 micrometres; timestamps unsigned64 microseconds. No precision reduction is authorized.

ACK requires currently offered exact session/sequence and approved encrypted/authenticated/bonded peer. Interrupted ACK replays. No individual sector reclaim: erase entire partition only after all committed records ACKed, recording stopped and safe gate; NVS durable erase intent recovers interrupted erase. Max32 recorded sessions may bind before byte capacity. No unACKed overwrite.

Existing filtered-sample serialization does not preserve all raw evidence: invalid observations have page/x/y/confidence zeroed; fault records become generic GAP; raw_down_us and contact_faults are transient. New lossless claims must distinguish exact existing pen_sample roundtrip from newly retained typed invalid-quality/contact/fault evidence. Raw images are outside this coordinate/event budget.

Read-only host tests rerun PASS: storage fault injection (52data cuts,12ACK cuts,512erase cuts), IDF mock security/NVS/readback, recorder pipeline. This is not physical power-cut/endurance/24h proof.

## Capacity arithmetic
24h*60=5,184,000 observations, plus events. Before overhead/events/reserve:
| Bytes/observation |24h MiB|existing-log hours|
|---:|---:|---:|
|8|39.55|2.351|
|12|59.33|1.568|
|16|79.10|1.176|
|32|158.20|0.588|
|36|177.98|0.523|
|64|316.41|0.294|
8–16B are illustrative, unmeasured compression averages, not guarantees. Arbitrary exact confidence/timing/coordinates cannot guarantee these ratios. Even independent confidence values alone need roughly10bits/observation, beyond3.875MiB for24h.

## Hardware pin audit and proposals
Actual controller baseline final_candidate/mainboard_revD.kicad_pcb in reconstruction_control_service_20261031_0510:
- pad36=GPIO48/SPICLK_N/ILLUM_STROBE.
- pad37=GPIO47/SPICLK_P/CAM_BUS_EN.
All ordinary available GPIOs already assigned. SPICS1 and GPIO33–37 are internal N8R8 PSRAM connections, not spare. NC pads not GPIO. Only strap nets0/3/45/46 remain outside functional assignments; GPIO0 also boot service, GPIO46 input-only. Do not assume16MiB internal flash or use volatile PSRAM for retention. Source:S1.

### Option A: preferred feasibility study, NOT selected design
Move five slow controls to resettable AON I2C expander: USB_EN1(GPIO18), USB_EN2(GPIO21), CAM_PWR_EN(GPIO41), CAM_IO_EN(GPIO42), CAM_BUS_EN(GPIO47). Reuse GPIO41 as direct expander RESET_N with proven default-low bias/reset circuit. Freed GPIO18/21/42/47 can carry storageCLK/MOSI/MISO/CS respectively, routing pending. Keep illuminationGPIO48, contact/pickup, DVP, sensor controls and USB D+/D- direct.

TCA6408A is a capability example: hardware reset returns outputs to inputs; both supplies can use qualified3V3_AON. Keep all downstream pulldowns and open commissioning jumpers. Existing USB low/low=USB100, not power isolation or USB suspend compliance. Source:S2.

Minimum delta: expander + decoupling/address/reset circuit; five control net reassignments; NAND+decoupling/control biases; fourSPI routes and CS pullup; revise pin contract/harness; evaluate bus loading, loaded VOH/VOL, output leakage and rail/reset ordering. Default outputs input; initialize zero output latch before configuring outputs; verify state before camera enable. Readback/I2C error must trigger direct reset, not an I2C-only shutdown.

POR-only expander is insufficient across MCU-only resets. Verify CPU/watchdog/brownout/bootloader/sleep and GPIO-hold behaviour; direct GPIO with pulldown is not proof of all reset cases. Resetting expander also disables camera and changes charger mode; log interruption. MCU frozen while reset driven high is not solved by this circuit; no independent-watchdog claim.

### Option B
Move USB_EN1/2,CAM_PWR_EN,CAM_IO_EN; retain GPIO47 CAM_BUS_EN. GPIO41 reset; three freed pinsSPI CLK/MOSI/MISO; fifth expander outputCS_N plus pullup. Fewer MCU reassignments but manualSPI ownership and extraI2C failure/latency for chip select. Similar component cost; not preferred.

Do not casually share boot straps, PSRAM or active camera pins; do not fix charger mode simply to free pins. None of these changes adopted.

## Proposed canonical schema / bounded envelope
This is a frozen study proposal, not code/API approval. Each canonical64B record: type1,version1,payload_length2,log_record_id8,timestamp_us8,payload40,CRC32 4. Device32/session64 in each independently recoverable page header. Page4096:header64 +62records*64 +footer64; header/footer bind page ID,count,length/checksums.

Types:SAMPLE(original seq32,page32,x/y32,confidence16,flags8); OBSERVATION_STATUS(original available invalid quality/reasons); CONTACT_EDGE(raw/confirmed states, exact times); FAULT(typed reason/state/action/related ID); PAGE_OR_CALIBRATION; SESSION; CLOCK_RESET; CONFIG_CHANGE. Payload overflow uses explicit continuation records, each counted. Exact field ordering for payloads and transactional commit spec still require implementation review. No invented precision, frames, nominal timestamps, smoothing or dropped events. Raw images excluded.

Optional block compression: integer deltas/varints, common page/session, raw fallback; byte-exact canonical reconstruction. Never depend on representative ratio for advertised worst-case capacity.

For512MiB reserve25% provisionally leaves384MiB=98,304pages=6,094,848positions. Budget:5,184,000observations +800,000extra event/continuation/session records +1,024session-boundary slack*61=62,464 +48,384remaining. This targets24h@60Hz without compression within stated limits; event budget is NOT a drop/rate-limit policy. Extra events/boots/failures beyond budget shorten duration. Unlimited elapsed idle events/boots cannot fit finite capacity. Reserve must cover qualified badblocks,torn pages,metadata and reclaim; actual goodcapacity/endurance remain unproven. Preserve data and signal capacity exhaustion safely.

## Durability, wear, upgrade
NAND is not a drop-in NOR callback: stage accepted records durably in wear-rotated internalNOR before batchingNAND pages; verify destination and persist migration watermark before staging reclaim. RAM-only batching is unacceptable. External segments reclaim only after durable authenticated exactACK; immutable IDs, duplicate-safe replay, append-only metadata and powercut recovery. NAND ECC complements but does not replace CRC/end-to-end checks. Exact chip programming restrictions apply (S4); current multiple writes per64B cannot simply migrate toNAND.

Keep dualOTA2MiB and rollback; never erase backlog for an upgrade; negotiate typed transport and receiver durable schema. Preserve accepted receiver v2 protections. Unrecognized typed records must not be ACKed by old host. Internal flash endurance is not established by PICO SKU; exact die/rating needed. Quantify staging write amplification, wear distribution, idle current and camera/BLE concurrency. No100k-cycle assumption or runtime promise.

## Cost-first alternatives and physical cost
1.Internal-only preserves current hardware/BOM, but root ceiling17.64min@60Hz before events. Future exact codec could give representative1.18–2.35h at16–8B average; this is unmeasured, not accepted duration. Compact scheme/NOR sector reclaim still needs implementation and tests. Retain24h goal as unmet; present explicit tradeoff rather than claim success.
2.256MiB NAND may meet24h only after a proved smaller worst-case envelope/event budget; current64B proposal does not. Same pin/reset/software complexity as512MiB, modest package saving not established.
3.512MiB NAND gives capacity margin, adds expander/reset/passives, routing/requalification, NAND firmware, powercut/endurance testing and hidden-joint assembly.
4.64MiB NOR lacks a worst-case24h bound; microSD adds socket/card footprint,power peaks and controller powerloss uncertainty.

NAND8x6mm body +expander3x3mm body =57mm² minimum package-body area, NOT placement/courtyard/route-area proof. Current14mm-wide controller cannot be declared to fit: pads/courtyards, decoupling, safe zones, refill/shell clearance, added routing and assembly access must be checked. WSON andQFN hidden joints require priced qualified reflow/inspection, not free hand-solder assumptions. Height and actual landpattern must be checked against exact datasheet/package drawing. No PCB geometry changed.

## Pricing/supply evidence and stopping condition
Read-only supplier catalog checks, no checkout/account/contact/RFQ. Supplier catalog is primary for its offer, manufacturer for capabilities. Search/open responses disagree, so these are observations, NOT actionable quotations.
- W25N04LVCEIG: manufacturerS3 says mass production,3V,4Gb,8x6SON,4096B pages,ECC; no longevity commitment shown. DatasheetS4 confirms CE8x6WSON part identity. Not the old KV part.
- MouserS5 search returned qty1USD30.48, nonstocked,36weeks; direct opened page returned no price and24weeks. Thus no reliable current two-unit price; both supply views exceed30days. Do not rely onUSD30.48 as quote.
- DigiKeyS6/S7 search showed nonstocked tubeMOQ63 ($7.37095 earlier scrape) and trayMOQ480 ($20.944 another scrape); live rendered opening lacked price. These are neither two-unit available stock nor a valid low-volume comparison.
- TCA6408ARGTR DigiKeyS8 direct opening: qty1USD1.66,33,988in stock; search previouslyUSD1.47. Prefer direct-page observation; no inventory reservation.
- LCSCS9 earlier searchUSD0.7141/1,763stock was stale; direct opening does not expose confirmed price/stock. Not a validated lower quote.
- Older W25N04KVZEIR LCSC catalog exists but manufacturer family marksNRND(S10). Do not silently substitute. GigaDevice4Gb catalog search did not establish an accessible matched manufacturer-data+two-unit offer. Generic low-price or parallelNAND alternatives are not qualified substitutes.

Indicative—not firm—Mouser search NAND plus directDigiKey expander would be2*(30.48+1.66)=USD64.28 just fourICs, before tax/passives/PCB/assembly/testing. Do NOT convert with invented FX or conclude≤CNY760. Complete incremental cost is unknown; existing fullpen BOM/assembly costs already contain unresolved items. Formula: C_existing_complete_two_pens +2*C_NAND+2*C_expander+C_passives+C_PCB_FPC_delta+C_assembly_inspection_delta+C_paid_validation ≤760CNY excluding shipping. No term may assume freelabor/equipment. Supply-price search stopped after manufacturer,currentWinbond distributor offers,LCSC,TI and alternateGigaDevice catalog leads failed to establish an actionable two-pieceNAND offer; no outreach authorized or needed for this report.

## Next bounded engineering actions (not adoption)
Compare expander-reset default truth table and physical placement against current checkpoint; freeze source-record requirements with accepted receiver v2; benchmark exact codec on representative real traces when available; obtain trustworthy catalog/quote evidence only within authorization. Resolve all-in cost and≤30day availability before choosingNAND. No firmware/PCB implementation or component purchase from this report alone.

## Primary sources / supplier evidence
S1 https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf
S2 https://www.ti.com/lit/ds/symlink/tca6408a.pdf
S3 https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-lv/?__locale=en&partNo=W25N04LVCEIG
S4 Winbond-authored datasheet via official distributor: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8919/W25N04LVxxxx_RevA_2026-03-24.pdf
S5 https://www.mouser.com/ProductDetail/Winbond/W25N04LVCEIG?qs=vcFyY%252BOcAyin5WPi7%252BalaA%3D%3D
S6 https://www.digikey.com/en/products/detail/winbond-electronics/W25N04LVCEIG/29746581
S7 https://www.digikey.com/en/products/detail/winbond-electronics/W25N04LVCEIG/29746641
S8 https://www.digikey.com/en/products/detail/texas-instruments/TCA6408ARGTR/2094640
S9 https://www.lcsc.com/product-detail/I-O-Expanders_Texas-Instruments-TCA6408ARGTR_C181499.html
S10 https://winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-kv/?__locale=en&partNo=W25N04KVZEIRG
S11 https://www.ti.com/product/TCA6408A/part-details/TCA6408ARGTR

### Additional datasheet constraints checked
S4 sections10/11: factory valid blocks minimum2008/2048; blocks256KiB; sequential page programming required; check program/erase status and ECC, replace failedblocks. CE is8-padWSON8x6, not CB24-ballBGA; centerpad is electrically unconnected and can float or connectGND; exposedvias underpad are discouraged. AC table limits partialpage programming to4operations. This reinforces that current per-slot NOR writes cannot be directly ported. Exact mechanical height/landpattern still needs drawing-level extraction before placement approval; no claim it fits existingboard.
