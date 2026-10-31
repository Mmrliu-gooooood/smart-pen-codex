#ifndef PEN_HOST_ADAPTER_H
#define PEN_HOST_ADAPTER_H
#include "pen_capture_app.h"
#ifndef PEN_ADAPTER_HOST_TEST
#define PEN_ADAPTER_HOST_TEST 0
#endif
#define PA_CAPACITY 8u
enum { PA_OK=0, PA_DISABLED=-1, PA_STATE=-2, PA_LATE=-3, PA_FULL=-4, PA_INPUT=-5, PA_SINK=-6, PA_LEASE=-7 };
enum pa_kind { PA_EDGE,PA_FRAME,PA_IDLE };
/* Input/frame pointers live only during sink. Nonzero result is fatal. The
 * mandatory fault sink must stop its application consumer and surface an error;
 * never continue recording after overflow, late data or a lost frame lease. */
typedef int (*pa_sink)(void*,const pen_app_input*);
typedef void (*pa_fault_sink)(void*,int);
typedef struct { uint64_t time; enum pa_kind kind; uint8_t contact,irq; pen_capture_view view; unsigned left,top,width,height; } pa_event;
/* Public storage for allocation only: fields are private implementation state.
 * Zero-initialize before first init; never mutate/reconstruct active storage. */
typedef struct { pa_event queue[PA_CAPACITY]; size_t count; pen_capture *capture; pa_sink sink; pa_fault_sink fault_sink; void *ctx; uint64_t sealed; uint8_t sealed_valid,enabled,faulted,busy,contact,irq,has_frame; pen_capture_view active_view; pen_app_frame active_frame; pen_capture_roi_origin active_origin; uint8_t binding; } pen_adapter;
/* Initialize only zero-initialized storage or a successfully stopped, nonfaulted
 * adapter. Fault is terminal for this adapter lifetime. New synthetic test fixture
 * != physical warm restart. Initialization never starts capture or power hooks.
 * Single task owner, never ISR/thread-safe. Callbacks may query pa_origin only;
 * they must not mutate capture/frame/adapter or retain borrowed pointers.
 * Reentrant init/enqueue/drain/stop are rejected. Both compile-time host-test gate
 * and runtime opt-in must be set. No production provider is installed. */
int pa_init(pen_adapter*,pen_capture*,pa_sink,pa_fault_sink,void*,int);
/* Explicit initial contact/IRQ levels must be queued before any frame if nonzero.
 * Values must be0/1. Arrivals may be out of order only before sealing. Same-time
 * edges retain arrival order and precede frames, then idle events. */
int pa_edge(pen_adapter*,uint64_t,uint8_t,uint8_t);
/* Takes ownership of the single current synthetic frame lease on success.
 * On fatal failure capture is stopped and any held lease released, INCLUDING
 * the attempted frame; caller must not keep/release/reuse it. On PA_STATE (e.g.
 * reentry/disabled) no new ownership transfer occurs. Valid ROI is96..256 per
 * axis; retains stride640 and source timestamp, no rescale or exposure claim. */
int pa_frame(pen_adapter*,const pen_capture_view*,unsigned,unsigned,unsigned,unsigned);
/* No-frame timer/timeout observation, not synthetic image or forced coordinate.
 * Pipeline's configured stale/GAP policy remains authoritative. */
int pa_idle(pen_adapter*,uint64_t);
/* Caller certifies ALL producers have supplied every event<=watermark. Dispatch
 * only queued events<=watermark, chronological and without timestamp retiming.
 * No implicit idle event. Later arrivals<=sealed watermark are terminal faults.
 * The watermark cannot be inferred merely from wall time or empty capture queue.
 * Sink sees current ordered levels, capture-running readiness, storage_pending0
 * and usb_sleep_allowed0: this candidate does NOT authorize real sleep/maintenance
 * or represent asynchronous dirty transactions. A real provider must add policy. */
int pa_drain(pen_adapter*,uint64_t);
/* Copy origin only for the exact live frame pointer during its sink callback.
 * The returned value may be copied, but must stay tied to frame/source identity.
 * No physical mapper/calibration/qualification is provided. */
int pa_origin(const pen_adapter*,const pen_app_frame*,pen_capture_roi_origin*);
/* Discard queue, release lease and stop capture; no restart. Nonfault stop is
 * idempotent. Underlying cleanup failure is terminal and reported to fault sink. */
int pa_stop(pen_adapter*);
#endif
