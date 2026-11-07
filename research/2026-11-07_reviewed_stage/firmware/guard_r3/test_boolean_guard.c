#include "pipeline.h"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} } while(0)
/* All timing, storage and readiness facts below are SYNTHETIC HOST FIXTURES. */
static const pen_cp_config cfg={.press_us=10,.camera_timeout_us=100000,
 .contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750};
static uint8_t flash[16*64];
static unsigned reads,writes,syncs,maps;
static pen_roi_workspace workspace;
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;reads++;if(o>sizeof flash||n>sizeof flash-o)return -1;memcpy(b,flash+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;writes++;if(o>sizeof flash||n>sizeof flash-o)return -1;for(size_t k=0;k<n;k++){if((flash[o+k]&b[k])!=b[k])return -1;flash[o+k]&=b[k];}return 0;}
static int sy(void*c){(void)c;syncs++;return 0;}
static int mapper(void*c,const pen_app_frame*f,const pen_roi_opt_result*r,pen_tip_solution*t){(void)c;(void)f;(void)r;(void)t;maps++;return -1;}
static void start(pen_app*a,pen_store*s){
 memset(flash,255,sizeof flash);*s=(pen_store){.log={.read=rd,.program=wr,.sync=sy,.slots=16}};
 CHECK(pen_store_open(s,42)==0);CHECK(pen_store_begin(s,7)==0);
 pen_sample durable={.timestamp_us=0,.flags=PEN_GAP};
 CHECK(pen_store_append(s,&durable,&durable)==0);
 pen_app_config c={.paper={710,1000,0,0},.contact=cfg,.source_id=17,
  .calibration_revision=7,.page=99,.max_frame_gap_us=2000,
  .min_x_um=-1000,.max_x_um=1000,.min_y_um=-1000,.max_y_um=1000,
  .camera_qualified=1,.map_tip=mapper};
 CHECK(pen_app_init(a,s,&workspace,&c)==0);
 pen_app_input i={.now_us=100,.pickup_irq_low=1,.camera_ready=1,.usb_sleep_allowed=1};
 pen_app_result r;CHECK(pen_app_step(a,&i,&r)==0);
 i.now_us=200;i.pickup_irq_low=0;CHECK(pen_app_step(a,&i,&r)==0);
 CHECK(a->recorder.contact.phase==PEN_CP_READY&&s->log.next==1);
 reads=writes=syncs=maps=0;
}
static const size_t cp_offsets[]={offsetof(pen_cp_input,usb_sleep_allowed),
 offsetof(pen_cp_input,raw_contact),offsetof(pen_cp_input,pickup_irq_low),
 offsetof(pen_cp_input,camera_ready),offsetof(pen_cp_input,storage_pending),
 offsetof(pen_cp_input,calibrated),offsetof(pen_cp_input,has_observation),offsetof(pen_cp_input,recover_fault)};
static const size_t app_offsets[]={offsetof(pen_app_input,usb_sleep_allowed),
 offsetof(pen_app_input,raw_contact),offsetof(pen_app_input,pickup_irq_low),
 offsetof(pen_app_input,camera_ready),offsetof(pen_app_input,storage_pending)};
