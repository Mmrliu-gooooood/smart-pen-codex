#ifndef PEN_UPDATE_IDF_H
#define PEN_UPDATE_IDF_H
#include "update_policy.h"
#include "esp_err.h"
#include "esp_ota_ops.h"
#include "mbedtls/sha256.h"
typedef struct {
 pen_update_transaction transaction;
 pen_update_manifest manifest;
 esp_ota_handle_t handle;
 const esp_partition_t *target;
 mbedtls_sha256_context digest;
 bool open, digest_open;
} pen_update_idf;
/* Zero-init once; serialize all calls in one application task. Never called by ISR. */
esp_err_t pen_update_idf_begin(pen_update_idf *u,const pen_update_manifest *m,const pen_update_safety *s);
esp_err_t pen_update_idf_write(pen_update_idf *u,uint32_t offset,const void *data,size_t n,const pen_update_safety *s);
/* Selects verified inactive app for NEXT boot; deliberately does not reboot. */
esp_err_t pen_update_idf_finish(pen_update_idf *u,const pen_update_safety *s);
void pen_update_idf_abort(pen_update_idf *u);
/* pending image: complete measured health -> valid. Explicit failure -> optional
   rollback reboot only with safe power/storage/contact gates. Incomplete health
   returns INVALID_STATE; never marks valid merely because a timer elapsed. */
esp_err_t pen_update_idf_boot_result(uint32_t passed,bool diagnostics_failed,bool allow_reboot,const pen_update_safety *s);
#endif
