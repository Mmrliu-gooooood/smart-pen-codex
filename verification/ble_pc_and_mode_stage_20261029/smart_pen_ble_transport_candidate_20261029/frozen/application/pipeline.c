#include "pipeline.h"
#include <string.h>
static int secure(const pen_link_security*s){return s&&s->encrypted==1&&s->authenticated==1&&s->bonded==1&&s->approved_peer==1&&s->connection_epoch!=0;}
static int initialize(pen_app*a,pen_store*s,pen_roi_workspace*w,const pen_app_config*c,int replay){
 if(!a)return -1;
 a->initialized=0; /* failed reinitialization cannot leave previous run active */
 if(!s||!w||!c||!c->max_frame_gap_us||c->camera_qualified>1||
    c->min_x_um>c->max_x_um||c->min_y_um>c->max_y_um||
    (c->camera_qualified&&(!c->source_id||!c->calibration_revision||!c->page||!c->map_tip)))return -1;
 memset(a,0,sizeof(*a));a->config=*c;a->workspace=w;
 if(replay){
  if(s->recording||s->log.faulted||pen_cp_init(&a->recorder.contact,&c->contact))return -1;
  a->recorder.store=s;a->replay_only=1;a->last_error=-2;
 }else if(pen_recorder_init(&a->recorder,s,&c->contact))return -1;
 a->initialized=1;return 0;
}
int pen_app_init(pen_app*a,pen_store*s,pen_roi_workspace*w,const pen_app_config*c){return initialize(a,s,w,c,0);}
int pen_app_init_replay(pen_app*a,pen_store*s,pen_roi_workspace*w,const pen_app_config*c){return initialize(a,s,w,c,1);}
int pen_app_needs_maintenance(const pen_store*s){
 return s&&(s->log.next>=s->log.slots||s->session_count>=PEN_STORE_MAX_SESSIONS);
}
int pen_app_reclaim(pen_app*a,int pressure,int irq,int pending,int quiet){
 if(!a||!a->initialized||(!a->replay_only&&!a->sleep_prepared))return -3;
 pen_store*s=a->recorder.store;
 if(s->log.faulted||a->last_contact_faults||pending<0||quiet<0)return -1;
 if(pressure!=1||irq!=1||pending!=0||quiet!=1)return 1;
 if(!pen_app_needs_maintenance(s))return 1;
 if(s->recording)return -3;
 if(!s->log.sync||s->log.sync(s->log.ctx)){s->log.faulted=1;a->last_error=-1;return -1;}
 /* Quiescence is trusted actor/provider state, never peer-provided metadata. */
 a->sent_pending=0;s->offering=0;
 int e=pen_store_reclaim(s,1);
 if(e==0){a->sleep_prepared=1;return 0;}
 if(e==-1){s->log.faulted=1;a->last_error=-1;}
 return e;
}
static int solution_ok(const pen_app*a,const pen_app_frame*f,const pen_tip_solution*t){
 return t->pose_valid==1&&t->timestamp_us==f->timestamp_us&&t->frame_id==f->frame_id&&
 t->source_id==a->config.source_id&&t->calibration_revision==a->config.calibration_revision&&
 t->page==a->config.page&&t->confidence>=a->config.contact.min_confidence&&t->confidence<=1000&&
 t->x_um>=a->config.min_x_um&&t->x_um<=a->config.max_x_um&&
 t->y_um>=a->config.min_y_um&&t->y_um<=a->config.max_y_um;
}
int pen_app_step(pen_app*a,const pen_app_input*i,pen_app_result*r){
 if(!a||!a->initialized||a->sleep_prepared||a->replay_only)return -1;
 if(!i||!r){a->last_error=-1;a->recorder.faulted=1;pen_store_stop(a->recorder.store);return -1;}
 memset(r,0,sizeof(*r));r->decode_status=PEN_ROI_ARGUMENT;
 pen_sample p={.timestamp_us=i->now_us};
 const pen_app_frame*f=i->frame;
 int qualified=a->config.camera_qualified==1;
 if(!qualified)r->diagnostics|=PEN_APP_UNQUALIFIED;
 if(!f)r->diagnostics|=PEN_APP_NO_FRAME;
 else {
  int ordered=f->timestamp_us==i->now_us&&f->frame_id&&
      (!a->seen_frame||(f->frame_id>a->last_frame_id&&f->timestamp_us>a->last_frame_us));
  if(!ordered||!f->gray||f->source_id!=a->config.source_id||
     (f->origin!=PEN_FRAME_SENSOR&&f->origin!=PEN_FRAME_SYNTHETIC))r->diagnostics|=PEN_APP_BAD_FRAME;
  else {
   /* Consume accepted identity even if pixels cannot decode; duplicates cannot
    * later reuse the same capture identity to change a record. */
   a->seen_frame=1;a->last_frame_id=f->frame_id;a->last_frame_us=f->timestamp_us;
   r->decode_status=pen_roi_decode_opt(f->gray,f->length,f->width,f->height,f->stride,
        &a->config.paper,a->workspace,NULL,&r->window); /* cold, no weak warm uniqueness */
   if(r->decode_status)r->diagnostics|=PEN_APP_DECODE_FAILED;
   else {
    r->decoded=1;
    if(f->origin!=PEN_FRAME_SENSOR)r->diagnostics|=PEN_APP_UNQUALIFIED;
    else if(qualified&&i->raw_contact==1&&i->camera_ready==1){
     pen_tip_solution t={0};
     if(a->config.map_tip(a->config.map_ctx,f,&r->window,&t)||!solution_ok(a,f,&t))r->diagnostics|=PEN_APP_MAPPING_REJECTED;
     else {p.page=t.page;p.x_um=t.x_um;p.y_um=t.y_um;p.confidence=t.confidence;p.flags=PEN_VALID;r->tip_accepted=1;}
    }
   }
  }
 }
 int fresh=a->seen_frame&&i->now_us>=a->last_frame_us&&i->now_us-a->last_frame_us<=a->config.max_frame_gap_us;
 if(!fresh)r->diagnostics|=PEN_APP_STALE;
 pen_cp_input in={.now_us=i->now_us,.raw_contact=i->raw_contact,.pickup_irq_low=i->pickup_irq_low,
   .camera_ready=(uint8_t)(qualified&&i->camera_ready==1&&(fresh||!i->raw_contact)),
   .storage_pending=(uint8_t)(i->storage_pending||a->recorder.store->log.faulted||a->recorder.faulted),
   .usb_sleep_allowed=i->usb_sleep_allowed,.calibrated=r->tip_accepted,.has_observation=(uint8_t)(f!=NULL)};
 int e=pen_recorder_step(&a->recorder,&in,&p,&r->recorder);
 a->last_contact_faults=r->recorder.contact_faults;
 if(e){a->last_error=e;r->tip_accepted=0;
  if(e==-2&&!a->recorder.store->log.faulted&&!r->recorder.input_error&&!r->recorder.contact_faults)a->replay_only=1;
 }
 if(a->last_contact_faults){r->tip_accepted=0;pen_store_stop(a->recorder.store);}
 return e;
}
int pen_app_get_status(const pen_app*a,pen_app_status*out){
 if(!a||!a->initialized||!out)return -1;
 const pen_store*s=a->recorder.store;
 *out=(pen_app_status){.slots_used=s->log.next,.slots_total=s->log.slots,.sessions=s->session_count,
  .device=s->device,.recording_session=s->recording_session,.last_error=a->last_error,
  .contact_faults=a->last_contact_faults,.recording=s->recording,.storage_fault=s->log.faulted,
  .sleep_prepared=a->sleep_prepared,.replay_only=a->replay_only};return 0;
}
int pen_app_pending(pen_app*a){
 if(!a||!a->initialized)return -1;
 /* pen_store_offer only reads Flash but mutates its cursor/offer. A local copy
  * probes pending data without granting the real store ACK authority. */
 pen_store probe=*a->recorder.store;pen_sample p;int e=pen_store_offer(&probe,&p);
 if(e<0){a->last_error=-1;a->recorder.store->log.faulted=1;a->recorder.faulted=1;pen_store_stop(a->recorder.store);return -1;}
 return e==0?1:0;
}
int pen_app_cancel_sleep(pen_app*a,uint64_t now){
 if(!a||!a->initialized||a->sleep_prepared||a->replay_only||a->recorder.faulted)return -1;
 pen_cp*c=&a->recorder.contact;
 if(now<c->last_us)return -1;
 if(c->phase==PEN_CP_ASLEEP){c->phase=PEN_CP_READY;c->activity_us=now;}
 return 0;
}
int pen_app_prepare_sleep(pen_app*a,int pending,int quiet){
 if(!a||!a->initialized||a->sleep_prepared)return -1;
 pen_cp*c=&a->recorder.contact;pen_store*s=a->recorder.store;
 if(pending<0||quiet<0||a->recorder.faulted||s->log.faulted)return -1;
 if(pending!=0||quiet!=1||c->phase!=PEN_CP_ASLEEP||c->raw||c->irq||c->confirmed||c->buffered_count)return 1;
 if(!s->log.sync||s->log.sync(s->log.ctx)){
  a->last_error=-1;s->log.faulted=1;a->recorder.faulted=1;pen_store_stop(s);return -1;
 }
 a->sent_pending=0;s->offering=0;pen_store_stop(s);a->sleep_prepared=1;return 0;
}
int pen_app_prepare_replay_sleep(pen_app*a,int pressure,int irq,int pending,int quiet){
 if(!a||!a->initialized||!a->replay_only||a->sleep_prepared)return -1;
 pen_store*s=a->recorder.store;
 if(s->log.faulted||a->last_contact_faults||pending<0||quiet<0)return -1;
 if(pressure!=1||irq!=1||pending!=0||quiet!=1||s->recording)return 1;
 if(!s->log.sync||s->log.sync(s->log.ctx)){s->log.faulted=1;a->last_error=-1;return -1;}
 a->sent_pending=0;s->offering=0;a->sleep_prepared=1;return 0;
}
int pen_app_offer(pen_app*a,const pen_link_security*s,pen_packet_sender send,void*ctx){
 if(!a||!a->initialized||!send)return -1;
 if(a->sleep_prepared)return -3;
 if(!secure(s)){a->sent_pending=0;return -3;}
 if(a->sent_epoch!=s->connection_epoch)a->sent_pending=0;
 pen_sample p;int e=pen_store_offer(a->recorder.store,&p);
 if(e){a->sent_pending=0;return e;}
 uint8_t b[PEN_PACKET_SIZE];if(pen_encode(b,&p))return -1;
 e=send(ctx,b,sizeof b,s->connection_epoch);
 if(e==0){a->sent_pending=1;a->sent_epoch=s->connection_epoch;a->sent_session=p.session;a->sent_seq=p.seq;}
 else if(e<0)a->sent_pending=0;
 return e; /* busy never arms first ACK; prior accepted same-link send remains valid */
}
int pen_app_ack(pen_app*a,const pen_link_security*s,const pen_link_security*receipt,uint64_t session,uint32_t seq){
 if(!a||!a->initialized)return -1;
 if(a->sleep_prepared)return -3;
 if(!secure(s)||!secure(receipt)||s->connection_epoch!=receipt->connection_epoch||
    !a->sent_pending||a->sent_epoch!=s->connection_epoch||a->sent_session!=session||a->sent_seq!=seq)return -3;
 int e=pen_store_ack(a->recorder.store,session,seq,1);if(!e)a->sent_pending=0;return e;
}
