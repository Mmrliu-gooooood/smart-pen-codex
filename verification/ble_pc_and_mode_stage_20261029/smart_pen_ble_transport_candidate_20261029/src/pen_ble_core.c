#include "pen_ble_core.h"
#include <string.h>
static void clear(pen_ble_core*c){c->ack_count=0;c->offered=0;c->attempted=0;}
static int secure(const pen_link_security*s){return s->encrypted==1&&s->authenticated==1&&s->bonded==1&&s->approved_peer==1&&s->connection_epoch!=0;}
void pen_ble_core_init(pen_ble_core*c){memset(c,0,sizeof *c);c->mtu=23;}
void pen_ble_core_link(pen_ble_core*c,const pen_link_security*s,unsigned key_size){
 pen_link_security next={0};if(s)next=*s;
 if(key_size!=16)next.authenticated=0;
 if(next.connection_epoch!=c->security.connection_epoch){clear(c);c->subscribed=0;c->mtu=23;}
 if(!secure(&next))clear(c);
 c->security=next;
}
void pen_ble_core_mtu(pen_ble_core*c,uint16_t mtu){c->mtu=mtu;if(mtu<23)clear(c);}
void pen_ble_core_subscribe(pen_ble_core*c,int enabled){c->subscribed=(uint8_t)(enabled==1);if(!c->subscribed)clear(c);}
void pen_ble_core_quiesce(pen_ble_core*c,int quiet){c->quiesced=(uint8_t)(quiet!=0);if(quiet)clear(c);}
int pen_ble_core_ready(const pen_ble_core*c){return c&&!c->faulted&&!c->quiesced&&c->subscribed&&c->mtu>=23&&secure(&c->security);}
int pen_ble_core_send(pen_ble_core*c,const uint8_t*b,size_t n,uint64_t epoch,uint64_t now,pen_ble_notify notify,void*ctx){
 if(!c||!b||n!=PEN_PACKET_SIZE||!notify)return -1;
 if(c->faulted)return -1;
 if(!pen_ble_core_ready(c)||epoch!=c->security.connection_epoch)return 1;
 pen_sample p;if(pen_decode(&p,b))return -1;
 int same=c->attempted&&!memcmp(c->packet,b,n);
 if(same&&now<c->last_attempt_us){c->faulted=1;clear(c);return -1;}
 if(same&&now-c->last_attempt_us<PEN_BLE_RETRY_US)return c->offered?0:1;
 if(!same){clear(c);memcpy(c->packet,b,n);}
 c->attempted=1;c->last_attempt_us=now;
 /* Any partially accepted retry cannot create new receipt authorization. A
  * previously complete same-epoch offer remains valid if a retry is busy. */
 for(unsigned i=0;i<3;i++){
  uint8_t f[20]={0xb1,(uint8_t)i,(uint8_t)p.seq,(uint8_t)(p.seq>>8)};
  memcpy(f+4,b+16*i,16);
  if(!pen_ble_core_ready(c)||c->security.connection_epoch!=epoch)return 1;
  int r=notify(ctx,f,sizeof f,epoch);
  if(r<0){c->faulted=1;clear(c);return -1;}
  if(r||!pen_ble_core_ready(c)||c->security.connection_epoch!=epoch)return 1;
 }
 c->offered=1;c->offered_session=p.session;c->offered_seq=p.seq;
 return 0;
}
static uint64_t le(const uint8_t*p,unsigned n){uint64_t v=0;for(unsigned i=0;i<n;i++)v|=(uint64_t)p[i]<<(8*i);return v;}
int pen_ble_core_receive(pen_ble_core*c,const uint8_t*b,size_t n,uint64_t now){
 if(!c||!b||!pen_ble_core_ready(c)||!c->offered||n!=20)return -3;
 if(b[0]!='A'||b[1]!='K'||b[2]!=1||b[3]||le(b+16,4)!=pen_crc32(b,16))return -3;
 uint64_t session=le(b+4,8);uint32_t seq=(uint32_t)le(b+12,4);
 if(!session||session!=c->offered_session||seq!=c->offered_seq||now<c->last_attempt_us)return -3;
 for(unsigned i=0;i<c->ack_count;i++)if(c->acks[i].session==session&&c->acks[i].seq==seq)return 0;
 if(c->ack_count==PEN_BLE_ACK_CAPACITY)return 1;
 c->acks[c->ack_count++]=(pen_ble_ack){.session=session,.seq=seq,.received_us=now,.receipt=c->security};
 return 0;
}
int pen_ble_core_pop(pen_ble_core*c,pen_ble_ack*a){
 if(!c||!a||c->faulted)return -1;
 if(!pen_ble_core_ready(c)){c->ack_count=0;return 1;}
 if(!c->ack_count)return 1;
 *a=c->acks[0];c->ack_count--;memmove(c->acks,c->acks+1,c->ack_count*sizeof c->acks[0]);return 0;
}
void pen_ble_core_committed(pen_ble_core*c,const pen_ble_ack*a){
 if(a&&a->receipt.connection_epoch==c->security.connection_epoch&&a->session==c->offered_session&&a->seq==c->offered_seq)clear(c);
}
