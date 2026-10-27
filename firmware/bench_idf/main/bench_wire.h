#ifndef PEN_BENCH_WIRE_H
#define PEN_BENCH_WIRE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Security booleans MUST come from live stack state, not client payload. */
int bench_ack(const uint8_t *bytes,size_t length,bool approved,bool encrypted,
              bool authenticated,bool bonded,bool have_sent,uint64_t session,uint32_t seq);
int bench_fragment(const uint8_t packet[48],uint32_t seq,unsigned index,uint8_t out[20]);
#endif
