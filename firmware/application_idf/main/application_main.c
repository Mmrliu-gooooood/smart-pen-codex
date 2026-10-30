#include "board_provider.h"
#include "storage_idf.h"
#include "partition_profile_idf.h"
#include "sdkconfig.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>
static pen_roi_workspace workspace; /* never put22KiB on main-task stack */
static pen_app application;
static pen_storage_idf persistence;
static const char *TAG="pen_app_candidate";
static void report(const pen_board_provider*b,int error){
 pen_app_status status={0};(void)pen_app_get_status(&application,&status);
 b->report_status(b->ctx,&status,error);
}
static void idle_blocked(const char*why){
 ESP_LOGW(TAG,"BLOCKED: %s; no further application actions until deliberate restart",why);
 for(;;)vTaskDelay(pdMS_TO_TICKS(1000));
}
void app_main(void){
 int enabled=0;
#ifdef CONFIG_PEN_APP_RUN_APPROVED_PROVIDER
 enabled=1;
#endif
 if(!enabled)idle_blocked("application provider execution is disabled");
 const pen_board_provider*b=pen_get_board_provider();
 if(!b||!b->device_id||!b->poll||!b->apply_actions||!b->safe_stop||!b->report_status||!b->stop_capture||
    !b->maintenance_idle_guard||!b->pending_transactions||!b->quiesce_transport||!b->resume_transport||!b->max_sleep_quiesce_us||
    b->config.camera_qualified!=1||!b->config.map_tip)idle_blocked("reviewed sensor/pose/board provider absent");
 if(pen_application_partition_guard()!=ESP_OK){
  report(b,-108);b->safe_stop(b->ctx);idle_blocked("explicit Flash profile/physical capacity refused");
 }
 /* Opening may recover a previously persisted erase intent. No autoformat or
  * secret/eFuse operations; real partition approval still required separately. */
 if(pen_storage_idf_open(&persistence,1,"pen_records",b->device_id)!=ESP_OK){report(b,-101);b->safe_stop(b->ctx);idle_blocked("storage refused configured partition");}
 uint64_t epoch=0;
 int startup=pen_app_needs_maintenance(&persistence.store)?
   pen_app_init_replay(&application,&persistence.store,&workspace,&b->config):
   (pen_storage_idf_begin_boot(&persistence,&epoch)!=ESP_OK?-1:
    pen_app_init(&application,&persistence.store,&workspace,&b->config));
 if(startup){
  report(b,-102);b->safe_stop(b->ctx);pen_storage_idf_close(&persistence);idle_blocked("durable session/application init failed");
 }
 if(application.replay_only&&b->stop_capture(b->ctx)){
  report(b,-106);b->safe_stop(b->ctx);pen_storage_idf_close(&persistence);idle_blocked("capture isolation failed");
 }
 report(b,0);
 pen_app_input input={0};int sleep_pending=0;uint64_t sleep_started=0;int fault_code=-100;uint64_t replay_idle_since=0;int replay_idle=0;
 for(;;){
  pen_app_input next={0};int e=b->poll(b->ctx,&next);
  if(e<0)break;
  if(e==0)input=next;
  else {input.frame=NULL;input.now_us=(uint64_t)esp_timer_get_time();}
  /* Synchronous recorder commits before return; provider reports only other
   * genuine uncommitted transactions, NEVER durable offline backlog. */
  int pending_status=b->pending_transactions(b->ctx);
  if(pending_status<0)break;
  input.storage_pending=(uint8_t)(pending_status!=0);
  if(application.replay_only){
   /* Capacity recovery is not fault clearing: no decoder/contact writes run.
    * Keep authenticated replay alive while unACK data prevents erase. */
   report(b,-2);
   uint64_t replay_now=(uint64_t)esp_timer_get_time();
   if(input.raw_contact||input.pickup_irq_low){
    replay_idle=0;if(sleep_pending){if(b->resume_transport(b->ctx))break;sleep_pending=0;}
   }else if(!replay_idle){replay_idle=1;replay_idle_since=replay_now;}
   if(replay_idle&&replay_now<replay_idle_since)break;
   int backlog=pen_app_pending(&application);if(backlog<0)break;
   if(backlog&&sleep_pending&&!input.usb_sleep_allowed){
    if(b->resume_transport(b->ctx))break;
    sleep_pending=0;
   }
   if(backlog&&replay_idle&&input.usb_sleep_allowed&&replay_now-replay_idle_since>=b->config.contact.idle_us){
    if(!sleep_pending){sleep_pending=1;sleep_started=replay_now;}
    int quiet=b->quiesce_transport(b->ctx);int dirty=b->pending_transactions(b->ctx);
    uint64_t end=(uint64_t)esp_timer_get_time();
    if(quiet<0||dirty<0||end<sleep_started||end-sleep_started>=b->max_sleep_quiesce_us)break;
    if(!quiet&&!dirty){
     if(pen_app_prepare_replay_sleep(&application,1,1,0,1))break;
     end=(uint64_t)esp_timer_get_time();
     if(end<sleep_started||end-sleep_started>=b->max_sleep_quiesce_us)break;
     report(b,-2);
     if(b->apply_actions(b->ctx,PEN_CP_SLEEP_REQUEST))break;
     report(b,-107);b->safe_stop(b->ctx);pen_storage_idf_close(&persistence);
     idle_blocked("capacity replay sleep returned; reopen retained log on next boot");
    }
    vTaskDelay(pdMS_TO_TICKS(1));continue;
   }
   if(!input.raw_contact&&!input.pickup_irq_low&&(!pending_status||sleep_pending)&&!backlog){
    if(!sleep_pending){sleep_pending=1;sleep_started=(uint64_t)esp_timer_get_time();}
    uint64_t start=sleep_started;
    int quiet=b->quiesce_transport(b->ctx);int dirty=b->pending_transactions(b->ctx);
    uint64_t end=(uint64_t)esp_timer_get_time();
    if(quiet<0||dirty<0||end<start||end-start>=b->max_sleep_quiesce_us)break;
    if(!quiet&&!dirty){
     int guard=b->maintenance_idle_guard(b->ctx);
     if(guard<0)break;
     if(!guard){if(b->resume_transport(b->ctx))break;sleep_pending=0;replay_idle=0;goto replay_transport;}
     report(b,-109); /* maintenance busy: recording already stopped */
     end=(uint64_t)esp_timer_get_time();
     if(end<start||end-start>=b->max_sleep_quiesce_us)break;
     int reclaimed=pen_app_reclaim(&application,1,1,0,1);
     end=(uint64_t)esp_timer_get_time();
     if(reclaimed<0||end<start||end-start>=b->max_sleep_quiesce_us)break;
     if(reclaimed==0){
      if(pen_storage_idf_begin_boot(&persistence,&epoch)!=ESP_OK||
         pen_app_init(&application,&persistence.store,&workspace,&b->config))break;
      if(b->resume_transport(b->ctx))break;
      sleep_pending=0;replay_idle=0;report(b,0);continue;
     }
    }
    if(quiet||dirty){vTaskDelay(pdMS_TO_TICKS(1));continue;}
    if(b->resume_transport(b->ctx))break;
    sleep_pending=0;
   }
   goto replay_transport;
  }
  pen_app_result result;
  int step_status=pen_app_step(&application,&input,&result);
  if(step_status==-2&&application.replay_only){
   report(b,-2);if(b->stop_capture(b->ctx))break;
   goto replay_transport;
  }
  if(step_status||result.recorder.contact_faults){fault_code=step_status?step_status:-103;break;}
  unsigned actions=result.recorder.actions;
  if(actions&PEN_CP_SLEEP_REQUEST){sleep_pending=1;sleep_started=(uint64_t)esp_timer_get_time();}
  if(sleep_pending&&(input.raw_contact||input.pickup_irq_low||!input.usb_sleep_allowed||application.recorder.contact.phase!=PEN_CP_ASLEEP)){
   if(b->resume_transport(b->ctx)||pen_app_cancel_sleep(&application,input.now_us))break;
   sleep_pending=0;
  }
  actions&=~PEN_CP_SLEEP_REQUEST;
  if(actions&&b->apply_actions(b->ctx,actions))break;
  if(sleep_pending){
   int quiet=b->quiesce_transport(b->ctx);pending_status=b->pending_transactions(b->ctx);
   if(quiet<0||pending_status<0)break;
   uint64_t now=(uint64_t)esp_timer_get_time();
   if(now<sleep_started||now-sleep_started>=b->max_sleep_quiesce_us){fault_code=-105;break;}
   if(quiet==0&&pending_status==0){
    if(pen_app_prepare_sleep(&application,0,1)){fault_code=-104;break;}
    now=(uint64_t)esp_timer_get_time();
    if(now<sleep_started||now-sleep_started>=b->max_sleep_quiesce_us){fault_code=-105;break;}
    int sleep_backlog=pen_app_pending(&application);
    if(sleep_backlog<0){fault_code=-104;break;}
    if(pen_app_needs_maintenance(&persistence.store)&&sleep_backlog==0){
     if(b->maintenance_idle_guard(b->ctx)!=1){fault_code=-104;break;}
     report(b,-109); /* visible before synchronous full-log scan/erase */
     now=(uint64_t)esp_timer_get_time();
     if(now<sleep_started||now-sleep_started>=b->max_sleep_quiesce_us){fault_code=-105;break;}
     int reclaimed=pen_app_reclaim(&application,1,1,0,1);
     if(reclaimed<0){fault_code=-104;break;}
    }
    now=(uint64_t)esp_timer_get_time();
    if(now<sleep_started||now-sleep_started>=b->max_sleep_quiesce_us){fault_code=-105;break;}
    report(b,0);
    if(b->apply_actions(b->ctx,PEN_CP_SLEEP_REQUEST)){fault_code=-104;break;}
    /* Deep sleep normally does not return. A returning provider must not reuse
     * this stopped session/tickets; require explicit boot/reinitialization. */
    report(b,-107);b->safe_stop(b->ctx);pen_storage_idf_close(&persistence);
    idle_blocked("sleep returned; durable session restart required");
   }
   vTaskDelay(pdMS_TO_TICKS(1));continue;
  }
 replay_transport: ;
  pen_link_security security={0};
  if(b->link_security&&b->link_security(b->ctx,&security)==0){
   if(b->next_ack){
    for(unsigned n=0;n<8;n++){
     uint64_t session=0;uint32_t seq=0;pen_link_security receipt={0};
     int a=b->next_ack(b->ctx,&session,&seq,&receipt);
     if(a<0){e=-1;break;}
     if(a>0)break;
     memset(&security,0,sizeof security);
     if(b->link_security(b->ctx,&security)!=0)break;
     int status=pen_app_ack(&application,&security,&receipt,session,seq);
     if(status==-1){e=-1;break;} /* persistence fault is terminal */
     /* -3 is rejected forged/stale/unauthorized ACK, not permission to erase. */
    }
   }
   if(e<0)break;
   memset(&security,0,sizeof security);
   if(b->send_packet&&b->link_security(b->ctx,&security)==0){
    int status=pen_app_offer(&application,&security,b->send_packet,b->ctx);if(status==-1)break;
   }
  }
  vTaskDelay(pdMS_TO_TICKS(1)); /* scheduler yield, not a measured frame-rate guarantee */
 }
 pen_store_stop(&persistence.store);report(b,fault_code);
 b->safe_stop(b->ctx);pen_storage_idf_close(&persistence);
 idle_blocked("actor fault latched; requires deliberate restart");
}
