#ifndef REVIEW_ALL_H
#define REVIEW_ALL_H
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_ERR_NVS_NOT_FOUND 1
#define ESP_ERR_INVALID_STATE 2
#define ESP_ERR_INVALID_ARG 3
#define ESP_ERR_NO_MEM 4
#define ESP_ERR_NOT_SUPPORTED 5
#define ESP_FAIL 6
typedef int nvs_handle_t;
#define NVS_READWRITE 1
int nvs_open(const char*,int,nvs_handle_t*);int nvs_get_u64(nvs_handle_t,const char*,uint64_t*);int nvs_set_u64(nvs_handle_t,const char*,uint64_t);int nvs_commit(nvs_handle_t);void nvs_close(nvs_handle_t);int nvs_flash_init(void);
uint32_t esp_random(void);int64_t esp_timer_get_time(void);
typedef struct test_sem*SemaphoreHandle_t;typedef uintptr_t TaskHandle_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
SemaphoreHandle_t xSemaphoreCreateMutex(void);SemaphoreHandle_t xSemaphoreCreateBinary(void);int xSemaphoreTake(SemaphoreHandle_t,unsigned);int xSemaphoreGive(SemaphoreHandle_t);TaskHandle_t xTaskGetCurrentTaskHandle(void);
struct ble_npl_event {void(*fn)(struct ble_npl_event*);void*arg;};struct ble_npl_eventq {int unused;};struct ble_npl_callout {struct ble_npl_event event;uint32_t ticks;int active;};int ble_npl_callout_init(struct ble_npl_callout*,struct ble_npl_eventq*,void(*)(struct ble_npl_event*),void*);int ble_npl_callout_reset(struct ble_npl_callout*,uint32_t);void ble_npl_callout_stop(struct ble_npl_callout*);uint32_t ble_npl_time_ms_to_ticks32(uint32_t);void ble_npl_event_init(struct ble_npl_event*,void(*)(struct ble_npl_event*),void*);void ble_npl_eventq_put(struct ble_npl_eventq*,struct ble_npl_event*);struct ble_npl_eventq*nimble_port_get_dflt_eventq(void);int nimble_port_init(void);void nimble_port_run(void);void nimble_port_freertos_init(void(*)(void*));void nimble_port_freertos_deinit(void);
#define BLE_HS_CONN_HANDLE_NONE 0xffff
#define BLE_HS_ESTORE_FAIL 10
#define BLE_HS_ESTORE_CAP 11
#define BLE_HS_EALREADY 12
#define BLE_HS_ENOMEM 13
#define BLE_HS_EBUSY 14
#define BLE_HS_ENOTCONN 15
#define BLE_ATT_ERR_INSUFFICIENT_AUTHEN 16
#define BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN 17
#define BLE_ATT_ERR_INSUFFICIENT_RES 18
#define BLE_ATT_ERR_VALUE_NOT_ALLOWED 19
#define BLE_ATT_ERR_READ_NOT_PERMITTED 20
#define BLE_ERR_REM_USER_CONN_TERM 21
#define BLE_ERR_AUTH_FAIL 22
#define BLE_GAP_REPEAT_PAIRING_IGNORE 23
#define BLE_SM_IOACT_DISP 24
#define BLE_HS_IO_DISPLAY_ONLY 25
#define BLE_STORE_OBJ_TYPE_LOCAL_IRK 99
#define BLE_STORE_OBJ_TYPE_OUR_SEC 98
#define BLE_STORE_OBJ_TYPE_PEER_SEC 97
#define BLE_SM_PAIR_KEY_DIST_ENC 1
#define BLE_SM_PAIR_KEY_DIST_ID 2
#define BLE_GATT_ACCESS_OP_WRITE_CHR 1
#define BLE_GATT_ACCESS_OP_READ_CHR 2
#define BLE_GATT_SVC_TYPE_PRIMARY 1
#define BLE_GATT_CHR_F_NOTIFY 1
#define BLE_GATT_CHR_F_WRITE 2
#define BLE_GATT_CHR_F_WRITE_ENC 4
#define BLE_GATT_CHR_F_WRITE_AUTHEN 8
#define BLE_GATT_CHR_F_READ 16
#define BLE_GATT_CHR_F_READ_ENC 32
#define BLE_GATT_CHR_F_READ_AUTHEN 64
#define BLE_HS_ADV_F_DISC_GEN 1
#define BLE_HS_ADV_F_BREDR_UNSUP 2
#define BLE_GAP_CONN_MODE_UND 1
#define BLE_GAP_DISC_MODE_GEN 2
#define BLE_GAP_EVENT_CONNECT 1
#define BLE_GAP_EVENT_DISCONNECT 2
#define BLE_GAP_EVENT_ENC_CHANGE 3
#define BLE_GAP_EVENT_SUBSCRIBE 4
#define BLE_GAP_EVENT_MTU 5
#define BLE_GAP_EVENT_REPEAT_PAIRING 6
#define BLE_GAP_EVENT_PASSKEY_ACTION 7
#define BLE_GAP_EVENT_NOTIFY_TX 8
#define BLE_GAP_EVENT_ADV_COMPLETE 9
struct ble_gap_sec_state {unsigned encrypted,authenticated,bonded,key_size;};struct ble_addr {uint8_t val[6],type;};struct ble_gap_conn_desc {uint16_t conn_handle;struct ble_gap_sec_state sec_state;struct ble_addr peer_id_addr,peer_ota_addr;};
struct ble_gap_event {int type;struct {int status;uint16_t conn_handle;}connect;struct {struct ble_gap_conn_desc conn;}disconnect;struct {uint16_t conn_handle,attr_handle;int cur_notify;}subscribe;struct {uint16_t conn_handle,value;}mtu;struct {uint16_t conn_handle;struct {int action;}params;}passkey;};
struct ble_store_key_sec {struct ble_addr peer_addr;};struct ble_store_value_sec{unsigned ltk_present,sc,authenticated,key_size;};union ble_store_value{int dummy;struct ble_store_value_sec sec;};int ble_store_read_our_sec(const struct ble_store_key_sec*,struct ble_store_value_sec*);struct ble_store_status_event{int dummy;};typedef int ble_store_write_fn(int,const union ble_store_value*);
struct ble_hs_cfg_struct {void(*reset_cb)(int);void(*sync_cb)(void);int sm_io_cap,sm_bonding,sm_mitm,sm_sc,sm_our_key_dist,sm_their_key_dist;ble_store_write_fn*store_write_cb;int(*store_status_cb)(struct ble_store_status_event*,void*);};extern struct ble_hs_cfg_struct ble_hs_cfg;
typedef struct {uint8_t type;}ble_uuid_t;typedef struct {ble_uuid_t u;uint8_t value[16];}ble_uuid128_t;
#define BLE_UUID128_INIT(...) {{0},{__VA_ARGS__}}
struct os_mbuf {uint8_t data[512];uint16_t len;};
#define OS_MBUF_PKTLEN(x) ((x)->len)
struct ble_gatt_access_ctxt {int op;struct os_mbuf*om;};
struct ble_gatt_chr_def{const ble_uuid_t*uuid;int(*access_cb)(uint16_t,uint16_t,struct ble_gatt_access_ctxt*,void*);void*arg;int flags;uint16_t*val_handle;unsigned min_key_size;};struct ble_gatt_svc_def{int type;const ble_uuid_t*uuid;struct ble_gatt_chr_def*characteristics;};
struct ble_hs_adv_fields {int flags;ble_uuid128_t*uuids128;int num_uuids128,uuids128_is_complete;};struct ble_gap_adv_params{int conn_mode,disc_mode;};struct ble_sm_io{int action;uint32_t passkey;};
int ble_gap_conn_find(uint16_t,struct ble_gap_conn_desc*);int ble_hs_mbuf_to_flat(struct os_mbuf*,void*,uint16_t,uint16_t*);int os_mbuf_append(struct os_mbuf*,const void*,size_t);int ble_gap_adv_set_fields(const struct ble_hs_adv_fields*);int ble_gap_adv_start(uint8_t,const void*,int,const struct ble_gap_adv_params*,int(*)(struct ble_gap_event*,void*),void*);int ble_gap_adv_stop(void);int ble_gap_adv_active(void);int ble_gap_terminate(uint16_t,int);int ble_sm_inject_io(uint16_t,const struct ble_sm_io*);struct os_mbuf*ble_hs_mbuf_from_flat(const void*,uint16_t);int ble_gatts_notify_custom(uint16_t,uint16_t,struct os_mbuf*);int ble_gap_security_initiate(uint16_t);int ble_hs_util_ensure_addr(int);int ble_hs_id_infer_auto(int,uint8_t*);void ble_svc_gap_init(void);void ble_svc_gatt_init(void);int ble_svc_gap_device_name_set(const char*);int ble_gatts_count_cfg(const struct ble_gatt_svc_def*);int ble_gatts_add_svcs(const struct ble_gatt_svc_def*);void ble_store_config_init(void);
#endif
