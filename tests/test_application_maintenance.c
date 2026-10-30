#include "pipeline.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"maintenance line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t bytes[64*32];static int intent,erase_failure,erases;
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;CHECK(o+n<=sizeof bytes);memcpy(b,bytes+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;CHECK(o+n<=sizeof bytes);for(size_t i=0;i<n;i++)bytes[o+i]&=b[i];return 0;}
static int sync_log(void*c){(void)c;return 0;}
static int get(void*c,int*v){(void)c;*v=intent;return 0;}
static int set(void*c,int v){(void)c;intent=v;return 0;}
static int erase(void*c){(void)c;erases++;if(erase_failure){memset(bytes,255,64);return -1;}memset(bytes,255,sizeof bytes);return 0;}
static int send_packet(void*c,const uint8_t*b,size_t n,uint64_t epoch){(void)c;(void)b;CHECK(n==48&&epoch);return 0;}
static pen_store store;static pen_app app;static pen_roi_workspace workspace;
static pen_app_config config={.paper={710,1000,0,0},.contact={.press_us=0,.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=5000,.idle_us=10000,.min_confidence=750},.max_frame_gap_us=2000};
static pen_link_security link={1,1,1,1,7};
static void setup(int acked){
 memset(bytes,255,sizeof bytes);intent=erase_failure=erases=0;memset(&store,0,sizeof store);
 store.log=(pen_log){.read=rd,.program=wr,.sync=sync_log,.slots=32};store.get_erase_intent=get;store.set_erase_intent=set;store.erase_all=erase;
 CHECK(!pen_store_open(&store,42));
 for(uint64_t session=1;session<=32;session++){
  CHECK(!pen_store_begin(&store,session));pen_sample p={.timestamp_us=session};CHECK(!pen_store_append(&store,&p,&p));pen_store_stop(&store);
  if(acked){CHECK(!pen_store_offer(&store,&p));CHECK(!pen_store_ack(&store,p.session,p.seq,1));}
 }
 CHECK(store.session_count==32&&pen_app_needs_maintenance(&store));
 CHECK(!pen_app_init_replay(&app,&store,&workspace,&config));
}
int main(void){
 setup(1);CHECK(pen_app_reclaim(&app,0,1,0,1)==1);CHECK(pen_app_reclaim(&app,1,0,0,1)==1);
 CHECK(pen_app_reclaim(&app,1,1,1,1)==1);CHECK(pen_app_reclaim(&app,1,1,0,0)==1);CHECK(!erases);
 CHECK(!pen_app_reclaim(&app,1,1,0,1));CHECK(erases==1&&!intent&&!store.session_count&&!store.log.next);
 CHECK(pen_app_offer(&app,&link,send_packet,NULL)==-3);
 /* Epoch33 represents caller's durable allocator; actor test covers that binding. */
 CHECK(!pen_store_begin(&store,33));CHECK(!pen_app_init(&app,&store,&workspace,&config));
 pen_sample p={0};CHECK(!pen_store_append(&store,&p,&p));CHECK(p.session==33&&p.seq==0);
 CHECK(!pen_app_offer(&app,&link,send_packet,NULL));CHECK(pen_app_ack(&app,&link,&link,1,0)==-3);
 CHECK(!pen_app_ack(&app,&link,&link,33,0));
 setup(0);CHECK(pen_app_reclaim(&app,1,1,0,1)==-3);CHECK(!erases&&store.log.next==32);
 pen_app_result result;pen_app_input input={0};CHECK(pen_app_step(&app,&input,&result)==-1);
 for(uint64_t session=1;session<=32;session++){
  CHECK(!pen_app_offer(&app,&link,send_packet,NULL));CHECK(!pen_app_ack(&app,&link,&link,session,0));
 }
 CHECK(!pen_app_reclaim(&app,1,1,0,1));CHECK(erases==1);
 setup(0);CHECK(pen_app_prepare_replay_sleep(&app,1,1,1,1)==1);
 CHECK(!pen_app_prepare_replay_sleep(&app,1,1,0,1));CHECK(!erases&&store.log.next==32);
 CHECK(pen_app_offer(&app,&link,send_packet,NULL)==-3);
 CHECK(!pen_store_open(&store,42));CHECK(!pen_app_init_replay(&app,&store,&workspace,&config));
 CHECK(!pen_app_offer(&app,&link,send_packet,NULL));CHECK(pen_app_ack(&app,&link,&link,32,0)==-3);
 CHECK(!pen_app_ack(&app,&link,&link,1,0));
 setup(1);erase_failure=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-1);CHECK(intent&&store.log.faulted);
 CHECK(pen_app_offer(&app,&link,send_packet,NULL)==-1);
 erase_failure=0;CHECK(!pen_store_open(&store,42));CHECK(!intent&&!store.log.next&&erases==2);
 CHECK(!pen_store_begin(&store,33));CHECK(!pen_app_init(&app,&store,&workspace,&config));
 CHECK(pen_app_ack(&app,&link,&link,32,0)==-3);
 puts("maintenance:32 ACK sessions reclaimed; unACK retained/replayed; dirty/contact gates; erase power-loss intent; new session staleACK rejection PASS");return 0;
}
