#pragma once
#include <stdint.h>
typedef struct {unsigned size,length,sosf,eof,owner; uint8_t *buf; uint32_t empty;}lldesc_t;
