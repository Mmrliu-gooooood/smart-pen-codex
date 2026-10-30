#include "board_provider.h"
#include "storage_idf.h"
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"actor FAIL line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
void app_main(void);
static jmp_buf stopped;
static int scenario,polls,stops,closed,opened,sends,delays,actions,available=1,quiesces,resumes,sleeps,sync_error;
static int maintenance_reports;
static uint64_t clock_us,boot_epoch;static int erase_intent,erase_count,begin_count,captures;static pen_sample sent;static int ack_queued;static int reports,last_report_error;static pen_app_status last_report;
static uint8_t bytes[64*32];
static pen_board_provider provider;
static int read_mem(void*c,size_t o,uint8_t*b,size_t n){(void)c;if(o>sizeof bytes||n>sizeof bytes-o)return -1;memcpy(b,bytes+o,n);return 0;}
static int write_mem(void*c,size_t o,const uint8_t*b,size_t n){(void)c;if(o>sizeof bytes||n>sizeof bytes-o)return -1;for(size_t k=0;k<n;k++)bytes[o+k]&=b[k];return 0;}
static int sync_mem(void*c){(void)c;if(scenario==12&&quiesces)clock_us+=600;return sync_error?-1:0;}
static int get_intent(void*c,int*v){(void)c;*v=erase_intent;return 0;}
static int set_intent(void*c,int v){(void)c;erase_intent=v;return 0;}
static int erase_log(void*c){(void)c;erase_count++;memset(bytes,255,sizeof bytes);return 0;}
int pen_application_partition_guard(void){return scenario==24?-1:0;}
int pen_storage_idf_open(pen_storage_idf*c,int enabled,const char*label,uint32_t id){
 opened++;CHECK(enabled==1&&!strcmp(label,"pen_records"));memset(bytes,255,sizeof bytes);
 memset(c,0,sizeof(*c));c->store.log=(pen_log){.read=read_mem,.program=write_mem,.sync=sync_mem,.slots=scenario==15||scenario==16?1:32};
 c->store.get_erase_intent=get_intent;c->store.set_erase_intent=set_intent;c->store.erase_all=erase_log;
 int result=pen_store_open(&c->store,id);
 if(scenario==13||scenario==14||(scenario>=17&&scenario<=20)||scenario==22||scenario==23){
  for(uint64_t k=1;k<=32;k++){
   CHECK(!pen_store_begin(&c->store,k));pen_sample p={.timestamp_us=k};CHECK(!pen_store_append(&c->store,&p,&p));pen_store_stop(&c->store);
   if(scenario==13||(scenario>=17&&scenario<=20)||scenario==22){CHECK(!pen_store_offer(&c->store,&p));CHECK(!pen_store_ack(&c->store,k,0,1));}
  }
 }
 return result;
}
int pen_storage_idf_begin_boot(pen_storage_idf*c,uint64_t*epoch){begin_count++;*epoch=++boot_epoch;return pen_store_begin(&c->store,*epoch);}
void pen_storage_idf_close(pen_storage_idf*c){closed++;pen_store_stop(&c->store);}
int64_t esp_timer_get_time(void){return (int64_t)clock_us;}
void actor_log(const char*a,const char*b,...){(void)a;(void)b;}
void vTaskDelay(unsigned n){if(n==1000)longjmp(stopped,1);delays++;CHECK(delays<40);}
static int poll_board(void*c,pen_app_input*i){
 (void)c;polls++;CHECK(polls<=36);memset(i,0,sizeof(*i));
 if(scenario>=13&&scenario!=21){
  i->now_us=(uint64_t)polls*100;i->usb_sleep_allowed=1;clock_us=i->now_us;
  if(scenario==15||scenario==16){i->raw_contact=(uint8_t)(polls==1);i->camera_ready=1;}
  if(scenario==16&&polls>=4){i->now_us=10300;clock_us=i->now_us;}
  if((scenario==18||scenario==22)&&polls==2){i->now_us=700;clock_us=i->now_us;}
  if(scenario==23){i->now_us=polls==1?100:polls==2?10200:polls==3?10300:10400;i->usb_sleep_allowed=(uint8_t)(polls!=3);clock_us=i->now_us;}
  if((scenario>=17&&scenario<=20&&polls==3)||(scenario==13&&polls==2)||(scenario==14&&polls==35)||(scenario==15&&polls==4))return -1;
  return 0;
 }
 if(scenario==10&&polls==5)return -1;
 i->now_us=polls==1?100:(scenario==1?10100:5100);i->raw_contact=1;i->camera_ready=1;i->usb_sleep_allowed=1;
 if(scenario==3){i->raw_contact=0;i->pickup_irq_low=1;}
 if(scenario==4&&polls==2)i->now_us=99;
 if(scenario>=5){
  i->now_us=polls==1?100:polls==2?200:polls==3?10200:scenario==7?10800:10300;
  i->raw_contact=(uint8_t)(polls==1||(scenario==10&&polls==4));
 }
 if(scenario==21){if(polls==4)i->usb_sleep_allowed=0;if(polls==5)i->now_us=20300;}
 clock_us=i->now_us;
 return 0;
}
static int apply(void*c,unsigned a){(void)c;actions++;if(a&PEN_CP_SLEEP_REQUEST){sleeps++;return 0;}CHECK(a&PEN_CP_WAKE_CAMERA);return 0;}
static int pending(void*c){(void)c;return (scenario==6&&polls==3)||(scenario==22&&polls>=2)?1:0;}
static int quiesce(void*c){(void)c;quiesces++;if(scenario==21||scenario==23)return quiesces==1?1:0;if(scenario==22)return 1;if(scenario==17)return quiesces==1?1:0;if(scenario==18)return 1;if(scenario==11)clock_us+=600;if(scenario==9)sync_error=1;return scenario==8?-1:(scenario==7||scenario==10)?1:0;}
static int maintenance_guard(void*c){(void)c;if(scenario==19&&polls==1)return 0;if(scenario==20)return -1;return 1;}
static int resume_link(void*c){(void)c;resumes++;return 0;}
static int link_status(void*c,pen_link_security*s){(void)c;*s=(pen_link_security){1,1,1,1,7};return (scenario>=5&&scenario<13)||scenario==16||scenario==21||scenario==23?1:0;}
static int next_ack(void*c,uint64_t*s,uint32_t*q,pen_link_security*r){(void)c;if((scenario==14||scenario==15)&&ack_queued){*s=sent.session;*q=sent.seq;*r=(pen_link_security){1,1,1,1,7};ack_queued=0;return 0;}return scenario==0?-1:1;}
static int send_packet(void*c,const uint8_t*b,size_t n,uint64_t epoch){(void)c;if(scenario>=13){CHECK(!pen_decode(&sent,b));ack_queued=1;}CHECK(epoch==7);CHECK(n==48);sends++;return 0;}
static void report_status(void*c,const pen_app_status*s,int error){(void)c;reports++;if(error==-109){maintenance_reports++;CHECK(!s->recording);}last_report=*s;last_report_error=error;}
static int stop_capture(void*c){(void)c;captures++;return 0;}
static void stop_board(void*c){(void)c;stops++;}
static int no_mapper(void*c,const pen_app_frame*f,const pen_roi_opt_result*r,pen_tip_solution*t){(void)c;(void)f;(void)r;(void)t;return -1;}
const pen_board_provider *pen_get_board_provider(void){return available?&provider:NULL;}
static void reset_case(int mode){
 maintenance_reports=0;
 boot_epoch=mode==13||mode==14||(mode>=17&&mode<=20)||mode==22||mode==23?32:122;erase_intent=erase_count=begin_count=captures=ack_queued=0;
 scenario=mode;polls=stops=closed=opened=sends=delays=actions=quiesces=resumes=sleeps=sync_error=0;available=1;clock_us=0;reports=last_report_error=0;memset(&last_report,0,sizeof last_report);
 provider=(pen_board_provider){.device_id=42,.max_sleep_quiesce_us=500,.maintenance_idle_guard=maintenance_guard,.pending_transactions=pending,.quiesce_transport=quiesce,.resume_transport=resume_link,.poll=poll_board,.apply_actions=apply,.link_security=link_status,.next_ack=next_ack,.send_packet=send_packet,.safe_stop=stop_board,.stop_capture=stop_capture,.report_status=report_status,
 .config={.paper={710,1000,0,0},.contact={.press_us=0,.camera_timeout_us=10000,.contact_stuck_us=mode==2?5000:100000,.irq_stuck_us=5000,.idle_us=10000,.min_confidence=750},
 .source_id=17,.calibration_revision=7,.page=99,.max_frame_gap_us=2000,.min_x_um=-100000,.max_x_um=100000,.min_y_um=-100000,.max_y_um=100000,.camera_qualified=1,.map_tip=no_mapper}};
}
int main(void){
#ifdef TEST_APP_DISABLED
 reset_case(0);if(!setjmp(stopped))app_main();CHECK(!opened&&!polls&&!stops&&!sends);
 puts("actor disabled: no storage/provider action PASS");
#else
 reset_case(0);available=0;if(!setjmp(stopped))app_main();CHECK(!opened&&!polls&&!stops&&!sends);
 for(volatile int mode=0;mode<25;mode++){
  reset_case(mode);if(!setjmp(stopped))app_main();
  if(mode==24){CHECK(!opened&&!polls&&!closed&&stops==1&&last_report_error==-108);continue;}
  CHECK(maintenance_reports==erase_count);
  CHECK(opened==1&&closed==1&&stops==1&&reports>=2&&!last_report.recording&&last_report_error<0);
  if(mode==21||mode==23){CHECK(sleeps==1&&resumes==1&&quiesces==2&&!erase_count);continue;}
  if(mode==22){CHECK(!erase_count&&!begin_count&&!sleeps&&polls==2&&quiesces==2&&!resumes);continue;}
  if(mode>=17){
   if(mode==17||mode==19)CHECK(erase_count==1&&begin_count==1&&boot_epoch==33&&quiesces==2);
   else CHECK(!erase_count&&!begin_count&&!sleeps);
   if(mode==17)CHECK(resumes==1);
   if(mode==19)CHECK(resumes==2);
   if(mode==18)CHECK(polls==2&&quiesces==2&&!resumes);
   continue;
  }
  if(mode==16){CHECK(!erase_count&&begin_count==1&&captures==1&&sleeps==1&&!sends&&last_report.sleep_prepared);CHECK(!memcmp(bytes+60,"DONE",4));continue;}
  if(mode==15){CHECK(erase_count==1&&begin_count==2&&boot_epoch==124&&captures==1&&resumes==1&&sends==1&&last_report.recording_session==124);continue;}
  if(mode>=13){CHECK(erase_count==1&&!erase_intent&&begin_count==1&&boot_epoch==33&&captures==1&&resumes==1);CHECK(last_report.recording_session==33);if(mode==14)CHECK(sends==32);continue;}
  if(mode==0)CHECK(polls==1&&sends==0); /* fatal ACK must not offer */
  else if(mode<5)CHECK(polls==2&&delays==1&&sends<=1); /* state-machine faults stop actor */
  else {
   CHECK(!sends&&!memcmp(bytes+60,"DONE",4));
   for(unsigned k=48;k<60;k++)CHECK(bytes[k]==255); /* never ACK/erase backlog */
   if(mode==5)CHECK(polls==3&&sleeps==1&&quiesces==1);
   if(mode==6)CHECK(polls==4&&sleeps==1&&quiesces==1); /* dirty blocked previous poll */
   if(mode==7)CHECK(polls==4&&!sleeps&&quiesces==2); /* bounded transport wait */
   if(mode==8||mode==9||mode==11||mode==12)CHECK(polls==3&&!sleeps&&quiesces==1);
   if(mode==10)CHECK(polls==5&&!sleeps&&quiesces==1&&resumes==1);
  }
 }
 puts("actor actual app_main: absent provider, ACK error, camera/contact/IRQ/clock faults stop PASS");
#endif
 return 0;
}
