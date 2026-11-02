/* Test fixture only: native store.c runs unchanged. Program bytes are immediately
 * persistent NOR 1->0; sync can report failure but does not undo programmed bytes.
 * This does NOT model real flash/page/controller/voltage failure behavior. */
#include "store.h"
#include <string.h>
#include <stdint.h>
#define CAPACITY 16u
static uint8_t media[CAPACITY*64u];
static pen_store state;
static int intent, bytes_until_fail=-1, sync_until_fail=-1, erases;
static int read_mem(void *ctx,size_t off,uint8_t*out,size_t len){
 (void)ctx;if(off>sizeof media||len>sizeof media-off)return -1;
 memcpy(out,media+off,len);return 0;
}
static int program(void *ctx,size_t off,const uint8_t*in,size_t len){
 (void)ctx;if(off>sizeof media||len>sizeof media-off)return -1;
 for(size_t i=0;i<len;i++){
  if(bytes_until_fail==0)return -1;
  if(bytes_until_fail>0)bytes_until_fail--;
  if((media[off+i]&in[i])!=in[i])return -1;
  media[off+i]&=in[i];
 }return 0;
}
static int sync_mem(void*ctx){(void)ctx;if(sync_until_fail==0)return -1;if(sync_until_fail>0)sync_until_fail--;return 0;}
static int get_intent(void*ctx,int*out){(void)ctx;*out=intent;return 0;}
static int set_intent(void*ctx,int value){(void)ctx;intent=value;return 0;}
static int erase_all(void*ctx){(void)ctx;memset(media,255,sizeof media);erases++;return 0;}
int fixture_boot(uint32_t device){
 memset(&state,0,sizeof state);
 state.log=(pen_log){.read=read_mem,.program=program,.sync=sync_mem,.slots=CAPACITY};
 state.get_erase_intent=get_intent;state.set_erase_intent=set_intent;state.erase_all=erase_all;
 bytes_until_fail=sync_until_fail=-1;
 return pen_store_open(&state,device);
}
int fixture_reset(uint32_t device){memset(media,255,sizeof media);intent=erases=0;return fixture_boot(device);}
int fixture_begin(uint64_t session){return pen_store_begin(&state,session);}
int fixture_append(const uint8_t raw[48]){pen_sample p,q;if(pen_decode(&p,raw))return -1;return pen_store_append(&state,&p,&q);}
int fixture_offer(uint8_t raw[48]){pen_sample p;int e=pen_store_offer(&state,&p);return e?e:pen_encode(raw,&p);}
int fixture_ack(uint64_t session,uint32_t seq,int authenticated){return pen_store_ack(&state,session,seq,authenticated);}
void fixture_cut(int bytes,int syncs){bytes_until_fail=bytes;sync_until_fail=syncs;}
void fixture_stop(void){pen_store_stop(&state);}
int fixture_reclaim(int safe){return pen_store_reclaim(&state,safe);}
int fixture_erases(void){return erases;}
size_t fixture_used(void){return state.log.next;}
void fixture_image(uint8_t out[CAPACITY*64u]){memcpy(out,media,sizeof media);}
