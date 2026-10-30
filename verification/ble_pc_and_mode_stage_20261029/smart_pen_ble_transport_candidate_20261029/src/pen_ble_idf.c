#include "pen_ble_idf.h"
#include "sdkconfig.h"
#include <string.h>
#if defined(CONFIG_PEN_BLE_TRANSPORT) && defined(CONFIG_PEN_BLE_DEV_PAIRING)
#if !defined(CONFIG_BT_NIMBLE_SM_SC) || defined(CONFIG_BT_NIMBLE_SM_LEGACY) || defined(CONFIG_BT_NIMBLE_SM_SC_DEBUG_KEYS) || !defined(CONFIG_BT_NIMBLE_NVS_PERSIST) || CONFIG_BT_NIMBLE_SM_LVL != 4 || CONFIG_BT_NIMBLE_MAX_CONNECTIONS != 1
#error "Requires SC-only, no debug keys, persistent bonds"
#endif
#include <stdatomic.h>
#include "esp_random.h"
#include "esp_timer.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_hs_mbuf.h"
#include "host/ble_sm.h"
#include "host/util/util.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
#include "store/config/ble_store_config.h"
#define RPC_TIMEOUT_MS 1000
/* Official bleprph declares this function; v5.4 header omits it. */
void ble_store_config_init(void);
static pen_ble_core core;
static pen_ble_local_io local_io;
static uint64_t boot,pairing_deadline_us;
static uint32_t connections;
static uint16_t connection=BLE_HS_CONN_HANDLE_NONE,tx_handle;
static uint8_t own_addr_type;
static int approved,pairing_allowed,store_fault,synced,started,start_attempted;
static int selected,passkey_shown;
static struct ble_npl_callout pairing_timer;
static atomic_bool rpc_failed;
static _Atomic(TaskHandle_t) host_task;
static SemaphoreHandle_t rpc_mutex,rpc_done;
static struct ble_npl_event rpc_event;
static ble_store_write_fn *original_store_write;
static const ble_uuid128_t service_uuid=BLE_UUID128_INIT(0xef,0xbe,0x00,0x00,0xb3,0x72,0x3a,0x96,0x6f,0x4d,0xd1,0x7a,0x01,0x00,0x3f,0x7c);
static const ble_uuid128_t tx_uuid=BLE_UUID128_INIT(0xef,0xbe,0x00,0x00,0xb3,0x72,0x3a,0x96,0x6f,0x4d,0xd1,0x7a,0x02,0x00,0x3f,0x7c);
static const ble_uuid128_t ack_uuid=BLE_UUID128_INIT(0xef,0xbe,0x00,0x00,0xb3,0x72,0x3a,0x96,0x6f,0x4d,0xd1,0x7a,0x03,0x00,0x3f,0x7c);
static const ble_uuid128_t info_uuid=BLE_UUID128_INIT(0xef,0xbe,0x00,0x00,0xb3,0x72,0x3a,0x96,0x6f,0x4d,0xd1,0x7a,0x04,0x00,0x3f,0x7c);
static uint64_t now(void){int64_t t=esp_timer_get_time();if(t<0){core.faulted=1;return 0;}return (uint64_t)t;}
static void refresh(void){
 struct ble_gap_conn_desc d;pen_link_security s={0};unsigned key=0;
 if(connection!=BLE_HS_CONN_HANDLE_NONE&&ble_gap_conn_find(connection,&d)==0){
  s=(pen_link_security){.encrypted=d.sec_state.encrypted,.authenticated=d.sec_state.authenticated,
   .bonded=d.sec_state.bonded,.approved_peer=(uint8_t)(approved&&!store_fault),.connection_epoch=(boot<<32)|connections};key=d.sec_state.key_size;
  if(s.encrypted&&s.authenticated&&s.bonded){
   struct ble_store_key_sec k={.peer_addr=d.peer_id_addr};struct ble_store_value_sec v={0};
   k.peer_addr.type&=1; /* identity 2/3 -> public/random 0/1 */
   if(ble_store_read_our_sec(&k,&v)||!v.ltk_present||!v.sc||!v.authenticated||v.key_size!=16)s.bonded=0;
   memset(&v,0,sizeof v); /* never expose or log stored key material */
  }
 }
 if(store_fault||atomic_load(&rpc_failed))core.faulted=1;
 pen_ble_core_link(&core,&s,key);
}
static void peer_info(pen_ble_peer*p){
 memset(p,0,sizeof *p);refresh();p->security=core.security;p->epoch=core.security.connection_epoch;p->handle=connection;
 struct ble_gap_conn_desc d;if(connection!=BLE_HS_CONN_HANDLE_NONE&&!ble_gap_conn_find(connection,&d)){memcpy(p->address,d.peer_id_addr.val,6);p->address_type=d.peer_id_addr.type;}
}
static int store_write(int type,const union ble_store_value *v){
 int allowed=!core.faulted&&!store_fault&&(type==BLE_STORE_OBJ_TYPE_LOCAL_IRK||
  (pairing_allowed&&!core.quiesced&&(approved||(pairing_deadline_us&&now()<pairing_deadline_us))));
 if((type==BLE_STORE_OBJ_TYPE_OUR_SEC||type==BLE_STORE_OBJ_TYPE_PEER_SEC)&&v->sec.ltk_present&&
    (!v->sec.sc||!v->sec.authenticated||v->sec.key_size!=16))allowed=0;
 int r=allowed&&original_store_write?original_store_write(type,v):BLE_HS_ESTORE_FAIL;
 if(r)store_fault=1; /* callback may hold host lock; no BLE API recursion */
 return r;
}
static int store_status(struct ble_store_status_event*e,void*arg){(void)e;(void)arg;store_fault=1;return BLE_HS_ESTORE_CAP;}
static int access_gatt(uint16_t conn,uint16_t attr,struct ble_gatt_access_ctxt*c,void*arg){
 (void)attr;refresh();
 if(conn!=connection||core.faulted||core.quiesced||!core.security.encrypted||!core.security.authenticated||!core.security.bonded||!core.security.approved_peer)return BLE_ATT_ERR_INSUFFICIENT_AUTHEN;
 if(arg==(void*)1&&c->op==BLE_GATT_ACCESS_OP_WRITE_CHR){
  uint8_t b[20];uint16_t n=0;
  if(OS_MBUF_PKTLEN(c->om)!=sizeof b||ble_hs_mbuf_to_flat(c->om,b,sizeof b,&n)||n!=sizeof b)return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
  int r=pen_ble_core_receive(&core,b,n,now());return r==0?0:r==1?BLE_ATT_ERR_INSUFFICIENT_RES:BLE_ATT_ERR_VALUE_NOT_ALLOWED;
 }
 if(arg==(void*)2&&c->op==BLE_GATT_ACCESS_OP_READ_CHR){
  static const char info[]="PEN/1 RECORD48 FRAG3 ACK20 DEV_USB; NO_SENSOR";
  return os_mbuf_append(c->om,info,sizeof info-1)==0?0:BLE_ATT_ERR_INSUFFICIENT_RES;
 }
 return BLE_ATT_ERR_READ_NOT_PERMITTED;
}
static const struct ble_gatt_svc_def services[]={
 {.type=BLE_GATT_SVC_TYPE_PRIMARY,.uuid=&service_uuid.u,.characteristics=(struct ble_gatt_chr_def[]){
  {.uuid=&tx_uuid.u,.access_cb=access_gatt,.flags=BLE_GATT_CHR_F_NOTIFY,.val_handle=&tx_handle},
  {.uuid=&ack_uuid.u,.access_cb=access_gatt,.arg=(void*)1,.flags=BLE_GATT_CHR_F_WRITE|BLE_GATT_CHR_F_WRITE_ENC|BLE_GATT_CHR_F_WRITE_AUTHEN,.min_key_size=16},
  {.uuid=&info_uuid.u,.access_cb=access_gatt,.arg=(void*)2,.flags=BLE_GATT_CHR_F_READ|BLE_GATT_CHR_F_READ_ENC|BLE_GATT_CHR_F_READ_AUTHEN,.min_key_size=16},{0}}},{0}};
