/* Test-only instrumentation observes real app_main's private state. This is
 * not a production hook, provider implementation, or change to report_status. */
#include ACTOR_SOURCE
#define main existing_actor_main
#include "test_application_actor.c"
#undef main
#include "activity_status.h"
static pen_app_activity_watch observed;
static unsigned seen;
static int observing_poll(void*c,pen_app_input*i){
 (void)c;
 static const enum pen_app_activity expected[]={
  PEN_ACTIVITY_LOGICAL_ASLEEP,PEN_ACTIVITY_PREPARING,PEN_ACTIVITY_READY,
  PEN_ACTIVITY_CONTACT_GAP,PEN_ACTIVITY_READY
 };
 pen_app_activity_status s;unsigned changes;
 CHECK(seen<sizeof expected/sizeof expected[0]);
 CHECK(!pen_app_poll_activity(&application,&observed,&s,&changes));
 CHECK(s.activity==expected[seen]);
 CHECK(changes==(seen?PEN_ACTIVITY_STATE_CHANGED|(seen>=3?PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED:0):PEN_ACTIVITY_INITIAL));
 CHECK(reports==1); /* Only startup callback so far, despite real transitions. */
 CHECK(s.legacy.recording);seen++;polls++;
 memset(i,0,sizeof(*i));i->now_us=100+10*(uint64_t)seen;
 i->usb_sleep_allowed=1;i->camera_ready=(uint8_t)(seen!=1);
 i->pickup_irq_low=(uint8_t)(seen==1);i->raw_contact=(uint8_t)(seen==3);
 clock_us=i->now_us;
 return seen==5?-1:0;
}
int main(void){
 reset_case(0);provider.poll=observing_poll;provider.link_security=NULL;
 observed=(pen_app_activity_watch){0};seen=0;
 if(!setjmp(stopped))app_main();
 CHECK(seen==5&&reports==2&&last_report_error<0&&!last_report.recording);
 CHECK(stops==1&&closed==1&&!sleeps&&!sends);
 puts("actual app_main: preparing/ready/contact-gap/release observed by TEST-ONLY sidecar; legacy reports remain startup+fault only PASS");
 return 0;
}
