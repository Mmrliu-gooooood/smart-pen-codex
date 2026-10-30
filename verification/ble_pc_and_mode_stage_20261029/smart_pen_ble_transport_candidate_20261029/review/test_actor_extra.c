#include "pen_ble_actor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t flash[64*8];static int fail_sync,programs;static pen_store store;static pen_app app;static pen_roi_workspace workspace;static pen_ble_actor actor;static pen_ble_core core;static int mode,calls,reentry;static uint64_t now;
static int rd(void*x,size_t o,uint8_t*b,size_t n){(void)x;if(o+n>sizeof flash)return -1;memcpy(b,flash+o,n);return 0;}
static int wr(void*x,size_t o,const uint8_t*b,size_t n){(void)x;if(o+n>sizeof flash)return -1;programs++;for(size_t k=0;k<n;k++){if((flash[o+k]&b[k])!=b[k])return -1;flash[o+k]&=b[k];}return 0;}
static int sy(void*x){(void)x;return fail_sync?-1:0;}
static int notify(void*x,const uint8_t*b,size_t n,uint64_t e){(void)x;(void)b;CHECK(n==20&&e==77);calls++;return 0;}
static int sec(void*x,pen_link_security*s){(void)x;*s=core.security;return 0;}
static int send(void*x,const uint8_t*b,size_t n,uint64_t e){(void)x;return pen_ble_core_send(&core,b,n,e,++now,notify,NULL);}
static int authorize(void*x,const pen_ble_ticket*t,pen_ble_grant*g){(void)x;if(mode==1)pen_ble_core_link(&core,NULL,0);if(mode==5)reentry=pen_ble_actor_turn(&actor);int r=pen_ble_core_authorize(&core,t,g);if(!r){if(mode==2)pen_ble_core_link(&core,NULL,0);if(mode==3)g->ticket.nonce--;if(mode==4)app.sent_seq++;if(mode==6)g->ticket.app++;if(mode==7)g->authorized=2;}return r;}
static void put(uint8_t*p,uint64_t v,unsigned n){for(unsigned k=0;k<n;k++)p[k]=(uint8_t)(v>>(8*k));}
static void start(void){memset(flash,255,sizeof flash);programs=fail_sync=calls=mode=reentry=0;now=100;store=(pen_store){.log={.read=rd,.program=wr,.sync=sy,.slots=8}};CHECK(!pen_store_open(&store,12));CHECK(!pen_store_begin(&store,100));pen_app_config conf={.max_frame_gap_us=5000,.contact={.press_us=0,.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750}};CHECK(!pen_app_init(&app,&store,&workspace,&conf));pen_sample p={.timestamp_us=1},durable;CHECK(!pen_store_append(&store,&p,&durable));pen_ble_core_init(&core);pen_link_security s={1,1,1,1,77};pen_ble_core_link(&core,&s,16);pen_ble_core_subscribe(&core,1);pen_ble_backend b={NULL,sec,send,authorize};CHECK(!pen_ble_actor_init(&actor,&app,&b));}
static void queued(void){CHECK(!pen_ble_actor_turn(&actor)&&calls==3&&app.sent_pending);uint8_t ack[20];memcpy(ack,"AK\1\0",4);put(ack+4,100,8);put(ack+12,0,4);put(ack+16,pen_crc32(ack,16),4);CHECK(!pen_ble_core_receive(&core,ack,20,++now));}
int main(void){unsigned count=0;start();CHECK(pen_app_pending(&app)==1&&!store.offering&&!app.sent_pending);CHECK(pen_ble_actor_turn(&actor)==0&&app.sent_pending);CHECK(pen_app_pending(&app)==1);count++;
start();queued();mode=1;int old=programs;CHECK(pen_ble_actor_turn(&actor)==-3&&!actor.faulted&&programs==old&&pen_app_pending(&app)==1);count++;
start();queued();mode=2;old=programs;CHECK(pen_ble_actor_turn(&actor)==-3&&!actor.faulted&&programs>old&&pen_app_pending(&app)==0);old=programs;CHECK(pen_ble_actor_turn(&actor)==-3&&programs==old);count++;
for(int m=3;m<=7;m++){if(m==5)continue;start();queued();mode=m;old=programs;CHECK(pen_ble_actor_turn(&actor)==-1&&actor.faulted&&programs==old&&pen_app_pending(&app)==1);CHECK(pen_ble_actor_turn(&actor)==-1&&programs==old);count++;}
start();queued();mode=5;CHECK(pen_ble_actor_turn(&actor)==1&&reentry==-1&&!actor.faulted&&pen_app_pending(&app)==0);count++;
start();queued();fail_sync=1;CHECK(pen_ble_actor_turn(&actor)==-1&&actor.faulted&&!app.sent_pending&&!core.offered);old=programs;CHECK(pen_ble_actor_turn(&actor)==-1&&programs==old);count++;
start();queued();actor.nonce=UINT64_MAX;old=programs;CHECK(pen_ble_actor_turn(&actor)==-1&&actor.faulted&&programs==old);count++;
start();queued();app.sleep_prepared=1;old=programs;CHECK(pen_ble_actor_turn(&actor)==-3&&programs==old);count++;
start();queued();pen_ble_ticket t={.app=(uintptr_t)&app,.nonce=1,.session=app.sent_session,.seq=app.sent_seq,.epoch=77};pen_ble_grant g;CHECK(!pen_ble_core_authorize(&core,&t,&g)&&g.authorized);CHECK(pen_ble_core_authorize(&core,&t,&g)==-3&&!g.authorized);count++;
printf("Independent actor/grant adversarial cases: %u PASS (mock flash and host ordering; no radio)\n",count);return 0;}
