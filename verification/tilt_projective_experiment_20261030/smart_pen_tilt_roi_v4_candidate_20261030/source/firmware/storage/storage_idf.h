#ifndef PEN_STORAGE_IDF_H
#define PEN_STORAGE_IDF_H
#include "store.h"
#include "esp_err.h"
#include "esp_partition.h"
#include "nvs.h"
typedef struct {pen_store store;const esp_partition_t *partition;nvs_handle_t nvs;int enabled,nvs_opened;} pen_storage_idf;
/* Requires BOTH CONFIG_PEN_FLASH_RECORDING=y and explicit_enabled=1.
   Never auto-erases NVS or an unknown data partition. Caller serializes all APIs. */
esp_err_t pen_storage_idf_open(pen_storage_idf *ctx,int explicit_enabled,const char *label,uint32_t device);
/* Durably allocates a unique monotonic boot epoch before accepting records. */
esp_err_t pen_storage_idf_begin_boot(pen_storage_idf *ctx,uint64_t *epoch);
void pen_storage_idf_close(pen_storage_idf *ctx);
/* BLE adapter passes actual connection security/approved identity, not user input. */
int pen_storage_idf_ack(pen_storage_idf *ctx,const uint8_t *ack,size_t length,
 int encrypted,int authenticated,int bonded,int approved_peer);
/* 0 immutable current record ->3 fragments;1 empty;-1 failure. */
int pen_storage_idf_fragments(pen_storage_idf *ctx,uint8_t out[3][20]);
#endif
