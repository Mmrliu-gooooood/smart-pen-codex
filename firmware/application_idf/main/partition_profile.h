#ifndef PEN_PARTITION_PROFILE_H
#define PEN_PARTITION_PROFILE_H
#include <stddef.h>
#include <stdint.h>
#define PEN_PROFILE8_FLASH_BYTES UINT32_C(0x800000)
#define PEN_PROFILE8_RECORD_BYTES UINT32_C(0x3e0000)
#define PEN_PROFILE8_RECORD_OFFSET UINT32_C(0x420000)
#define PEN_PROFILE8_PARTITIONS 6u
typedef struct {
 const char *label;
 uint32_t address, size;
 uint8_t type, subtype, encrypted, readonly;
} pen_partition_description;
/* Pure, read-only validator. Both physical JEDEC-detected and image-header
 * logical size must exactly match this deliberately strict 8 MiB profile.
 * A 16 MiB DevKit is NOT silently accepted as the 8 MiB PICO configuration.
 * Returns 0 only for the complete exact table; no mutation or formatting. */
int pen_profile8_validate(uint32_t physical_bytes, uint32_t logical_bytes,
 const pen_partition_description *parts, size_t count);
#endif