static int gap(struct ble_gap_event*,void*);
static int advertise(void){
 if(!selected||!synced||core.quiesced||core.faulted||connection!=BLE_HS_CONN_HANDLE_NONE)return 1;
 struct ble_hs_adv_fields f={0};f.flags=BLE_HS_ADV_F_DISC_GEN|BLE_HS_ADV_F_BREDR_UNSUP;
 f.uuids128=(ble_uuid128_t*)&service_uuid;f.num_uuids128=1;f.uuids128_is_complete=1;
 if(ble_gap_adv_set_fields(&f))return -1;
 struct ble_gap_adv_params p={.conn_mode=BLE_GAP_CONN_MODE_UND,.disc_mode=BLE_GAP_DISC_MODE_GEN};
 int r=ble_gap_adv_start(own_addr_type,NULL,60000,&p,gap,NULL);
 return r==0?0:r==BLE_HS_EALREADY?1:-1;
}
static int gap(struct ble_gap_event*e,void*arg){
 (void)arg;
 switch(e->type){
 case BLE_GAP_EVENT_CONNECT: {
  if(e->connect.status)return 0;
  struct ble_gap_conn_desc d;
  int match=selected&&ble_gap_conn_find(e->connect.conn_handle,&d)==0;
  selected=0; /* one local window, one connection, no automatic retry */
  if(!match||connection!=BLE_HS_CONN_HANDLE_NONE||connections==UINT32_MAX||core.quiesced||core.faulted){
   (void)ble_gap_terminate(e->connect.conn_handle,BLE_ERR_REM_USER_CONN_TERM);return 0;
  }
  connection=e->connect.conn_handle;connections++;approved=0;pairing_allowed=1;passkey_shown=0;pairing_deadline_us=now()+60000000u;refresh();
  int r=ble_npl_callout_reset(&pairing_timer,ble_npl_time_ms_to_ticks32(60000));
  if(!r)r=ble_gap_security_initiate(connection);
  if(r&&r!=BLE_HS_EALREADY){pairing_allowed=0;core.faulted=1;(void)ble_gap_terminate(connection,BLE_ERR_AUTH_FAIL);}
  return 0;
 }
 case BLE_GAP_EVENT_DISCONNECT:
  if(e->disconnect.conn.conn_handle==connection){connection=BLE_HS_CONN_HANDLE_NONE;approved=0;pairing_allowed=0;pairing_deadline_us=0;ble_npl_callout_stop(&pairing_timer);refresh();}
  /* No automatic reconnect advertising. Local operator must reopen window. */
  return 0;
 case BLE_GAP_EVENT_ENC_CHANGE:refresh();return 0;
 case BLE_GAP_EVENT_SUBSCRIBE:
  if(e->subscribe.conn_handle==connection&&e->subscribe.attr_handle==tx_handle){refresh();pen_ble_core_subscribe(&core,e->subscribe.cur_notify);}return 0;
 case BLE_GAP_EVENT_MTU:
  if(e->mtu.conn_handle==connection)pen_ble_core_mtu(&core,e->mtu.value);
  return 0;
 case BLE_GAP_EVENT_ADV_COMPLETE:selected=0;return 0;
 case BLE_GAP_EVENT_REPEAT_PAIRING:return BLE_GAP_REPEAT_PAIRING_IGNORE;
 case BLE_GAP_EVENT_PASSKEY_ACTION: {
  if(e->passkey.conn_handle!=connection||!pairing_allowed||core.quiesced||now()>=pairing_deadline_us||passkey_shown||e->passkey.params.action!=BLE_SM_IOACT_DISP){
   approved=0;pairing_allowed=0;pairing_deadline_us=0;refresh();
   if(ble_gap_terminate(e->passkey.conn_handle,BLE_ERR_AUTH_FAIL))core.faulted=1;
   return 0;
  }
  /* Rejection sampling avoids modulo bias, never a hardcoded or persisted key. */
  passkey_shown=1;
  uint32_t x;do{x=esp_random();}while(x>=4294000000u);
  struct ble_sm_io io={.action=BLE_SM_IOACT_DISP,.passkey=x%1000000u};pen_ble_peer peer;peer_info(&peer);
  if(!local_io.show_passkey||local_io.show_passkey(local_io.ctx,&peer,io.passkey)||ble_sm_inject_io(connection,&io)){
   approved=0;pairing_allowed=0;pairing_deadline_us=0;refresh();if(ble_gap_terminate(connection,BLE_ERR_AUTH_FAIL))core.faulted=1;
  }
  return 0;
 }
 /* notify_custom invokes this synchronously. Do not RPC or create ACK ticket. */
 case BLE_GAP_EVENT_NOTIFY_TX:return 0;
 default:return 0;
 }
}
static int notify(void*unused,const uint8_t*b,size_t n,uint64_t epoch){
 (void)unused;refresh();if(!pen_ble_core_ready(&core)||core.security.connection_epoch!=epoch)return 1;
 struct os_mbuf*om=ble_hs_mbuf_from_flat(b,(uint16_t)n);if(!om)return 1;
 int r=ble_gatts_notify_custom(connection,tx_handle,om); /* consumes on ALL paths */
 if(!r)return 0;
 return r==BLE_HS_ENOMEM||r==BLE_HS_EBUSY||r==BLE_HS_ENOTCONN?1:-1;
}
enum operation{OP_SECURITY,OP_SEND,OP_AUTHORIZE,OP_PEER,OP_APPROVE,OP_ADV,OP_QUIET,OP_RESUME};
static struct {enum operation op;uint64_t epoch;uint8_t packet[48];pen_link_security security;pen_ble_ticket ticket;pen_ble_grant grant;pen_ble_peer peer;int result;} request;
static void dispatch(struct ble_npl_event*e){
 (void)e;int r=-1;
 if(!atomic_load(&rpc_failed)){
  refresh();
  switch(request.op){
  case OP_SECURITY:request.security=core.security;r=core.faulted?-1:0;break;
  case OP_SEND:r=pen_ble_core_send(&core,request.packet,48,request.epoch,now(),notify,NULL);break;
  case OP_AUTHORIZE:r=pen_ble_core_authorize(&core,&request.ticket,&request.grant);break;
  case OP_PEER:peer_info(&request.peer);r=0;break;
  case OP_APPROVE:
   if(request.epoch&&request.epoch==core.security.connection_epoch&&!core.quiesced&&!core.faulted){
    if(core.security.encrypted&&core.security.authenticated&&core.security.bonded&&pairing_allowed&&!store_fault&&now()<pairing_deadline_us){approved=1;pairing_deadline_us=0;ble_npl_callout_stop(&pairing_timer);refresh();r=0;}else r=1;
   }else r=1;
   break;
  case OP_ADV:
   if(connection==BLE_HS_CONN_HANDLE_NONE&&!ble_gap_adv_active()){selected=1;r=advertise();if(r)selected=0;}else r=1;
   break;
  case OP_QUIET:
   pen_ble_core_quiesce(&core,1);selected=0;pairing_allowed=0;approved=0;pairing_deadline_us=0;ble_npl_callout_stop(&pairing_timer);
   {int stop=ble_gap_adv_stop();if((stop!=0&&stop!=BLE_HS_EALREADY)||ble_gap_adv_active()){r=-1;break;}}
   if(connection!=BLE_HS_CONN_HANDLE_NONE){int t=ble_gap_terminate(connection,BLE_ERR_REM_USER_CONN_TERM);r=t==0||t==BLE_HS_EALREADY?1:-1;}else r=0;
   break;
  case OP_RESUME:pen_ble_core_quiesce(&core,0);r=0;break;
  }
 }
 request.result=r;xSemaphoreGive(rpc_done);
}
/* Exactly one bounded static request: no task-stack pointer can be retained on
 * timeout. A timeout poisons the channel permanently; late authorization cannot
 * trigger a Flash write because no caller receives its grant. */
