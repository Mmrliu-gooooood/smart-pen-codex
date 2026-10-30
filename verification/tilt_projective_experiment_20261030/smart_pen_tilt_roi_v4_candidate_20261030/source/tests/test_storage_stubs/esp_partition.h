#ifndef MOCK_PARTITION
#define MOCK_PARTITION
#include "esp_err.h"
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
typedef struct {uint32_t address,size;bool encrypted;} esp_partition_t;
#define ESP_PARTITION_TYPE_DATA 1
#define ESP_PARTITION_SUBTYPE_ANY 0xff
const esp_partition_t *esp_partition_find_first(int,int,const char*);
esp_err_t esp_partition_read(const esp_partition_t*,size_t,void*,size_t);
esp_err_t esp_partition_write(const esp_partition_t*,size_t,const void*,size_t);
esp_err_t esp_partition_erase_range(const esp_partition_t*,size_t,size_t);
#endif
