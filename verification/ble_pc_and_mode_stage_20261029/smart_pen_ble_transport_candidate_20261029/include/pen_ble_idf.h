#ifndef PEN_BLE_IDF_H
#define PEN_BLE_IDF_H
#include "pen_ble_actor.h"
#include "esp_err.h"
typedef struct {uint64_t epoch;uint16_t handle;uint8_t address[6],address_type;pen_link_security security;} pen_ble_peer;
typedef struct {
 void *ctx;
 /* REQUIRED reviewed LOCAL USB display. Called on host task: no blocking,
  * no BLE RPC, no logging of passkey to cloud, no fixed passkey. 0 shown. */
 int (*show_passkey)(void*,const pen_ble_peer*,uint32_t);
} pen_ble_local_io;
/* Never called by checked-in app_main. Only development USB/display policy;
 * headless production pairing is NOT implemented. No NVS erase fallback. */
esp_err_t pen_ble_dev_start(const pen_ble_local_io*,int locally_authorized);
/* Local 60s, one-connection pairing window. No phone address required. */
int pen_ble_dev_advertise(void);
int pen_ble_dev_peer(pen_ble_peer*);
/* Only a trusted LOCAL operator action after inspecting this exact epoch.
 * Never expose through GATT or authorize from a remote payload. */
int pen_ble_dev_approve(uint64_t epoch);
int pen_ble_quiesce(void); /*0 disconnected+adv stopped;1 waiting;-1 fault*/
int pen_ble_resume(void);
const pen_ble_backend *pen_ble_transport_backend(void);
#endif
