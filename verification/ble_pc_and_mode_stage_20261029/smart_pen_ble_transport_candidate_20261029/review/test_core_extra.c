#include "pen_ble_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"%s:%d failed: %s\n",__FILE__,__LINE__,#x);exit(1);} }while(0)
static unsigned cases;
static void put(uint8_t*p,uint64_t v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(uint8_t)(v>>(8*i));}
static void ack(uint8_t*b,uint64_t s,uint32_t q){memcpy(b,"AK\1\0",4);put(b+4,s,8);put(b+12,q,4);put(b+16,pen_crc32(b,16),4);}
static void packet(uint8_t*b,uint64_t s,uint32_t q){pen_sample p={.device=7,.session=s,.seq=q,.page=4,.timestamp_us=100,.x_um=1,.y_um=2,.confidence=1000,.flags=PEN_VALID|PEN_CONTACT};CHECK(!pen_encode(b,&p));}
static pen_link_security security(uint64_t epoch){return (pen_link_security){1,1,1,1,epoch};}
static void ready(pen_ble_core*c){pen_ble_core_init(c);pen_link_security s=security(55);pen_ble_core_link(c,&s,16);pen_ble_core_subscribe(c,1);}
struct tx {pen_ble_core*c;int calls,mode,when;uint8_t assembled[48];};
static int notify(void*v,const uint8_t*f,size_t n,uint64_t e){struct tx*t=v;CHECK(n==20&&f[0]==0xb1&&f[1]==t->calls%3&&e==55);memcpy(t->assembled+16*f[1],f+4,16);t->calls++;if(t->calls==t->when){pen_link_security s=security(56);switch(t->mode){case 1:return 1;case 2:pen_ble_core_link(t->c,NULL,0);break;case 3:pen_ble_core_link(t->c,&s,16);break;case 4:s=security(55);s.approved_peer=0;pen_ble_core_link(t->c,&s,16);break;case 5:pen_ble_core_quiesce(t->c,1);break;case 6:return -1;default:break;}}return 0;}
int main(void){pen_ble_core c;uint8_t b[48],a[20];pen_ble_ack got;packet(b,99,7);ack(a,99,7);
 ready(&c);CHECK(pen_ble_core_receive(&c,a,20,20)==-3);CHECK(pen_ble_core_pop(&c,&got)==1);cases++;
 for(int mode=1;mode<=6;mode++)for(int when=1;when<=3;when++){ready(&c);struct tx t={.c=&c,.mode=mode,.when=when};int r=pen_ble_core_send(&c,b,48,55,1000,notify,&t);CHECK(r==(mode==6?-1:1));CHECK(!c.offered);CHECK(pen_ble_core_receive(&c,a,20,2000)==-3);cases++;}
 ready(&c);struct tx t={.c=&c};CHECK(!pen_ble_core_send(&c,b,48,55,1000,notify,&t));CHECK(t.calls==3&&!memcmp(t.assembled,b,48));ack(a,99,8);CHECK(pen_ble_core_receive(&c,a,20,2000)==-3);ack(a,100,7);CHECK(pen_ble_core_receive(&c,a,20,2000)==-3);ack(a,99,7);CHECK(pen_ble_core_receive(&c,a,20,999)==-3);cases++;
 CHECK(!pen_ble_core_receive(&c,a,20,2000));CHECK(!pen_ble_core_receive(&c,a,20,2001));CHECK(c.ack_count==1);CHECK(!pen_ble_core_pop(&c,&got));CHECK(got.session==99&&got.seq==7&&got.received_us==2000&&got.receipt.connection_epoch==55);pen_ble_core_committed(&c,&got);CHECK(!c.offered&&!c.ack_count);CHECK(pen_ble_core_receive(&c,a,20,2002)==-3);cases++;
 ready(&c);t=(struct tx){.c=&c};CHECK(!pen_ble_core_send(&c,b,48,55,1000,notify,&t));CHECK(!pen_ble_core_receive(&c,a,20,2000));pen_link_security s=security(56);pen_ble_core_link(&c,&s,16);CHECK(!c.offered&&!c.ack_count);CHECK(pen_ble_core_pop(&c,&got)==1);CHECK(pen_ble_core_receive(&c,a,20,2001)==-3);cases++;
 for(unsigned k=0;k<16;k++){ready(&c);s=security(55);pen_ble_core_link(&c,&s,k);t=(struct tx){.c=&c};CHECK(pen_ble_core_send(&c,b,48,55,1000,notify,&t)==1&&!t.calls);cases++;}
 for(unsigned field=0;field<5;field++){ready(&c);s=security(55);if(field==0)s.encrypted=0;if(field==1)s.authenticated=0;if(field==2)s.bonded=0;if(field==3)s.approved_peer=0;if(field==4)s.connection_epoch=0;pen_ble_core_link(&c,&s,16);t=(struct tx){.c=&c};CHECK(pen_ble_core_send(&c,b,48,55,1000,notify,&t)==1&&!t.calls);cases++;}
 ready(&c);pen_ble_core_mtu(&c,22);t=(struct tx){.c=&c};CHECK(pen_ble_core_send(&c,b,48,55,1000,notify,&t)==1&&!t.calls);pen_ble_core_mtu(&c,517);CHECK(!pen_ble_core_send(&c,b,48,55,1001,notify,&t)&&t.calls==3);cases++;
 ready(&c);t=(struct tx){.c=&c};CHECK(!pen_ble_core_send(&c,b,48,55,1000,notify,&t));CHECK(!pen_ble_core_send(&c,b,48,55,1001,notify,&t)&&t.calls==3);t.calls=0;t.mode=1;t.when=2;CHECK(pen_ble_core_send(&c,b,48,55,1000+PEN_BLE_RETRY_US,notify,&t)==1&&c.offered);CHECK(!pen_ble_core_receive(&c,a,20,1001+PEN_BLE_RETRY_US));cases++;
 ready(&c);t=(struct tx){.c=&c};CHECK(!pen_ble_core_send(&c,b,48,55,1000,notify,&t));CHECK(pen_ble_core_send(&c,b,48,55,999,notify,&t)==-1&&c.faulted&&!c.offered);cases++;
 ready(&c);t=(struct tx){.c=&c};CHECK(!pen_ble_core_send(&c,b,48,55,1000,notify,&t));for(unsigned i=0;i<20;i++){uint8_t corrupt[20];memcpy(corrupt,a,20);corrupt[i]^=1;CHECK(pen_ble_core_receive(&c,corrupt,20,2000)==-3);}CHECK(!c.ack_count);cases++;
 printf("Independent core adversarial cases: %u PASS (single-owner event-order simulation; no radio)\n",cases);return 0;}
