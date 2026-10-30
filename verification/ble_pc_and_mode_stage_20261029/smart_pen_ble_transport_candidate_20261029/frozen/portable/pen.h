#ifndef SMART_PEN_H
#define SMART_PEN_H
#include <stddef.h>
#include <stdint.h>
#define PEN_PACKET_SIZE 48u
#define PEN_SLOT_SIZE 64u
#define PEN_CONTACT 1u
#define PEN_VALID 2u
#define PEN_GAP 4u
/* Coordinates are calibrated physical tip micrometres, never image origins. */
typedef struct {
 uint32_t device, seq, page;
 uint64_t session, timestamp_us;
 int32_t x_um, y_um;
 uint16_t confidence;
 uint8_t flags;
} pen_sample;
uint32_t pen_crc32(const uint8_t *p, size_t n);
int pen_encode(uint8_t out[PEN_PACKET_SIZE], const pen_sample *p);
int pen_decode(pen_sample *p, const uint8_t in[PEN_PACKET_SIZE]);
/* Fail closed: raw contact must remain stable for debounce_us. Invalid optical
   observations immediately clear VALID, and force a new segment on recovery. */
typedef struct { uint64_t changed, last; uint8_t raw, stable, started, lost; } pen_gate;
void pen_gate_apply(pen_gate *g, pen_sample *p, uint8_t raw_contact,
                    uint8_t calibrated, uint16_t threshold, uint32_t debounce_us);
/* NOR contract: erased bytes FF; program only 1->0; sync returns only once
   bytes are persistent. Slots are never erased/overwritten by this module. */
typedef struct {
 void *ctx;
 int (*read)(void *, size_t, uint8_t *, size_t);
 int (*program)(void *, size_t, const uint8_t *, size_t);
 int (*sync)(void *);
 size_t slots, next;
 uint8_t faulted; /* latched until open successfully syncs and rescans */
} pen_log;
int pen_log_open(pen_log *log);
/* 0 durable, -1 storage failure/invalid, -2 full. Failed writes consume a slot. */
int pen_log_append(pen_log *log, const pen_sample *sample);
/* 0 valid, 1 erased/torn/corrupt, -1 I/O. Caller must preserve seq gaps. */
int pen_log_read(pen_log *log, size_t slot, pen_sample *sample);
#endif
