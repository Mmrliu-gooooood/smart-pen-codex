#ifndef PEN_STORE_H
#define PEN_STORE_H
#include "pen.h"
#define PEN_STORE_MAX_SESSIONS 32
/* All callbacks run under one caller-owned actor/mutex; never from an ISR.
   Intent callbacks MUST persist before returning. Erase callback may be retried
   after power loss. Keep recording disabled until open completes. */
typedef struct {
 pen_log log;
 void *meta_ctx;
 int (*get_erase_intent)(void *,int *);
 int (*set_erase_intent)(void *,int);
 int (*erase_all)(void *);
 uint64_t sessions[PEN_STORE_MAX_SESSIONS];
 uint32_t last_seq[PEN_STORE_MAX_SESSIONS];
 unsigned session_count;
 uint32_t device,next_seq;
 uint64_t recording_session;
 size_t replay_slot,offered_slot;
 pen_sample offered;
 uint8_t offering,recording,sequence_exhausted;
} pen_store;
/* 0 success; -1 I/O/corruption/invalid; -2 full; -3 unauthorized/mismatch.
   Open recovers a durable reclaim intent BEFORE permitting any recording. */
int pen_store_open(pen_store *s,uint32_t device);
int pen_store_begin(pen_store *s,uint64_t unique_boot_session);
int pen_store_append(pen_store *s,const pen_sample *observation,pen_sample *durable);
/* 0 offer immutable pending record, 1 nothing to replay, -1 failure. */
int pen_store_offer(pen_store *s,pen_sample *sample);
int pen_store_ack(pen_store *s,uint64_t session,uint32_t seq,int authenticated_peer);
/* Reclaim only when recording stopped, caller safety gate true, all committed
   records ACKed. Durable intent makes interrupted erase restartable. */
int pen_store_reclaim(pen_store *s,int safe_idle);
void pen_store_stop(pen_store *s);
#endif
