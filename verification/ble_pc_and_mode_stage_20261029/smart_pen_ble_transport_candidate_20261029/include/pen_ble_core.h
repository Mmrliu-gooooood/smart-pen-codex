#ifndef PEN_BLE_CORE_H
#define PEN_BLE_CORE_H
#include "pipeline.h"
#define PEN_BLE_ACK_CAPACITY 8u
#define PEN_BLE_FRAGMENT_SIZE 20u
#define PEN_BLE_RETRY_US 250000u
/* Single serialized owner. This is not a mutex and is never ISR safe. */
typedef struct {
 uint64_t session,received_us; uint32_t seq; pen_link_security receipt;
} pen_ble_ack;
typedef struct {
 pen_link_security security;
 pen_ble_ack acks[PEN_BLE_ACK_CAPACITY];
 uint8_t packet[PEN_PACKET_SIZE];
 uint64_t last_attempt_us,offered_session; uint32_t offered_seq;
 uint16_t mtu; unsigned ack_count;
 uint8_t subscribed,quiesced,faulted,offered,attempted;
} pen_ble_core;
typedef int (*pen_ble_notify)(void*,const uint8_t*,size_t,uint64_t);
void pen_ble_core_init(pen_ble_core*);
/* Trusted stack facts only, including new durable epoch per connection. */
void pen_ble_core_link(pen_ble_core*,const pen_link_security*,unsigned key_size);
void pen_ble_core_mtu(pen_ble_core*,uint16_t);
void pen_ble_core_subscribe(pen_ble_core*,int);
void pen_ble_core_quiesce(pen_ble_core*,int);
int pen_ble_core_ready(const pen_ble_core*);
/*0 all three notifications accepted (NOT peer delivery);1 backpressure;-1 fault.*/
int pen_ble_core_send(pen_ble_core*,const uint8_t*,size_t,uint64_t,uint64_t,pen_ble_notify,void*);
/* Parse only ACK identity. Security and monotonic receive time are not payload. */
int pen_ble_core_receive(pen_ble_core*,const uint8_t*,size_t,uint64_t);
int pen_ble_core_pop(pen_ble_core*,pen_ble_ack*);
void pen_ble_core_committed(pen_ble_core*,const pen_ble_ack*);
#endif
