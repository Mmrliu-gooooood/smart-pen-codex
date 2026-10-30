#include "recorder.h"
#include <string.h>
int pen_recorder_init(pen_recorder*r,pen_store*s,const pen_cp_config*c){
 if(!r||!s||!s->recording||s->log.faulted)return -1;
 memset(r,0,sizeof(*r));r->store=s;return pen_cp_init(&r->contact,c);
}
int pen_recorder_step(pen_recorder*r,const pen_cp_input*i,const pen_sample*p,pen_recorder_result*out){
 if(!r||!i||!p||!out)return -1;
 memset(out,0,sizeof(*out));if(r->faulted||!r->store->recording){out->storage_error=-1;return -1;}
 pen_sample template=*p;template.device=r->store->device;template.session=r->store->recording_session;
 pen_cp_output contact;int error=pen_cp_step(&r->contact,i,&template,&contact);
 if(error){out->input_error=error;r->faulted=1;pen_store_stop(r->store);return error;}
 out->actions=contact.actions;out->contact_faults=contact.faults;out->raw_down_us=contact.raw_down_us;
 for(unsigned n=0;n<contact.count;n++){
  pen_sample durable;error=pen_store_append(r->store,&contact.events[n],&durable);
  if(error){out->storage_error=error;out->actions&=~PEN_CP_SLEEP_REQUEST;r->faulted=1;pen_store_stop(r->store);return error;}
  out->recorded++;
 }
 return 0;
}
