#ifndef PEN_APPLICATION_PIPELINE_H
#define PEN_APPLICATION_PIPELINE_H
#include "recorder.h"
#include "roi_opt.h"
/* Single actor, never ISR/reentrant. Caller owns workspace and frame bytes for
 * duration of step. No sensor/GPIO/clock/BLE/OTA configuration occurs here. */
enum pen_frame_origin { PEN_FRAME_UNKNOWN=0, PEN_FRAME_SENSOR=1, PEN_FRAME_SYNTHETIC=2 };
typedef struct {
 const uint8_t *gray; size_t length; unsigned width,height,stride;
 uint64_t timestamp_us, frame_id; uint32_t source_id;
 enum pen_frame_origin origin;
} pen_app_frame;
typedef struct {
 uint64_t timestamp_us,frame_id;
 uint32_t source_id,calibration_revision,page;
 int32_t x_um,y_um;
 uint16_t confidence;
 uint8_t pose_valid;
} pen_tip_solution;
/* Mapping MUST solve physical tip pose in paper coordinates from calibrated
 * optics/axis and current frame, not multiply decoded window origin by pitch.
 * It must independently validate contact/pose and reject ambiguous/extrapolated
 * results. No such SC035HGS mapper is supplied. Metadata is a consistency gate,
 * not cryptographic proof of calibration or physical qualification. */
typedef int (*pen_tip_mapper)(void*,const pen_app_frame*,const pen_roi_opt_result*,pen_tip_solution*);
typedef struct {
 pen_roi_config paper;
 pen_cp_config contact;
 uint32_t source_id,calibration_revision,page;
 uint64_t max_frame_gap_us;
 int32_t min_x_um,max_x_um,min_y_um,max_y_um;
 uint8_t camera_qualified; /* explicit deployment gate; zero-initialized is OFF */
 pen_tip_mapper map_tip; void *map_ctx;
} pen_app_config;
enum pen_app_diagnostic {
 PEN_APP_NO_FRAME=1, PEN_APP_UNQUALIFIED=2, PEN_APP_BAD_FRAME=4,
 PEN_APP_DECODE_FAILED=8, PEN_APP_MAPPING_REJECTED=16, PEN_APP_STALE=32
};
typedef struct {
 uint64_t now_us;
 uint8_t raw_contact,pickup_irq_low,camera_ready,storage_pending,usb_sleep_allowed;
 /* storage_pending means genuine uncommitted external transactions, NOT durable backlog. */
 const pen_app_frame *frame; /* NULL: contact/timer-only poll */
} pen_app_input;
typedef struct {
 unsigned diagnostics; int decode_status;
 uint8_t decoded,tip_accepted;
 pen_roi_opt_result window; /* diagnostic only; NEVER an ink coordinate */
 pen_recorder_result recorder;
} pen_app_result;
typedef struct {
 pen_app_config config; pen_recorder recorder; pen_roi_workspace *workspace;
 uint64_t last_frame_us,last_frame_id;
 int last_error; unsigned last_contact_faults;
 uint64_t sent_epoch,sent_session; uint32_t sent_seq;
 uint8_t seen_frame,initialized,sent_pending,sleep_prepared,replay_only;
} pen_app;
int pen_app_init(pen_app*,pen_store*,pen_roi_workspace*,const pen_app_config*);
/* Capacity-only mode: opened healthy store, no recording; no frames accepted. */
int pen_app_init_replay(pen_app*,pen_store*,pen_roi_workspace*,const pen_app_config*);
int pen_app_needs_maintenance(const pen_store*);
/* Explicit idle maintenance; 0 reclaimed,1 deferred,-1 fault,-3 unACK/unsafe.
 * Only capacity replay or sleep-prepared mode; no arbitrary fault recovery.
 * Caller must durably allocate a NEW session before initializing recording. */
int pen_app_reclaim(pen_app*,int pressure_released,int irq_released,int pending_transactions,int transport_quiesced);
/* Rejected frames still enter contact machine as invalid observations, so loss
 * breaks the stroke. Call on every contact edge/timer; do not wait for a frame.
 * Current synchronous adapter requires frame timestamp == event timestamp.
 * Async capture requires an ordered queue outside this module. */
int pen_app_step(pen_app*,const pen_app_input*,pen_app_result*);
typedef struct {
 size_t slots_used,slots_total; unsigned sessions;
 uint32_t device;uint64_t recording_session;
 int last_error;unsigned contact_faults;
 uint8_t recording,storage_fault,sleep_prepared,replay_only;
} pen_app_status;
int pen_app_get_status(const pen_app*,pen_app_status*);
/* Exact stored record replay. Delivery acceptance does not ACK/erase. All four
 * security facts must come from actual authenticated link policy, not packet
 * payload. BLE GATT/radio fragmentation belongs to a transport adapter. */
typedef struct {uint8_t encrypted,authenticated,bonded,approved_peer; uint64_t connection_epoch;} pen_link_security;
/* Adapter must atomically reject a changed link before accepting the packet. */
typedef int (*pen_packet_sender)(void*,const uint8_t*,size_t,uint64_t expected_connection_epoch);
/*1 pending,0 none,-1 read failure; never arms a store ACK offer. */
int pen_app_pending(pen_app*);
/* 0 durable barrier + tickets revoked + session stopped,1 defer,-1 fault.
 * Only after contact machine requests idle sleep. Durable backlog is retained. */
/* Cancel logical sleep before hardware sleep, e.g. latest USB policy veto. */
int pen_app_cancel_sleep(pen_app*,uint64_t now_us);
int pen_app_prepare_sleep(pen_app*,int pending_transactions,int transport_quiesced);
/* Capacity-only idle path; actor supplies current physical idle after timeout. */
int pen_app_prepare_replay_sleep(pen_app*,int pressure_released,int irq_released,int pending_transactions,int transport_quiesced);
int pen_app_offer(pen_app*,const pen_link_security*,pen_packet_sender,void*);
int pen_app_ack(pen_app*,const pen_link_security *current,const pen_link_security *receipt,
                uint64_t session,uint32_t seq);
#endif
