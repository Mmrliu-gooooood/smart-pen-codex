#include "contact_power.h"
#include <string.h>
int pen_cp_init(pen_cp *s,const pen_cp_config *c){
 if(!s||!c||!c->camera_timeout_us||!c->contact_stuck_us||!c->irq_stuck_us||!c->idle_us||c->min_confidence>1000||c->press_us>=c->contact_stuck_us)return -1;
 memset(s,0,sizeof(*s));s->config=*c;s->lost=1;return 0;
}
static void control(pen_cp_output *o,const pen_sample *p,unsigned flags){
 pen_sample q=*p;q.flags=(uint8_t)flags;q.page=0;q.x_um=0;q.y_um=0;q.confidence=0;
 o->events[o->count++]=q;
}
static pen_sample gated(pen_cp *s,const pen_cp_input *i,const pen_sample *p){
 pen_sample q=*p;q.flags=(uint8_t)((q.flags&PEN_GAP)|PEN_CONTACT);
 if(i->has_observation&&i->calibrated&&i->camera_ready&&p->page&&p->confidence>=s->config.min_confidence&&(p->flags&PEN_VALID))q.flags|=PEN_VALID;
 if(!(q.flags&PEN_VALID)){q.page=0;q.x_um=0;q.y_um=0;q.confidence=0;s->lost=1;}
 else if(s->lost){q.flags|=PEN_GAP;s->lost=0;}
 return q;
}
static void fault(pen_cp *s,pen_cp_output *o,const pen_sample *p,unsigned reason){
 if(s->phase!=PEN_CP_FAULT)control(o,p,PEN_GAP);
 s->phase=PEN_CP_FAULT;s->faults|=reason;s->confirmed=0;s->buffered_count=0;s->lost=1;
}
int pen_cp_step(pen_cp *s,const pen_cp_input *i,const pen_sample *p,pen_cp_output *o){
 if(!s||!i||!p||!o||p->timestamp_us!=i->now_us||!p->session||p->confidence>1000||(p->flags&~7u))return -1;
 memset(o,0,sizeof(*o));
 if(s->started&&i->now_us<s->last_us)fault(s,o,p,PEN_CP_CLOCK);
 if(!s->started){s->started=1;s->last_us=i->now_us;s->activity_us=i->now_us;}
 if(s->phase==PEN_CP_FAULT){
  /* Clock faults require an explicit new boot/reset, not a local timestamp fix. */
  if(i->recover_fault&&!(s->faults&PEN_CP_CLOCK)&&!i->raw_contact&&!i->pickup_irq_low&&!i->storage_pending&&i->usb_sleep_allowed){
   s->phase=PEN_CP_ASLEEP;s->faults=0;s->raw=0;s->irq=0;s->activity_us=i->now_us;
  }
  s->last_us=i->now_us;o->faults=s->faults;o->raw_down_us=s->down_us;return 0;
 }
 s->last_us=i->now_us;
 if(i->pickup_irq_low&&!s->irq){s->irq_us=i->now_us;s->activity_us=i->now_us;o->actions|=PEN_CP_CLEAR_PICKUP;}
 s->irq=!!i->pickup_irq_low;
 if(s->irq&&i->now_us-s->irq_us>=s->config.irq_stuck_us)fault(s,o,p,PEN_CP_IRQ_STUCK);
 if(i->raw_contact&&!s->raw){s->down_us=i->now_us;s->buffered_count=0;s->lost=1;s->activity_us=i->now_us;}
 if(i->raw_contact&&i->now_us-s->down_us>=s->config.contact_stuck_us)fault(s,o,p,PEN_CP_CONTACT_STUCK);
 if(s->phase==PEN_CP_FAULT){s->raw=!!i->raw_contact;o->faults=s->faults;o->raw_down_us=s->down_us;return 0;}
 if((i->raw_contact||i->pickup_irq_low)&&s->phase==PEN_CP_ASLEEP){s->phase=PEN_CP_WAKING;s->wake_us=i->now_us;o->actions|=PEN_CP_WAKE_CAMERA;}
 if(s->phase==PEN_CP_READY&&!i->camera_ready){s->phase=PEN_CP_WAKING;s->wake_us=i->now_us;}
 if(s->phase==PEN_CP_WAKING){
  if(i->camera_ready)s->phase=PEN_CP_READY;
  else if(i->now_us-s->wake_us>=s->config.camera_timeout_us){fault(s,o,p,PEN_CP_CAMERA_TIMEOUT);o->faults=s->faults;return 0;}
 }
 if(!i->raw_contact&&s->raw){
  /* Release bypasses debounce. A short tap is explicitly missing, never invented. */
  control(o,p,s->confirmed?0:PEN_GAP);s->confirmed=0;s->buffered_count=0;s->lost=1;s->activity_us=i->now_us;
 }else if(i->raw_contact){
  s->activity_us=i->now_us;
  if(!s->confirmed){
   if(i->has_observation||!s->raw){
    if(s->buffered_count==PEN_CP_BUFFER){s->buffered_count=0;s->lost=1;control(o,p,PEN_CONTACT|PEN_GAP);}
    s->buffered[s->buffered_count++]=gated(s,i,p);
   }
   if(i->now_us-s->down_us>=s->config.press_us){
    s->confirmed=1;
    for(unsigned n=0;n<s->buffered_count;n++)o->events[o->count++]=s->buffered[n];
    s->buffered_count=0;
   }
  }else if(i->has_observation){o->events[o->count++]=gated(s,i,p);}
  else if(!i->camera_ready&&!s->lost){control(o,p,PEN_CONTACT|PEN_GAP);s->lost=1;}
 }
 s->raw=!!i->raw_contact;
 if(s->phase==PEN_CP_READY&&!s->raw&&!s->irq&&!s->confirmed&&!s->buffered_count&&!i->storage_pending&&i->usb_sleep_allowed&&i->now_us-s->activity_us>=s->config.idle_us){
  o->actions|=PEN_CP_SLEEP_REQUEST;s->phase=PEN_CP_ASLEEP;
 }
 o->raw_down_us=s->down_us;o->contact_confirmed=s->confirmed;o->faults=s->faults;return 0;
}
