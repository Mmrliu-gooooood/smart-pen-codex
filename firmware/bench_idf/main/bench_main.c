/* Explicit synthetic transport bench. No camera, pressure, OTA or offline log. */
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sdkconfig.h"
#include "esp_log.h"
#include "esp_random.h"
#include "esp_timer.h"
#include "nvs_flash.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_sm.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
#include "pen.h"
#include "bench_wire.h"

#define BENCH_DEVICE UINT32_C(0x42454e43)
#define UUID(n) BLE_UUID128_INIT(0xef,0xbe,0x00,0x00,0xb3,0x72,0x3a,0x96,0x6f,0x4d,0xd1,0x7a,n,0x00,0x3f,0x7c)
static const ble_uuid128_t service_uuid=UUID(1),tx_uuid=UUID(2),ack_uuid=UUID(3),info_uuid=UUID(4);
static const char *TAG="SYNTHETIC_BENCH";
static uint16_t connection=BLE_HS_CONN_HANDLE_NONE,tx_handle;
static uint8_t own_type;
static bool subscribed,configured,have_sent,complete;
static ble_addr_t approved;
static uint8_t packet[48];
static uint64_t session;
static uint32_t sequence;
static struct ble_npl_callout timer;
void ble_store_config_init(void);
static void advertise(void);
static bool authorized(uint16_t handle){
    struct ble_gap_conn_desc d;
    return configured && !ble_gap_conn_find(handle,&d) &&
        d.sec_state.encrypted && d.sec_state.authenticated && d.sec_state.bonded &&
        d.peer_id_addr.type==approved.type && !memcmp(d.peer_id_addr.val,approved.val,6);
}
static void make_sample(void){
    pen_sample p={.device=BENCH_DEVICE,.session=session,.seq=sequence,
        .timestamp_us=(uint64_t)esp_timer_get_time(),.page=UINT32_MAX,
        .x_um=(int32_t)(sequence%100)*100,.y_um=0,.confidence=0,.flags=PEN_GAP};
    /* Deliberately NOT VALID/CONTACT: production consumers must never draw. */
    if(pen_encode(packet,&p))abort();
}
static int access_cb(uint16_t handle,uint16_t attr,struct ble_gatt_access_ctxt *ctxt,void *arg){
    (void)attr;(void)arg;
    if(ctxt->op==BLE_GATT_ACCESS_OP_READ_CHR && !ble_uuid_cmp(ctxt->chr->uuid,&info_uuid.u)){
        const char *info="SYNTHETIC_BENCH_ONLY;device=42454e43;NO_VALID_COORDINATES";
        return os_mbuf_append(ctxt->om,info,strlen(info))?BLE_ATT_ERR_INSUFFICIENT_RES:0;
    }
    if(ctxt->op!=BLE_GATT_ACCESS_OP_WRITE_CHR || ble_uuid_cmp(ctxt->chr->uuid,&ack_uuid.u))return BLE_ATT_ERR_WRITE_NOT_PERMITTED;
    if(!authorized(handle))return BLE_ATT_ERR_INSUFFICIENT_AUTHEN;
    if(OS_MBUF_PKTLEN(ctxt->om)!=20)return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
    uint8_t b[20];uint16_t n;
    if(ble_hs_mbuf_to_flat(ctxt->om,b,sizeof(b),&n)||n!=20)return BLE_ATT_ERR_UNLIKELY;
    int result=bench_ack(b,n,true,true,true,true,have_sent,session,sequence);
    if(result<0)return BLE_ATT_ERR_VALUE_NOT_ALLOWED;
    if(result==0)return 0;
    uint32_t ack=sequence;
    ESP_LOGI(TAG,"bench ACK seq=%"PRIu32" (no flash erase)",ack);
    if(sequence==UINT32_MAX){complete=true;return 0;}
    sequence++;have_sent=false;make_sample();return 0;
}
static const struct ble_gatt_svc_def services[]={
 {.type=BLE_GATT_SVC_TYPE_PRIMARY,.uuid=&service_uuid.u,.characteristics=(struct ble_gatt_chr_def[]){
  {.uuid=&tx_uuid.u,.access_cb=access_cb,.flags=BLE_GATT_CHR_F_NOTIFY,.val_handle=&tx_handle},
  {.uuid=&ack_uuid.u,.access_cb=access_cb,.flags=BLE_GATT_CHR_F_WRITE|BLE_GATT_CHR_F_WRITE_ENC|BLE_GATT_CHR_F_WRITE_AUTHEN},
  {.uuid=&info_uuid.u,.access_cb=access_cb,.flags=BLE_GATT_CHR_F_READ},
  {0}}}, {0}};
