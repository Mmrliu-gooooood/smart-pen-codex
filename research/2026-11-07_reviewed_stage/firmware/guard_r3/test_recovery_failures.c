#include "store.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#define CHECK(x) do { if(!(x)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);exit(1); } } while(0)
static uint8_t data[256];
static int intent,reads,programs,syncs,gets,sets,erases,get_fail,set1_before,set1_after,set0_before,set0_after,erase_partial;
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;reads++;CHECK(o<=sizeof data&&n<=sizeof data-o);memcpy(b,data+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;programs++;CHECK(o<=sizeof data&&n<=sizeof data-o);for(size_t i=0;i<n;i++){CHECK((data[o+i]&b[i])==b[i]);data[o+i]&=b[i];}return 0;}
static int sy(void*c){(void)c;syncs++;return 0;}
static int gi(void*c,int*v){(void)c;gets++;*v=intent;return get_fail?-1:0;}
static int si(void*c,int v){(void)c;sets++;if((v&&set1_before)||(!v&&set0_before))return -1;intent=v;return (v&&set1_after)||(!v&&set0_after)?-1:0;}
static int er(void*c){(void)c;erases++;memset(data,255,erase_partial?16:sizeof data);return erase_partial?-1:0;}
static pen_store fresh(void){pen_store s={.log={.read=rd,.program=wr,.sync=sy,.slots=4},.get_erase_intent=gi,.set_erase_intent=si,.erase_all=er};return s;}
static pen_store setup(int ack){
 memset(data,255,sizeof data);intent=get_fail=set1_before=set1_after=set0_before=set0_after=erase_partial=0;
 pen_store s=fresh();CHECK(pen_store_open(&s,42)==0);CHECK(pen_store_begin(&s,10)==0);
 pen_sample p={.timestamp_us=99,.flags=PEN_GAP};CHECK(pen_store_append(&s,&p,&p)==0);pen_store_stop(&s);
 if(ack){CHECK(pen_store_offer(&s,&p)==0);CHECK(pen_store_ack(&s,10,0,1)==0);}
 reads=programs=syncs=gets=sets=erases=0;return s;
}
int main(void){
 const int bad[]={INT_MIN,-65536,-255,-1,2,255,65536,INT_MAX};uint8_t before[sizeof data];pen_store s;
 for(unsigned j=0;j<sizeof bad/sizeof bad[0];j++){
  s=setup(0);memcpy(before,data,sizeof data);intent=bad[j];
  CHECK(pen_store_open(&s,42)==-1&&s.log.faulted&&!s.recording);
  CHECK(!reads&&!programs&&!syncs&&!sets&&!erases&&intent==bad[j]&&!memcmp(data,before,sizeof data));
  pen_sample p={0};CHECK(pen_store_begin(&s,11)==-1&&pen_store_append(&s,&p,&p)==-1&&pen_store_offer(&s,&p)==-1&&pen_store_reclaim(&s,1)==-3);
 }
 s=setup(0);memcpy(before,data,sizeof data);intent=1;get_fail=1;
 CHECK(pen_store_open(&s,42)==-1&&s.log.faulted&&!erases&&!sets&&!memcmp(before,data,sizeof data));
 s=setup(0);memcpy(before,data,sizeof data);
 CHECK(pen_store_open(&s,42)==0&&pen_store_reclaim(&s,1)==-3&&!erases&&!sets&&!memcmp(before,data,sizeof data));
 s=setup(1);memcpy(before,data,sizeof data);set1_before=1;
 CHECK(pen_store_reclaim(&s,1)==-1&&s.log.faulted&&!intent&&!erases&&!memcmp(before,data,sizeof data));
 set1_before=0;CHECK(pen_store_open(&s,42)==0&&s.log.next==1&&!erases);CHECK(pen_store_reclaim(&s,1)==0&&erases==1&&!intent);
 s=setup(1);set1_after=1;
 CHECK(pen_store_reclaim(&s,1)==-1&&s.log.faulted&&intent==1&&!erases);
 set1_after=0;CHECK(pen_store_open(&s,42)==0&&erases==1&&!intent&&!s.log.next);
 s=setup(1);erase_partial=1;
 CHECK(pen_store_reclaim(&s,1)==-1&&s.log.faulted&&intent==1&&erases==1);
 erase_partial=0;CHECK(pen_store_open(&s,42)==0&&erases==2&&!intent&&!s.log.next);
 s=setup(1);set0_before=1;
 CHECK(pen_store_reclaim(&s,1)==-1&&s.log.faulted&&intent==1&&erases==1);
 set0_before=0;CHECK(pen_store_open(&s,42)==0&&erases==2&&!intent&&!s.log.next);
 s=setup(1);set0_after=1;
 CHECK(pen_store_reclaim(&s,1)==-1&&s.log.faulted&&!intent&&erases==1);
 set0_after=0;CHECK(pen_store_open(&s,42)==0&&erases==1&&!intent&&!s.log.next);
 puts("independent recovery: invalid intent with unACK; callback read failure; absent intent unACK gate; intent-set fail before/after durability; partial erase; clear fail before/after durability PASS");
 return 0;
}
