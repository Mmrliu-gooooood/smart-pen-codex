#include "pen_ble_actor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t flash[512],wire[60];static pen_store store;static pen_app app;
static pen_roi_workspace workspace;static pen_ble_core core;static pen_ble_actor actor;
static unsigned writes,syncs,notify_calls,fail_stage,stage;static int disconnect_when;static uint64_t timer;
static int read_flash(void*x,size_t o,uint8_t*b,size_t n){(void)x;if(o+n>sizeof flash)return -1;memcpy(b,flash+o,n);return 0;}
static int write_flash(void*x,size_t o,const uint8_t*b,size_t n){(void)x;writes++;if(++stage==fail_stage)return -1;if(o+n>sizeof flash)return -1;for(size_t i=0;i<n;i++){if((flash[o+i]&b[i])!=b[i])return -1;flash[o+i]&=b[i];}return 0;}
static int sync_flash(void*x){(void)x;syncs++;return ++stage==fail_stage?-1:0;}
static int notify(void*x,const uint8_t*b,size_t n,uint64_t e){(void)x;CHECK(n==20&&e==91);memcpy(wire+(notify_calls%3)*20,b,20);notify_calls++;return 0;}
static int security(void*x,pen_link_security*s){(void)x;*s=core.security;return 0;}
static int sender(void*x,const uint8_t*b,size_t n,uint64_t e){(void)x;return pen_ble_core_send(&core,b,n,e,++timer,notify,NULL);}
static int authorize(void*x,const pen_ble_ticket*t,pen_ble_grant*g){(void)x;if(disconnect_when==1)pen_ble_core_link(&core,NULL,0);int r=pen_ble_core_authorize(&core,t,g);if(disconnect_when==2)pen_ble_core_link(&core,NULL,0);return r;}
static void init(void){
 memset(flash,255,sizeof flash);writes=syncs=notify_calls=fail_stage=stage=0;disconnect_when=0;timer=100;
 store=(pen_store){.log={.read=read_flash,.program=write_flash,.sync=sync_flash,.slots=8}};
 CHECK(!pen_store_open(&store,10));CHECK(!pen_store_begin(&store,100));
 pen_app_config c={.max_frame_gap_us=5000,.contact={.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750}};
 CHECK(!pen_app_init(&app,&store,&workspace,&c));
 /* Explicitly invalid/no-ink sample; transport must NEVER fabricate VALID. */
 pen_sample p={.timestamp_us=1},durable;CHECK(!pen_store_append(&store,&p,&durable));
 pen_ble_core_init(&core);pen_link_security s={1,1,1,1,91};pen_ble_core_link(&core,&s,16);pen_ble_core_subscribe(&core,1);
 pen_ble_backend backend={NULL,security,sender,authorize};CHECK(!pen_ble_actor_init(&actor,&app,&backend));
}
static void put(uint8_t*p,uint64_t v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(uint8_t)(v>>(8*i));}
static void ack(uint8_t b[20]){memcpy(b,"AK\1\0",4);put(b+4,100,8);put(b+12,0,4);put(b+16,pen_crc32(b,16),4);}
static void queue(void){uint8_t b[20];CHECK(!pen_ble_actor_turn(&actor));ack(b);CHECK(!pen_ble_core_receive(&core,b,20,++timer));}
int main(void){unsigned cases=0;
 init();uint8_t b[20];ack(b);CHECK(pen_app_pending(&app)==1&&!app.sent_pending&&!store.offering);CHECK(pen_ble_core_receive(&core,b,20,101)==-3);cases++;
 CHECK(!pen_ble_actor_turn(&actor)&&notify_calls==3);uint8_t packet[48];for(unsigned i=0;i<3;i++){CHECK(wire[i*20]==0xb1&&wire[i*20+1]==i);memcpy(packet+i*16,wire+i*20+4,16);}pen_sample p;CHECK(!pen_decode(&p,packet)&&p.flags==0&&p.session==100&&p.seq==0);cases++;
 for(unsigned i=0;i<20;i++){uint8_t bad[20];memcpy(bad,b,20);bad[i]^=1;CHECK(pen_ble_core_receive(&core,bad,20,++timer)==-3);cases++;}
 CHECK(pen_ble_core_receive(&core,b,19,++timer)==-3);CHECK(pen_ble_core_receive(&core,b,21,++timer)==-3);cases++;
 CHECK(!pen_ble_core_receive(&core,b,20,++timer));for(unsigned i=0;i<100;i++)CHECK(!pen_ble_core_receive(&core,b,20,++timer));CHECK(core.ack_count==1);cases++;
 unsigned old=writes;CHECK(pen_ble_actor_turn(&actor)==1&&writes==old+2&&pen_app_pending(&app)==0);old=writes;CHECK(pen_ble_actor_turn(&actor)==1&&writes==old);cases++;
 for(int ordering=1;ordering<=2;ordering++){init();queue();old=writes;disconnect_when=ordering;CHECK(pen_ble_actor_turn(&actor)==-3);CHECK(writes==old+(ordering==2?2u:0u));CHECK(pen_app_pending(&app)==(ordering==1));cases++;}
 for(unsigned failure=1;failure<=4;failure++){
  init();queue();stage=0;fail_stage=failure;CHECK(pen_ble_actor_turn(&actor)==-1&&actor.faulted&&!app.sent_pending);old=writes;CHECK(pen_ble_actor_turn(&actor)==-1&&writes==old);
  /* Reopen simulates reboot after the failed authorized write. Only the fully
   * committed marker may retire a record; prior authorization is never reused. */
  fail_stage=0;store.log.faulted=0;CHECK(!pen_store_open(&store,10));pen_sample pending;CHECK(pen_store_offer(&store,&pending)==(failure==4?1:0));cases++;
 }
 printf("Author transport/actor cases: %u PASS; mock flash, no radio\n",cases);
 init();CHECK(!pen_ble_actor_turn(&actor));printf("WIRE=");for(unsigned i=0;i<60;i++)printf("%02x",wire[i]);puts("");return 0;
}
