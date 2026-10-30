#ifndef PEN_BLE_ACTOR_H
#define PEN_BLE_ACTOR_H
#include "pen_ble_core.h"
/* Trusted, local transport boundary, never serialized to BLE. */
typedef struct {uintptr_t app;uint64_t nonce,session,epoch;uint32_t seq;} pen_ble_ticket;
typedef struct {pen_ble_ticket ticket;uint8_t authorized;} pen_ble_grant;
typedef struct {
 void *ctx;
 int (*security)(void*,pen_link_security*);
 pen_packet_sender send;
 int (*authorize)(void*,const pen_ble_ticket*,pen_ble_grant*);
} pen_ble_backend;
typedef struct {pen_app *app;pen_ble_backend backend;uint64_t nonce;uint8_t faulted,busy;} pen_ble_actor;
/* Must be initialized once for an exclusive application lifetime. No copies,
 * reentrance, concurrent step/maintenance/sleep, or externally provided grant. */
int pen_ble_actor_init(pen_ble_actor*,pen_app*,const pen_ble_backend*);
/* Caller task performs Flash. Host only authorizes and submits notifications.
 *0 successful progress/idle,1 backpressure,-1 terminal,-3 unauthorized. */
int pen_ble_actor_turn(pen_ble_actor*);
/* Host owner only: exact authenticated receipt + present offered ticket. */
int pen_ble_core_authorize(pen_ble_core*,const pen_ble_ticket*,pen_ble_grant*);
#endif
