/* Independent same-offer retry: reuse only earlier reviewer storage doubles. */
#define main recovery_tests_main
#include "test_recovery_failures.c"
#undef main
int main(void){
 const int bad[]={INT_MIN,-65536,-255,-1,0,2,255,65536,INT_MAX};
 for(unsigned k=0;k<sizeof bad/sizeof bad[0];k++){
  pen_store s=setup(0);pen_sample p;CHECK(pen_store_offer(&s,&p)==0);
  pen_store saved=s;uint8_t before[sizeof data];memcpy(before,data,sizeof data);
  reads=programs=syncs=gets=sets=erases=0;
  CHECK(pen_store_ack(&s,10,0,bad[k])==-3);
  CHECK(pen_store_ack(&s,10,0,bad[k])==-3);
  CHECK(!memcmp(&s,&saved,sizeof s)&&!memcmp(data,before,sizeof data));
  CHECK(!reads&&!programs&&!syncs&&!gets&&!sets&&!erases);
  CHECK(pen_store_ack(&s,10,0,1)==0&&programs==2&&syncs==2);
  CHECK(pen_store_ack(&s,10,0,1)==-3&&programs==2&&syncs==2);
  CHECK(pen_store_open(&s,42)==0&&pen_store_offer(&s,&p)==1);
  CHECK(pen_store_reclaim(&s,1)==0&&erases==1&&!intent);
 }
 pen_store s=setup(0);pen_sample p;CHECK(pen_store_offer(&s,&p)==0);s.log.faulted=1;
 CHECK(pen_store_ack(&s,10,0,2)==-3&&s.log.faulted&&!programs&&!syncs);
 CHECK(pen_store_ack(&s,10,0,1)==-1&&s.log.faulted&&!programs&&!syncs);
 puts("independent: repeated invalid auth retains exact same offer; immediate lawful retry persists once; duplicate ACK no writes; fault never cleared PASS");
 return 0;
}