static void tick(struct ble_npl_event *event){
    (void)event;
    if(!complete&&subscribed&&authorized(connection)){
        bool sent=true;
        for(unsigned i=0;i<3;i++){
            uint8_t fragment[20];
            if(bench_fragment(packet,sequence,i,fragment)){sent=false;break;}
            struct os_mbuf *om=ble_hs_mbuf_from_flat(fragment,sizeof(fragment));
            if(!om||ble_gatts_notify_custom(connection,tx_handle,om)){sent=false;break;}
        }
        if(sent)have_sent=true; /* queued, not durable; only host ACK advances */
    }
    ble_npl_callout_reset(&timer,ble_npl_time_ms_to_ticks32(250));
}
static int gap_cb(struct ble_gap_event *event,void *arg){
    (void)arg;
    switch(event->type){
    case BLE_GAP_EVENT_LINK_ESTAB:
        if(event->connect.status){advertise();break;}
        connection=event->connect.conn_handle;subscribed=false;
        struct ble_gap_conn_desc peer;
        if(ble_gap_conn_find(connection,&peer)||peer.peer_id_addr.type!=approved.type||memcmp(peer.peer_id_addr.val,approved.val,6)){
            ble_gap_terminate(connection,BLE_ERR_REM_USER_CONN_TERM);break;
        }
        if(ble_gap_security_initiate(connection))ble_gap_terminate(connection,BLE_ERR_REM_USER_CONN_TERM);
        break;
    case BLE_GAP_EVENT_DISCONNECT:connection=BLE_HS_CONN_HANDLE_NONE;subscribed=false;advertise();break;
    case BLE_GAP_EVENT_SUBSCRIBE:if(event->subscribe.attr_handle==tx_handle)subscribed=event->subscribe.cur_notify;break;
    case BLE_GAP_EVENT_ADV_COMPLETE:advertise();break;
    case BLE_GAP_EVENT_REPEAT_PAIRING:return BLE_GAP_REPEAT_PAIRING_IGNORE; /* never delete trusted bond automatically */
    case BLE_GAP_EVENT_PASSKEY_ACTION:{
        struct ble_sm_io io={0};io.action=event->passkey.params.action;
        if(io.action!=BLE_SM_IOACT_DISP){ble_gap_terminate(event->passkey.conn_handle,BLE_ERR_REM_USER_CONN_TERM);break;}
        io.passkey=esp_random()%1000000;
        ESP_LOGW(TAG,"Trusted local console: enter pairing passkey %06"PRIu32" on approved PC",io.passkey);
        if(ble_sm_inject_io(event->passkey.conn_handle,&io))ble_gap_terminate(event->passkey.conn_handle,BLE_ERR_REM_USER_CONN_TERM);
        break;}
    default:break;
    }return 0;
}
static void advertise(void){
    struct ble_hs_adv_fields f={0};f.flags=BLE_HS_ADV_F_DISC_GEN|BLE_HS_ADV_F_BREDR_UNSUP;
    f.uuids128=(ble_uuid128_t*)&service_uuid;f.num_uuids128=1;f.uuids128_is_complete=1;
    if(ble_gap_adv_set_fields(&f))return;
    memset(&f,0,sizeof(f));f.name=(uint8_t*)"PEN-SYNTHETIC-BENCH";f.name_len=strlen((char*)f.name);f.name_is_complete=1;
    if(ble_gap_adv_rsp_set_fields(&f))return;
    struct ble_gap_adv_params p={0};p.conn_mode=BLE_GAP_CONN_MODE_UND;p.disc_mode=BLE_GAP_DISC_MODE_GEN;
    int rc=ble_gap_adv_start(own_type,NULL,BLE_HS_FOREVER,&p,gap_cb,NULL);if(rc)ESP_LOGE(TAG,"advertise rc=%d",rc);
}
static void on_sync(void){
    if(ble_hs_id_infer_auto(0,&own_type)){ESP_LOGE(TAG,"address unavailable");return;}
    advertise();ble_npl_callout_reset(&timer,ble_npl_time_ms_to_ticks32(250));
}
static void host_task(void *arg){(void)arg;nimble_port_run();nimble_port_freertos_deinit();}
void app_main(void){
#ifndef CONFIG_PEN_SYNTHETIC_BENCH
    ESP_LOGE(TAG,"DISABLED. Explicit menuconfig synthetic opt-in required.");return;
#endif
    unsigned a[6];char tail;
    configured=sscanf(CONFIG_PEN_APPROVED_PEER,"%2x:%2x:%2x:%2x:%2x:%2x%c",a,a+1,a+2,a+3,a+4,a+5,&tail)==6;
    if(!configured){ESP_LOGE(TAG,"No approved peer configured; refusing BLE start");return;}
    approved.type=CONFIG_PEN_APPROVED_PEER_TYPE;
    for(unsigned i=0;i<6;i++)approved.val[i]=(uint8_t)a[5-i];
    /* Do NOT auto-erase NVS on init failure: it may hold pairing identities. */
    ESP_ERROR_CHECK(nvs_flash_init());ESP_ERROR_CHECK(nimble_port_init());
    do{esp_fill_random(&session,sizeof(session));}while(!session);
    make_sample();ble_svc_gap_init();ble_svc_gatt_init();
    ble_hs_cfg.sync_cb=on_sync;ble_hs_cfg.sm_io_cap=BLE_HS_IO_DISPLAY_ONLY;
    ble_hs_cfg.sm_bonding=1;ble_hs_cfg.sm_mitm=1;ble_hs_cfg.sm_sc=1;
    ble_hs_cfg.sm_our_key_dist=BLE_SM_PAIR_KEY_DIST_ENC|BLE_SM_PAIR_KEY_DIST_ID;
    ble_hs_cfg.sm_their_key_dist=BLE_SM_PAIR_KEY_DIST_ENC|BLE_SM_PAIR_KEY_DIST_ID;
    if(ble_gatts_count_cfg(services)||ble_gatts_add_svcs(services))abort();
    ble_svc_gap_device_name_set("PEN-SYNTHETIC-BENCH");ble_store_config_init();
    ble_npl_callout_init(&timer,nimble_port_get_dflt_eventq(),tick,NULL);
    ESP_LOGW(TAG,"SYNTHETIC ONLY: no valid coordinates, no camera, no OTA, no offline recording");
    nimble_port_freertos_init(host_task);
}
