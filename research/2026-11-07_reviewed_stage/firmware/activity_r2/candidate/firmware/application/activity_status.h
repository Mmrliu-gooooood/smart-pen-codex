#ifndef PEN_APPLICATION_ACTIVITY_STATUS_H
#define PEN_APPLICATION_ACTIVITY_STATUS_H
#include "pipeline.h"

/* Optional, host-reviewed sidecar. No existing structure, callback, wire packet,
 * or default build is changed. Call only on the same actor as pen_app_step.
 * This is a software snapshot, NOT a physical contact/power/ink measurement. */
#define PEN_APP_ACTIVITY_VERSION 1u
enum pen_app_activity {
 PEN_ACTIVITY_UNAVAILABLE=0, PEN_ACTIVITY_LOGICAL_ASLEEP,
 PEN_ACTIVITY_PREPARING, PEN_ACTIVITY_READY, PEN_ACTIVITY_CONFIRMING,
 PEN_ACTIVITY_CONTACT_GAP, PEN_ACTIVITY_TRACKING, PEN_ACTIVITY_REPLAY_ONLY,
 PEN_ACTIVITY_SLEEP_PREPARED, PEN_ACTIVITY_BLOCKED, PEN_ACTIVITY_FAULT
};
typedef struct {
 pen_app_status legacy; /* recording still means STORE SESSION OPEN */
 uint32_t version;
 enum pen_app_activity activity;
 enum pen_cp_phase logical_phase; /* ASLEEP never proves hardware deep sleep */
 uint64_t last_event_us;
 uint64_t durable_reference_session;
 uint32_t durable_reference_seq;
 uint8_t event_known, last_raw_contact, last_contact_confirmed;
 uint8_t preconfirm_count, gap_required, pipeline_ready, durable_reference_known;
} pen_app_activity_status;

/* last_* contact facts describe the last processed CP event, not live GPIO.
 * Replay/fault/prepared snapshots may contain stale historical contact facts.
 * pipeline_ready means the CP readiness gate, NOT camera-ready GPIO, decoded
 * paper or permission to declare a coordinate valid. TRACKING means confirmed
 * contact with an unbroken valid-observation chain; it may persist on a fresh
 * timer-only step. It is NOT "a new point committed this step" or physical ink.
 * CONFIRMING may have valid samples only in RAM. CONTACT_GAP can be confirmed
 * without any valid coordinate. Read committed records for software ink data.
 * The durable reference is the last record of the final session-table entry.
 * It is a known committed record from successful append/reopen metadata,
 * including GAP/release. It is NOT the physical last slot for an interleaved
 * restored log, an all-session maximum sequence, or history across reclaim.
 * It may lag a physically written final-sync failure; reclaim clears it.
 * Actor/provider errors not stored in pen_app are NOT classified as FAULT here.
 * Preserve the separate actor_error reporting channel when integrating.
 * No clock read, allocation, Flash I/O, ACK, ticket or application mutation.
 * With no new CP step, time passing alone does NOT expire READY/TRACKING or
 * advance last_event_us. UI must check event_known and event-stream age using
 * the same boot's monotonic clock plus its own qualified timeout/watchdog;
 * querying this API is not a freshness check or a source of new sensor data.
 * Output must not overlap app/store. Such overlap returns -1 with all objects
 * unchanged. A non-NULL app with initialized!=1 also returns -1 without any
 * write or store-pointer inspection: failed init may leave that pointer
 * indeterminate or retain an old store that could alias output. Other invalid
 * inputs return -1 and clear output. Never consume output on nonzero return. */
int pen_app_get_activity_status(const pen_app*,pen_app_activity_status*);

enum pen_app_activity_change {
 PEN_ACTIVITY_INITIAL=1, PEN_ACTIVITY_STATE_CHANGED=2,
 PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED=4
};
typedef struct {
 pen_app_activity_status previous;
 uint8_t initialized;
} pen_app_activity_watch; /* zero-initialize for each app lifetime */

/* Optional local transition detector. Caller invokes after EACH ordered step
 * and sleep/cancel/replay/fault boundary; no callback or reporting is installed.
 * STATE ignores timestamps, preconfirm count, slot counts and durable position,
 * so ordinary frames/timers do not flood a state indicator. A changed durable
 * reference is separate; it is not an every-commit notification guarantee.
 * New consumers must choose their own delivery/backpressure policy. The old
 * report_status ABI remains unchanged and does not receive this snapshot.
 * watch, output and changes must not overlap one another or app/store. Overlap
 * (including out=&watch.previous or changes inside a snapshot) returns -1
 * BEFORE ANY WRITE, leaving all objects unchanged. Non-NULL app initialized!=1
 * also leaves everything unchanged without inspecting store. Other errors clear
 * supplied output/changes and leave watch unchanged. Never consume output on
 * nonzero return. All non-NULL pointers must identify
 * valid objects of the declared types; this is not an invalid-pointer probe. */
int pen_app_poll_activity(const pen_app*,pen_app_activity_watch*,
                          pen_app_activity_status*,unsigned *changes);
#endif