static void cp_tests(void){
 pen_sample p={.device=42,.session=7};
 for(unsigned field=0;field<8;field++)for(unsigned value=2;value<=255;value++){
  pen_cp s;pen_cp_output o;CHECK(pen_cp_init(&s,&cfg)==0);
  pen_cp_input i={.now_us=100,.pickup_irq_low=1,.camera_ready=1,.usb_sleep_allowed=1};p.timestamp_us=100;
  CHECK(pen_cp_step(&s,&i,&p,&o)==0);
  i.now_us=200;i.pickup_irq_low=0;p.timestamp_us=200;CHECK(pen_cp_step(&s,&i,&p,&o)==0);
  pen_cp before=s;i.now_us=10200;p.timestamp_us=10200;
  ((uint8_t*)&i)[cp_offsets[field]]=(uint8_t)value;memset(&o,0xa5,sizeof o);
  int e=pen_cp_step(&s,&i,&p,&o);
  if(e!=-1)fprintf(stderr,"CP accepted malformed field=%u byte=%u rc=%d actions=%u phase=%d\n",field,value,e,o.actions,(int)s.phase);
  CHECK(e==-1);CHECK(!memcmp(&s,&before,sizeof s));
  CHECK(o.count==0&&o.actions==0&&o.faults==0);
 }
 /* All 2^8 legal combinations still enter the existing state machine. */
 for(unsigned mask=0;mask<256;mask++){
  pen_cp s;pen_cp_output o;CHECK(pen_cp_init(&s,&cfg)==0);
  pen_cp_input i={.now_us=1};p.timestamp_us=1;
  for(unsigned k=0;k<8;k++)((uint8_t*)&i)[cp_offsets[k]]=(uint8_t)((mask>>k)&1u);
  CHECK(pen_cp_step(&s,&i,&p,&o)==0);
 }
 puts("boolean CP: 2032 invalid bytes rejected without state/action changes; 256 legal combinations PASS");
}
static void app_tests(void){
 for(unsigned field=0;field<5;field++)for(unsigned value=2;value<=255;value++){
  pen_app a;pen_store s;start(&a,&s);uint8_t retained[sizeof flash];memcpy(retained,flash,sizeof flash);
  pen_cp before=a.recorder.contact;
  pen_app_input i={.now_us=10200,.camera_ready=1,.usb_sleep_allowed=1};
  /* Supply a real frame descriptor with intentionally undecodable bytes: an
   * invalid fact must be rejected BEFORE consuming its identity or decoding. */
  uint8_t pixel=0;
  pen_app_frame f={.gray=&pixel,.length=1,.width=1,.height=1,.stride=1,
   .timestamp_us=10200,.frame_id=1,.source_id=17,.origin=PEN_FRAME_SENSOR};
  if(field!=0)i.frame=&f; /* first case isolates unsafe idle USB permission */
  ((uint8_t*)&i)[app_offsets[field]]=(uint8_t)value;
  pen_app_result r;memset(&r,0xa5,sizeof r);int e=pen_app_step(&a,&i,&r);
  if(e!=-1)fprintf(stderr,"APP accepted malformed field=%u byte=%u rc=%d actions=%u recording=%u\n",field,value,e,r.recorder.actions,s.recording);
  CHECK(e==-1&&r.recorder.input_error==-1&&a.last_error==-1&&a.recorder.faulted&&!s.recording);
  CHECK(r.recorder.actions==0&&r.recorder.recorded==0&&!r.tip_accepted&&!r.decoded);
  CHECK(!a.seen_frame&&!memcmp(&a.recorder.contact,&before,sizeof before));
  CHECK(!reads&&!writes&&!syncs&&!maps&&s.log.next==1&&!memcmp(retained,flash,sizeof flash));
  pen_app_status status;CHECK(pen_app_get_status(&a,&status)==0&&status.last_error==-1&&!status.recording&&!status.storage_fault);
  i=(pen_app_input){.now_us=10300,.camera_ready=1,.usb_sleep_allowed=1};
  CHECK(pen_app_step(&a,&i,&r)==-1);CHECK(pen_app_prepare_sleep(&a,0,1)==-1);
  CHECK(!writes&&!syncs&&s.log.next==1&&!memcmp(retained,flash,sizeof flash));
 }
 for(unsigned mask=0;mask<32;mask++){
  pen_app a;pen_store s;start(&a,&s);pen_app_result r;pen_app_input i={.now_us=300};
  for(unsigned k=0;k<5;k++)((uint8_t*)&i)[app_offsets[k]]=(uint8_t)((mask>>k)&1u);
  CHECK(pen_app_step(&a,&i,&r)==0);
 }
 puts("boolean APP: 1270 invalid bytes fail closed before frame/storage effects; 32 legal combinations PASS");
}
int main(int argc,char**argv){
 CHECK(argc==2);
 if(!strcmp(argv[1],"cp"))cp_tests();else if(!strcmp(argv[1],"app"))app_tests();else CHECK(0);
 return 0;
}
