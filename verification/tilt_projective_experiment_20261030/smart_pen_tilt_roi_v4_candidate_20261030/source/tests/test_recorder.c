#include "recorder.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t bytes[64*4];
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;memcpy(b,bytes+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;for(size_t i=0;i<n;i++){assert((bytes[o+i]&b[i])==b[i]);bytes[o+i]&=b[i];}return 0;}
static int sync_flash(void*c){(void)c;return 0;}
int main(void){
 memset(bytes,255,sizeof bytes);pen_store s={.log={.read=rd,.program=wr,.sync=sync_flash,.slots=4}};
 assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,123));
 pen_cp_config config={.press_us=1000,.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750};
 pen_recorder r;assert(!pen_recorder_init(&r,&s,&config));pen_recorder_result result;
 pen_cp_input in={.now_us=100,.raw_contact=1,.camera_ready=1,.usb_sleep_allowed=1,.calibrated=1,.has_observation=1};
 pen_sample p={.timestamp_us=100,.page=1,.confidence=900,.flags=PEN_VALID,.x_um=100};
 assert(!pen_recorder_step(&r,&in,&p,&result)&&result.recorded==0);pen_sample q;assert(pen_store_offer(&s,&q)==1);
 in.now_us=p.timestamp_us=1100;p.x_um=200;assert(!pen_recorder_step(&r,&in,&p,&result)&&result.recorded==2);
 assert(!pen_store_offer(&s,&q)&&q.seq==0&&q.timestamp_us==100&&q.x_um==100&&(q.flags&PEN_VALID));assert(!pen_store_ack(&s,123,0,1));
 assert(!pen_store_offer(&s,&q)&&q.seq==1&&q.timestamp_us==1100);assert(!pen_store_ack(&s,123,1,1));
 in.now_us=p.timestamp_us=1200;in.raw_contact=0;assert(!pen_recorder_step(&r,&in,&p,&result)&&result.recorded==1);assert(!pen_store_offer(&s,&q)&&q.seq==2&&!(q.flags&PEN_CONTACT)&&!(q.flags&PEN_VALID));assert(!pen_store_ack(&s,123,2,1));
 in.now_us=p.timestamp_us=1300;in.raw_contact=1;assert(!pen_recorder_step(&r,&in,&p,&result));in.now_us=p.timestamp_us=2300;assert(pen_recorder_step(&r,&in,&p,&result)==-2);assert(result.recorded==1&&r.faulted&&!s.recording&&!(result.actions&PEN_CP_SLEEP_REQUEST));
 assert(!pen_store_offer(&s,&q)&&q.seq==3);assert(pen_recorder_step(&r,&in,&p,&result)==-1);
 /* A rejected observation must not reconnect valid points across its loss. */
 memset(bytes,255,sizeof bytes);s=(pen_store){.log={.read=rd,.program=wr,.sync=sync_flash,.slots=4}};
 assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,124));assert(!pen_recorder_init(&r,&s,&config));
 in.now_us=p.timestamp_us=100;in.raw_contact=1;assert(!pen_recorder_step(&r,&in,&p,&result));
 in.now_us=p.timestamp_us=1100;assert(!pen_recorder_step(&r,&in,&p,&result)&&result.recorded==2);
 in.now_us=1200;p.timestamp_us=1199;assert(pen_recorder_step(&r,&in,&p,&result)==-1&&result.input_error==-1&&r.faulted&&!s.recording);
 in.now_us=p.timestamp_us=1300;assert(pen_recorder_step(&r,&in,&p,&result)==-1&&s.log.next==2);
 puts("recorder pipeline: raw edge -> debounce -> durable sequence -> replay ACK + midburst FULL latch PASS");return 0;
}