static int begin(enum operation op){
 if(!started||atomic_load(&rpc_failed)||xTaskGetCurrentTaskHandle()==atomic_load(&host_task))return -1;
 if(xSemaphoreTake(rpc_mutex,pdMS_TO_TICKS(RPC_TIMEOUT_MS))!=pdTRUE)return -1;
 if(atomic_load(&rpc_failed)){xSemaphoreGive(rpc_mutex);return -1;}
 memset(&request,0,sizeof request);request.op=op;return 0;
}
static int call(void){
 ble_npl_eventq_put(nimble_port_get_dflt_eventq(),&rpc_event);
 if(xSemaphoreTake(rpc_done,pdMS_TO_TICKS(RPC_TIMEOUT_MS))!=pdTRUE){atomic_store(&rpc_failed,1);return -1;}
 return request.result;
}
static int end(int r){xSemaphoreGive(rpc_mutex);return r;}
static int security(void*ctx,pen_link_security*s){(void)ctx;if(!s||begin(OP_SECURITY))return -1;int r=call();if(!r)*s=request.security;return end(r);}
static int send_packet(void*ctx,const uint8_t*b,size_t n,uint64_t epoch){(void)ctx;if(!b||n!=48||begin(OP_SEND))return -1;memcpy(request.packet,b,48);request.epoch=epoch;return end(call());}
static int authorize(void*ctx,const pen_ble_ticket*t,pen_ble_grant*g){(void)ctx;if(!t||!g||begin(OP_AUTHORIZE))return -1;request.ticket=*t;int r=call();if(!r)*g=request.grant;return end(r);}
static const pen_ble_backend backend={.security=security,.send=send_packet,.authorize=authorize};
const pen_ble_backend*pen_ble_transport_backend(void){return started?&backend:NULL;}
int pen_ble_dev_peer(pen_ble_peer*p){if(!p||begin(OP_PEER))return -1;int r=call();if(!r)*p=request.peer;return end(r);}
int pen_ble_dev_approve(uint64_t epoch){if(begin(OP_APPROVE))return -1;request.epoch=epoch;return end(call());}
int pen_ble_dev_advertise(void){if(begin(OP_ADV))return -1;return end(call());}
int pen_ble_quiesce(void){if(begin(OP_QUIET))return -1;return end(call());}
int pen_ble_resume(void){if(begin(OP_RESUME))return -1;return end(call());}
static void reset(int reason){(void)reason;core.faulted=1;synced=0;connection=BLE_HS_CONN_HANDLE_NONE;refresh();}
static void pairing_expired(struct ble_npl_event*e){
 (void)e;
 if(!pairing_allowed||approved||connection==BLE_HS_CONN_HANDLE_NONE||!pairing_deadline_us||now()<pairing_deadline_us)return;
 approved=0;pairing_allowed=0;pairing_deadline_us=0;refresh();
 if(connection!=BLE_HS_CONN_HANDLE_NONE&&ble_gap_terminate(connection,BLE_ERR_AUTH_FAIL))core.faulted=1;
}
static void sync_host(void){if(ble_hs_util_ensure_addr(0)||ble_hs_id_infer_auto(0,&own_addr_type)){core.faulted=1;return;}synced=1;}
static void run(void*p){(void)p;atomic_store(&host_task,xTaskGetCurrentTaskHandle());nimble_port_run();atomic_store(&rpc_failed,1);nimble_port_freertos_deinit();}
static esp_err_t reserve_epoch(void){
 nvs_handle_t h;esp_err_t e=nvs_open("pen_ble",NVS_READWRITE,&h);if(e!=ESP_OK)return e;
 uint64_t v=0;e=nvs_get_u64(h,"boot_epoch",&v);
 if(e==ESP_ERR_NVS_NOT_FOUND)e=ESP_OK;
 if(e==ESP_OK&&v>=UINT32_MAX)e=ESP_ERR_INVALID_STATE;
 if(e==ESP_OK)e=nvs_set_u64(h,"boot_epoch",v+1);
 if(e==ESP_OK)e=nvs_commit(h);
 if(e==ESP_OK)boot=v+1;
 nvs_close(h);return e;
}
esp_err_t pen_ble_dev_start(const pen_ble_local_io*io,int consent){
 if(start_attempted||!io||!io->show_passkey||consent!=1)return ESP_ERR_INVALID_ARG;
 start_attempted=1; /* partial initialization requires deliberate reboot, not retry */
 /* Runtime-only persistent writes. Never autoerase NVS, keys, or epochs. */
 esp_err_t e=nvs_flash_init();if(e!=ESP_OK)return e;e=reserve_epoch();if(e!=ESP_OK)return e;
 rpc_mutex=xSemaphoreCreateMutex();rpc_done=xSemaphoreCreateBinary();if(!rpc_mutex||!rpc_done)return ESP_ERR_NO_MEM;
 local_io=*io;pen_ble_core_init(&core);atomic_store(&rpc_failed,0);
 e=nimble_port_init();if(e!=ESP_OK)return e;
 ble_hs_cfg.reset_cb=reset;ble_hs_cfg.sync_cb=sync_host;
 ble_hs_cfg.sm_io_cap=BLE_HS_IO_DISPLAY_ONLY;ble_hs_cfg.sm_bonding=1;ble_hs_cfg.sm_mitm=1;ble_hs_cfg.sm_sc=1;
 ble_hs_cfg.sm_our_key_dist=BLE_SM_PAIR_KEY_DIST_ENC|BLE_SM_PAIR_KEY_DIST_ID;
 ble_hs_cfg.sm_their_key_dist=BLE_SM_PAIR_KEY_DIST_ENC|BLE_SM_PAIR_KEY_DIST_ID;
 ble_svc_gap_init();ble_svc_gatt_init();
 if(ble_svc_gap_device_name_set("Pen dev USB consent")||ble_gatts_count_cfg(services)||ble_gatts_add_svcs(services))return ESP_FAIL;
 ble_store_config_init();original_store_write=ble_hs_cfg.store_write_cb;ble_hs_cfg.store_write_cb=store_write;ble_hs_cfg.store_status_cb=store_status;
 ble_npl_event_init(&rpc_event,dispatch,NULL);
 if(ble_npl_callout_init(&pairing_timer,nimble_port_get_dflt_eventq(),pairing_expired,NULL))return ESP_FAIL;
 started=1;nimble_port_freertos_init(run);return ESP_OK;
}
#else
esp_err_t pen_ble_dev_start(const pen_ble_local_io*io,int consent){(void)io;(void)consent;return ESP_ERR_NOT_SUPPORTED;}
int pen_ble_dev_advertise(void){return -1;}
int pen_ble_dev_peer(pen_ble_peer*p){if(p)memset(p,0,sizeof *p);return -1;}
int pen_ble_dev_approve(uint64_t e){(void)e;return -1;}
int pen_ble_quiesce(void){return -1;}
int pen_ble_resume(void){return -1;}
const pen_ble_backend*pen_ble_transport_backend(void){return NULL;}
#endif
