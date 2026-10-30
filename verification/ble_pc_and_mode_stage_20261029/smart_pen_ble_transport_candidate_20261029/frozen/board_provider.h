#ifndef PEN_BOARD_PROVIDER_H
#define PEN_BOARD_PROVIDER_H
#include "pipeline.h"
/* APPLICATION CANDIDATE ABI, NOT a SC035HGS implementation.
 * Exactly one actor owns storage/pipeline. Provider may queue ISR events, but
 * callbacks below execute on that actor. poll must preserve capture ordering,
 * emit raw contact edges even without images and retain frame bytes until the
 * next poll. Return0 event,1 idle,-1 fatal. Never relabel synthetic frames SENSOR.
 * Idle must mean no queued older frame/edge; actor then emits a timer-only poll.
 * security reads actual BLE connection policy; ACK payload is not authorization.
 * Connection and approval-policy events must be serialized with this actor.
 * Connection epoch must never repeat across reconnects OR device boots, and
 * never be taken from untrusted data. Persistent allocator/validated nonce
 * ownership belongs to the real provider; no cross-boot BLE proof is supplied.
 * send_packet must check its expected epoch atomically with queue acceptance.
 * ACK carries captured receipt security; actor also requires same current link.
 * Final sleep action must atomically recheck pressure/IRQ, arm compatible wake
 * sources, stop capture safely and handle a racing event. Deep-sleep success
 * normally never returns. A veto/failure returns nonzero; actor safely stops
 * and requires a fresh durable session, never reuses revoked tickets.
 * apply_actions implements reviewed wake/IRQ/sleep GPIO logic, never inferred
 * from old camera30pin labels. It must safely handle partial power-up failures.
 */
typedef struct {
 uint32_t device_id;
 uint32_t max_sleep_quiesce_us; /* bounded flush/cancel timeout, qualified board policy */
 pen_app_config config;
 void *ctx;
 int (*poll)(void*,pen_app_input*);
 int (*apply_actions)(void*,unsigned);
 int (*pending_transactions)(void*); /*0 all external writes committed,1 busy,-1 fatal; NOT durable backlog*/
 int (*quiesce_transport)(void*); /*0 quiet,1 waiting,-1 fatal; drain/cancel in-flight work, not stored backlog*/
 /* Called after transport quiet, before erase: atomically verify current
  * pressure/IRQ released AND no queued edge/frame/transaction. On1 hold capture
  * inhibited until resume_transport; queue later edges without dropping them.
  *0 race/busy: cancel maintenance, -1 fault. Real hardware binding absent. */
 int (*maintenance_idle_guard)(void*);
 int (*resume_transport)(void*); /* cancel quiesce when new contact/pickup arrives */
 int (*link_security)(void*,pen_link_security*);
 pen_packet_sender send_packet; /*0 accepted to expected link,1 busy/changed link,-1 fault*/
 int (*next_ack)(void*,uint64_t*,uint32_t*,pen_link_security*); /* receipt-time security and connection epoch;0 one ACK,1 none,-1 fault */
 /* Required status sink: start/stop/fault/sleep-prepared notifications. Must
  * drive a local indicator or authenticated transport/UI policy; not silence a
  * full log while pretending writing continues. Does not implement that UI. */
 void (*report_status)(void*,const pen_app_status*,int actor_error);
 /* Stop capture/LED only; retain authenticated replay transport in full-log mode. */
 int (*stop_capture)(void*);
 void (*safe_stop)(void*);
} pen_board_provider;
/* Returns NULL in checked-in provider. The integration does not fabricate
 * actual camera, GPIO, low-power, radio, calibration or Flash partition data. */
const pen_board_provider *pen_get_board_provider(void);
#endif
