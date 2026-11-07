/* Actual app_main with existing host doubles. No device/Flash/IRQ proof. */
#define pen_storage_idf_open fixture_base_open
#define main existing_actor_test_main
#include "test_application_actor.c"
#undef main
#undef pen_storage_idf_open
#include <limits.h>
static int normal_path,guard_value,guard_calls,retain_backlog;
static uint8_t at_guard[sizeof bytes];
int pen_storage_idf_open(pen_storage_idf*c,int enabled,const char*label,uint32_t id){
 int e=fixture_base_open(c,enabled,label,id);
 if(!e&&normal_path)c->store.log.slots=2;
 return e;
}
static int checked_guard(void*c){(void)c;guard_calls++;memcpy(at_guard,bytes,sizeof bytes);return guard_value;}
static int timed_poll(void*c,pen_app_input*i){
 if(!normal_path)return poll_board(c,i);
 (void)c;polls++;CHECK(polls<=4);memset(i,0,sizeof(*i));
 i->now_us=polls==1?100:polls==2?200:polls==3?300:10200;
 i->raw_contact=(uint8_t)(polls==1);i->camera_ready=1;i->usb_sleep_allowed=1;clock_us=i->now_us;
 return 0;
}
static int auth_link(void*c,pen_link_security*s){(void)c;*s=(pen_link_security){1,1,1,1,7};return retain_backlog?1:0;}
static int queued_send(void*c,const uint8_t*b,size_t n,uint64_t epoch){
 (void)c;CHECK(n==48&&epoch==7);CHECK(!pen_decode(&sent,b));sends++;ack_queued=1;return 0;
}
static int queued_ack(void*c,uint64_t*s,uint32_t*q,pen_link_security*r){
 (void)c;if(!ack_queued)return 1;
 *s=sent.session;*q=sent.seq;*r=(pen_link_security){1,1,1,1,7};ack_queued=0;return 0;
}
static void run_case(int value){
 guard_value=value;guard_calls=0;retain_backlog=0;reset_case(normal_path?5:13);
 provider.poll=timed_poll;provider.maintenance_idle_guard=checked_guard;
 if(normal_path){provider.link_security=auth_link;provider.send_packet=queued_send;provider.next_ack=queued_ack;}
 if(!setjmp(stopped))app_main();
 CHECK(guard_calls==1&&stops==1&&closed==1&&opened==1&&!last_report.recording);
 if(value==1){
  CHECK(erase_count==1&&maintenance_reports==1&&!erase_intent&&begin_count==1);
  CHECK(sleeps==(normal_path?1:0)&&resumes==(normal_path?0:1));
  CHECK(last_report.slots_used==0);
 }else{
  if(erase_count)fprintf(stderr,"maintenance guard=%d path=%s erased=%d new_session=%d\n",value,normal_path?"sleep":"replay",erase_count,normal_path?begin_count-1:begin_count);
  CHECK(!erase_count&&!maintenance_reports&&!sleeps&&!erase_intent);
  CHECK(begin_count==(normal_path?1:0));CHECK(!memcmp(at_guard,bytes,sizeof bytes));
  CHECK(last_report.slots_used==(normal_path?2u:32u));
  CHECK(resumes==(!normal_path&&value==0?1:0));
  CHECK(last_report_error==(normal_path?-104:-100));
 }
}
int main(int argc,char**argv){
 CHECK(argc==2);normal_path=!strcmp(argv[1],"sleep");CHECK(normal_path||!strcmp(argv[1],"replay"));
 /* Start with the exact independently reported regression. */
 run_case(2);
 for(volatile int value=-255;value<=255;value++)run_case(value);
 run_case(INT_MIN);run_case(INT_MAX);run_case(-65536);run_case(65536);
 /* UnACK backlog must remain protected independently of the guard value. */
 retain_backlog=1;guard_value=1;guard_calls=0;reset_case(normal_path?5:23);
 provider.poll=timed_poll;provider.maintenance_idle_guard=checked_guard;provider.link_security=auth_link;
 if(!setjmp(stopped))app_main();
 CHECK(!guard_calls&&!erase_count&&!maintenance_reports&&sleeps==1);
 CHECK(last_report.slots_used==(normal_path?2u:32u));
 for(size_t slot=0;slot<last_report.slots_used;slot++){
  CHECK(!memcmp(bytes+slot*64+60,"DONE",4));
  for(unsigned k=48;k<60;k++)CHECK(bytes[slot*64+k]==255);
 }
 printf("maintenance actor %s: exact-1 grant; zero/fatal/malformed integers; unACK backlog preserved PASS\n",argv[1]);
 return 0;
}
