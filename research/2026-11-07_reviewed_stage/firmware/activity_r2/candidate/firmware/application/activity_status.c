#include "activity_status.h"
#include <string.h>

/* Address differences avoid overflowing an end-address calculation. uintptr_t
 * address ordering is supported by the host/ESP-IDF targets; no pointer order
 * comparison or subtraction between unrelated C objects is performed. */
static int overlaps(const void*p,size_t pn,const void*q,size_t qn){
 if(!p||!q)return 0;
 uintptr_t x=(uintptr_t)p,y=(uintptr_t)q;
 return x<=y?y-x<pn:x-y<qn;
}
static int overlaps_input(const pen_app*a,const void*p,size_t n){
 if(overlaps(p,n,a,sizeof(*a)))return 1;
 return a&&a->initialized&&overlaps(p,n,a->recorder.store,sizeof(pen_store));
}
int pen_app_get_activity_status(const pen_app*a,pen_app_activity_status*out){
 if(!out)return -1;
 /* A failed init may leave store indeterminate or retain a prior store. Do
  * not inspect that pointer, or clear a potentially aliased output, then. */
 if(a&&a->initialized!=1)return -1;
 if(overlaps_input(a,out,sizeof(*out)))return -1;
 memset(out,0,sizeof(*out));
 if(!a||!a->initialized||!a->recorder.store)return -1;
 const pen_cp*c=&a->recorder.contact;
 const pen_store*s=a->recorder.store;
 if(c->phase<PEN_CP_ASLEEP||c->phase>PEN_CP_FAULT||
    c->raw>1||c->confirmed>1||c->lost>1||c->started>1||
    c->buffered_count>PEN_CP_BUFFER||s->session_count>PEN_STORE_MAX_SESSIONS)
  return -1;
 pen_app_activity_status v={0};
 if(pen_app_get_status(a,&v.legacy))return -1;
 v.version=PEN_APP_ACTIVITY_VERSION;v.logical_phase=c->phase;
 v.event_known=c->started;v.last_event_us=c->started?c->last_us:0;
 v.last_raw_contact=c->raw;v.last_contact_confirmed=c->confirmed;
 v.preconfirm_count=(uint8_t)c->buffered_count;v.gap_required=c->lost;
 if(s->session_count){
  unsigned k=s->session_count-1;
  v.durable_reference_known=1;v.durable_reference_session=s->sessions[k];
  v.durable_reference_seq=s->last_seq[k];
 }
 /* Capacity exhaustion latches recorder.faulted too, but is replay-only,
  * not an I/O fault. A later real fault still takes precedence over replay. */
 int capacity=a->replay_only==1&&a->last_error==-2;
 int fault=s->log.faulted||a->last_contact_faults||c->faults||
     c->phase==PEN_CP_FAULT||(a->last_error&&!capacity)||
     (a->recorder.faulted&&!capacity);
 if(fault)v.activity=PEN_ACTIVITY_FAULT;
 else if(a->sleep_prepared)v.activity=PEN_ACTIVITY_SLEEP_PREPARED;
 else if(a->replay_only)v.activity=PEN_ACTIVITY_REPLAY_ONLY;
 else if(!s->recording)v.activity=PEN_ACTIVITY_BLOCKED;
 else {
  v.pipeline_ready=(uint8_t)(c->phase==PEN_CP_READY);
  if(c->raw){
   if(!c->confirmed)v.activity=PEN_ACTIVITY_CONFIRMING;
   else if(c->phase!=PEN_CP_READY||c->lost)v.activity=PEN_ACTIVITY_CONTACT_GAP;
   else v.activity=PEN_ACTIVITY_TRACKING;
  }else if(c->phase==PEN_CP_READY)v.activity=PEN_ACTIVITY_READY;
  else if(c->phase==PEN_CP_WAKING)v.activity=PEN_ACTIVITY_PREPARING;
  else v.activity=PEN_ACTIVITY_LOGICAL_ASLEEP;
 }
 *out=v;return 0;
}

static int state_changed(const pen_app_activity_status*a,const pen_app_activity_status*b){
 return a->activity!=b->activity||a->logical_phase!=b->logical_phase||
  a->event_known!=b->event_known||a->last_raw_contact!=b->last_raw_contact||
  a->last_contact_confirmed!=b->last_contact_confirmed||
  a->gap_required!=b->gap_required||a->pipeline_ready!=b->pipeline_ready||
  a->legacy.device!=b->legacy.device||
  a->legacy.recording_session!=b->legacy.recording_session||
  a->legacy.recording!=b->legacy.recording||
  a->legacy.last_error!=b->legacy.last_error||
  a->legacy.contact_faults!=b->legacy.contact_faults||
  a->legacy.storage_fault!=b->legacy.storage_fault||
  a->legacy.sleep_prepared!=b->legacy.sleep_prepared||
  a->legacy.replay_only!=b->legacy.replay_only;
}
int pen_app_poll_activity(const pen_app*a,pen_app_activity_watch*w,
                          pen_app_activity_status*out,unsigned*changes){
 if(a&&a->initialized!=1)return -1;
 /* Reject overlap BEFORE clearing outputs or touching the saved baseline.
  * On alias errors no output can safely be cleared: it may be input/watch. */
 if(overlaps(w,sizeof(*w),out,sizeof(*out))||
    overlaps(w,sizeof(*w),changes,sizeof(*changes))||
    overlaps(out,sizeof(*out),changes,sizeof(*changes))||
    overlaps_input(a,w,sizeof(*w))||overlaps_input(a,out,sizeof(*out))||
    overlaps_input(a,changes,sizeof(*changes)))return -1;
 if(out)memset(out,0,sizeof(*out));
 if(changes)*changes=0;
 if(!w||w->initialized>1||!out||!changes)return -1;
 pen_app_activity_status v;
 if(pen_app_get_activity_status(a,&v))return -1;
 unsigned mask=0;
 if(!w->initialized)mask=PEN_ACTIVITY_INITIAL;
 else {
  if(state_changed(&w->previous,&v))mask|=PEN_ACTIVITY_STATE_CHANGED;
  if(w->previous.durable_reference_known!=v.durable_reference_known||
     w->previous.durable_reference_session!=v.durable_reference_session||
     w->previous.durable_reference_seq!=v.durable_reference_seq)
   mask|=PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED;
 }
 *out=v;*changes=mask;w->previous=v;w->initialized=1;return 0;
}
