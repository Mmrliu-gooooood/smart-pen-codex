# Contact edge / prewake runtime — 2026-10-28

## What is implemented
`firmware/runtime/contact_power.c/.h` is an executable, allocation-free C11 state machine, not a GPIO driver. `pen_cp_step()` consumes a monotonic timestamp, normalized contact/IRQ levels, camera-readiness/calibration evidence, storage/USB sleep constraints and an optional fresh coordinate observation. It produces ordered `pen_sample` records and explicit adapter action requests. No function drives a pin, powers a camera, sleeps the MCU or writes flash. Hardware actions therefore remain disabled unless a separately reviewed adapter explicitly performs them.

The audited hardware table currently names `PICKUP_INT_N` GPIO1 and `NIB_CONTACT_N` GPIO2; **no GPIO number is compiled into this module**. `hardware/mcu_usb/gpio_assignment.json` and the electronics owner's next revision remain authoritative. `docs/electronics/pickup_contact.md` specifies a normally-open binary dry contact, **not an analog pressure/force sensor**. This implementation does not invent a pressure value or ADC threshold calibration.

## Concrete behavior
- A pickup IRQ or raw nib-down in logical ASLEEP requests `WAKE_CAMERA`. Initial low pickup IRQ also requests `CLEAR_PICKUP` once; the adapter must clear the actual latched sensor source and subsequently report the real pin level.
- On raw nib-down, capture `raw_down_us` immediately. Hold up to eight candidate observations while debouncing the press. Confirmation emits the captured samples in timestamp order, including the original down-edge sample. This does not move the first observed nib location to the later debounce instant.
- If no fresh observation existed at the edge, its retained record is explicitly invalid, with zero coordinate/page/confidence. No interpolation manufactures the missing onset.
- An overflowing eight-sample buffer is dropped with an explicit invalid CONTACT+GAP boundary; later observed coordinates restart with GAP. A short press released before confirmation yields a GAP release, not invented ink.
- Raw release bypasses press debounce immediately, clears pending samples and emits an invalid contact-off record. Hardware RC/filter/interrupt latency still exists and has not been measured.
- VALID is propagated only from a fresh input that was already marked valid, calibrated, camera-ready, assigned a nonzero page and at/above configured confidence. This core never generates coordinates, page IDs or calibration evidence. Invalid outputs clear page/coordinates/confidence; recovery marks GAP.
- Camera not-ready starts a bounded readiness wait; exceeding it latches CAMERA_TIMEOUT. A stuck low pickup IRQ and excessively long contact latch separate faults. A fault emits one invalid GAP/release boundary, drops buffered points, suppresses new coordinate output and never requests sleep while unsafe.
- Fault recovery must be explicit and requires raw contact released, pickup IRQ high, no pending storage and USB sleep permission. A backwards clock latches CLOCK and **cannot** be cleared by local recovery; create a new boot/session and initialize the state again.
- Sleep is requested only after configured idle time while READY, contact/IRQ both inactive, no unconfirmed samples, no pending storage and explicit USB sleep permission. Readiness of actual RTC wake routing, IRQ configuration/readback, bus state and system power rails remains the adapter's responsibility. The request is not proof that physical sleep occurred.

## API and ownership contract
1. Initialize once per boot with explicit timings and confidence. Zero/invalid deadlines and a press debounce at least as long as stuck-contact timeout are rejected. Test timings are fixture values, not tuned pen defaults.
2. Serialize calls in one owner task. Capture physical contact edges in an ISR/timestamp ring if polling cannot meet timing; this core cannot recover an edge it was never given. Pass normalized booleans (active-low pin inversion belongs to the adapter).
3. Every call has a template `pen_sample` with correct device/session and `timestamp_us == input.now_us`. Set `has_observation=0` for pure control ticks; do not repeatedly re-use an old image coordinate as a fresh observation. Buffered candidates retain their own capture time.
4. `output.events[0..count)` must be consumed in order. **The core is not a sequence allocator:** input `seq` is copied only as a placeholder. The durable recording layer assigns each emitted record its next sequence and reconciles failed writes before advancing. Session reset, flash-full/user-visible error and queue backpressure are external responsibilities. Do not discard contact-off/GAP control records merely because they have no valid coordinate.
5. Output capacity is fixed at ten records, covering the eight-entry debounce buffer plus control boundaries. No heap allocations occur.
6. No calibrated input must be admitted from synthetic bench fixtures. Existing bench packets are invalid and stay invalid through this gate.

## Executed verification
```
python -m unittest discover -s tests -p test_contact_power.py -v
cc -std=c11 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined \
  -Ifirmware/runtime -Ifirmware/portable firmware/runtime/contact_power.c \
  tests/test_contact_power.c -o /tmp/contact_power_san
ASAN_OPTIONS=detect_leaks=0 /tmp/contact_power_san
```
Both passed in this workspace. Tests execute the real C implementation and cover original-edge timestamps, debounce flush, immediate release, short tap, overflow GAP, missing observation, calibration loss/recovery, readiness timeout, safe fault recovery, storage/USB sleep interlocks, stuck IRQ/contact, backwards clock and malformed configuration. ASan/UBSan pass is host-memory/undefined-behavior evidence, not device validation; leak detection is explicitly disabled.

## Still unverified
GPIO/RTC wake setup, LIS2DW12 register driver and physical IRQ clearing, ISR latency, contact bounce/RC/ESD behavior, actual camera startup time, sensor sleep/rail sequencing, measured first-stroke accuracy, analog force sensing, hardware energy/current and real flash integration. This module is reusable logic, not completion of those gates or of the full pen.
