/* Reuse the existing narrow IDF/board/Flash doubles, not a second actor model. */
#define main existing_actor_test_main
#include "test_application_actor.c"
#undef main
#include <stddef.h>
static unsigned bad_field,bad_byte,inject_at;
static const size_t offsets[]={offsetof(pen_app_input,usb_sleep_allowed),
 offsetof(pen_app_input,raw_contact),offsetof(pen_app_input,pickup_irq_low),
 offsetof(pen_app_input,camera_ready),offsetof(pen_app_input,storage_pending)};
static int invalid_poll(void*c,pen_app_input*i){
 int e=poll_board(c,i);
 if(!e&&(unsigned)polls==inject_at)((uint8_t*)i)[offsets[bad_field]]=(uint8_t)bad_byte;
 return e;
}
int main(int argc,char**argv){
 CHECK(argc==2);
 int mode=!strcmp(argv[1],"recording")?5:!strcmp(argv[1],"replay")?23:-1;
 CHECK(mode>=0);inject_at=mode==5?3u:2u;
 for(bad_field=0;bad_field<5;bad_field++)for(bad_byte=2;bad_byte<=255;bad_byte++){
  reset_case(mode);provider.poll=invalid_poll;
  if(!setjmp(stopped))app_main();
  if(sleeps||last_report_error!=-110)fprintf(stderr,"ACTOR mode=%s accepted malformed field=%u byte=%u sleeps=%d polls=%d error=%d\n",argv[1],bad_field,bad_byte,sleeps,polls,last_report_error);
  CHECK(!sleeps&&polls==(int)inject_at&&last_report_error==-110);
  CHECK(stops==1&&closed==1&&opened==1&&!last_report.recording&&!last_report.sleep_prepared);
  CHECK(!erase_count&&!quiesces&&!sends&&!last_report.storage_fault);
  CHECK(last_report.slots_used==(mode==5?2u:32u));
  /* First durable record body/commit survives, never ACKed or erased. */
  CHECK(!memcmp(bytes+60,"DONE",4));
  for(unsigned k=48;k<60;k++)CHECK(bytes[k]==255);
 }
 printf("boolean ACTOR %s: 1270 invalid bytes stopped before quiesce/sleep/erase/send PASS\n",argv[1]);
 return 0;
}
