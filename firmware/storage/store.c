#include "store.h"
#include <string.h>
static const uint8_t done[4]={'D','O','N','E'}, ackdone[4]={'A','C','K','!'};
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void wr32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static int slot(pen_store*s,size_t i,pen_sample*p,int*acked){
 uint8_t b[64];if(s->log.read(s->log.ctx,i*64,b,64))return -1;
 if(memcmp(b+60,done,4))return 1; /* erased or interrupted uncommitted write */
 if(pen_decode(p,b)||p->device!=s->device)return -1;
 *acked=!memcmp(b+56,ackdone,4)&&!memcmp(b+48,"PAK1",4)&&rd32(b+52)==pen_crc32(b,44);
 return 0;
}
int pen_store_open(pen_store*s,uint32_t device){
 s->log.faulted=1;
 s->recording=s->offering=s->sequence_exhausted=0;s->recording_session=0;
 s->device=device;s->session_count=0;s->replay_slot=0;
 if(s->get_erase_intent){int intent=0;if(s->get_erase_intent(s->meta_ctx,&intent))return -1;
  if(intent){if(!s->erase_all||!s->set_erase_intent||s->erase_all(s->meta_ctx)||s->set_erase_intent(s->meta_ctx,0))return -1;}}
 if(pen_log_open(&s->log))return -1;
 for(size_t i=0;i<s->log.next;i++){
  pen_sample p;int acked;int result=slot(s,i,&p,&acked);(void)acked;
  if(result<0){s->log.faulted=1;return -1;}if(result)continue;
  unsigned k=0;while(k<s->session_count&&s->sessions[k]!=p.session)k++;
  if(k==s->session_count){if(k==PEN_STORE_MAX_SESSIONS||p.seq!=0){s->log.faulted=1;return -1;}s->sessions[k]=p.session;s->last_seq[k]=0;s->session_count++;}
  else {if(s->last_seq[k]==UINT32_MAX||p.seq!=s->last_seq[k]+1){s->log.faulted=1;return -1;}s->last_seq[k]=p.seq;}
 }
 return 0;
}
int pen_store_begin(pen_store*s,uint64_t session){
 if(!session||s->recording||s->log.faulted||s->session_count==PEN_STORE_MAX_SESSIONS)return -1;
 for(unsigned i=0;i<s->session_count;i++)if(s->sessions[i]==session)return -1;
 s->recording_session=session;s->next_seq=0;s->sequence_exhausted=0;s->recording=1;return 0;
}
int pen_store_append(pen_store*s,const pen_sample*observation,pen_sample*durable){
 if(!s->recording||s->sequence_exhausted||s->log.faulted)return -1;
 pen_sample p=*observation;p.device=s->device;p.session=s->recording_session;p.seq=s->next_seq;
 int result=pen_log_append(&s->log,&p);if(result)return result;
 if(p.seq==0){s->sessions[s->session_count]=p.session;s->last_seq[s->session_count]=0;s->session_count++;}
 else s->last_seq[s->session_count-1]=p.seq;
 if(s->next_seq==UINT32_MAX)s->sequence_exhausted=1;else s->next_seq++;
 *durable=p;return 0;
}
void pen_store_stop(pen_store*s){s->recording=0;}
int pen_store_offer(pen_store*s,pen_sample*p){
 if(s->log.faulted)return -1;
 if(s->offering){*p=s->offered;return 0;}
 while(s->replay_slot<s->log.next){int acked;int result=slot(s,s->replay_slot,p,&acked);
  if(result<0){s->log.faulted=1;return -1;}
  if(!result&&!acked){s->offered=*p;s->offered_slot=s->replay_slot;s->offering=1;return 0;}
  s->replay_slot++;
 }return 1;
}
int pen_store_ack(pen_store*s,uint64_t session,uint32_t seq,int authenticated){
 if(!authenticated||!s->offering||session!=s->offered.session||seq!=s->offered.seq)return -3;
 if(s->log.faulted)return -1;
 uint8_t packet[48],body[8];if(pen_encode(packet,&s->offered))return -1;
 memcpy(body,"PAK1",4);wr32(body+4,pen_crc32(packet,44));size_t offset=s->offered_slot*64;
 if(s->log.program(s->log.ctx,offset+48,body,8)||s->log.sync(s->log.ctx)||
    s->log.program(s->log.ctx,offset+56,ackdone,4)||s->log.sync(s->log.ctx)){s->log.faulted=1;return -1;}
 s->offering=0;s->replay_slot=s->offered_slot+1;return 0;
}
int pen_store_reclaim(pen_store*s,int safe){
 if(!safe||s->recording||s->offering||s->log.faulted||!s->get_erase_intent||!s->set_erase_intent||!s->erase_all)return -3;
 for(size_t i=0;i<s->log.next;i++){pen_sample p;int acked;int result=slot(s,i,&p,&acked);if(result<0)return -1;if(!result&&!acked)return -3;}
 s->log.faulted=1;
 if(s->set_erase_intent(s->meta_ctx,1)||s->erase_all(s->meta_ctx)||s->set_erase_intent(s->meta_ctx,0))return -1;
 return pen_store_open(s,s->device);
}
