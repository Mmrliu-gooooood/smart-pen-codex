#include "update_idf.h"
#include "sdkconfig.h"
#include "esp_app_desc.h"
#include "nvs.h"
#include <string.h>
static bool configuration_ok(void){
#if defined(CONFIG_PEN_OTA_ALLOW_INSTALL) && CONFIG_PEN_OTA_ALLOW_INSTALL && defined(CONFIG_SECURE_SIGNED_ON_UPDATE) && CONFIG_SECURE_SIGNED_ON_UPDATE && defined(CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE) && CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE && !defined(CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK)
 const esp_app_desc_t *d=esp_app_get_description();uint32_t version;
 return !strcmp(CONFIG_PEN_OTA_PROJECT,CONFIG_PEN_OTA_HARDWARE)&&strcmp(CONFIG_PEN_OTA_PROJECT,"smartpen-unqualified")&&strcmp(CONFIG_PEN_OTA_HARDWARE,"UNQUALIFIED")&&
  memchr(d->project_name,0,sizeof(d->project_name))&&!strcmp(d->project_name,CONFIG_PEN_OTA_PROJECT)&&!pen_update_version_parse(d->version,&version);
#else
 return false;
#endif
}
static esp_err_t floor_read(uint32_t *v){
 uint32_t current;if(pen_update_version_parse(esp_app_get_description()->version,&current))return ESP_ERR_INVALID_VERSION;
 nvs_handle_t h;esp_err_t e=nvs_open("pen_update",NVS_READONLY,&h);
 if(e==ESP_ERR_NVS_NOT_FOUND){*v=current;return ESP_OK;}
 if(e!=ESP_OK)return e;
 e=nvs_get_u32(h,"floor",v);nvs_close(h);
 if(e==ESP_ERR_NVS_NOT_FOUND){*v=current;return ESP_OK;}return e;
}
static esp_err_t floor_commit(uint32_t v){
 uint32_t old;esp_err_t e=floor_read(&old);if(e!=ESP_OK)return e;
 if(v<old)return ESP_ERR_INVALID_VERSION;
 nvs_handle_t h;e=nvs_open("pen_update",NVS_READWRITE,&h);if(e!=ESP_OK)return e;
 e=nvs_set_u32(h,"floor",v);if(e==ESP_OK)e=nvs_commit(h);nvs_close(h);return e;
}
void pen_update_idf_abort(pen_update_idf *u){
 if(!u)return;
 if(u->open){esp_ota_abort(u->handle);u->open=false;}
 if(u->digest_open){mbedtls_sha256_free(&u->digest);u->digest_open=false;}
 u->transaction.state=PEN_UPDATE_FAILED;
}
esp_err_t pen_update_idf_begin(pen_update_idf *u,const pen_update_manifest *m,const pen_update_safety *s){
 if(!u||!m)return ESP_ERR_INVALID_ARG;
 if(!configuration_ok()||u->open||u->digest_open||u->transaction.state!=PEN_UPDATE_IDLE)return ESP_ERR_INVALID_STATE;
 const esp_partition_t *running=esp_ota_get_running_partition(),*boot=esp_ota_get_boot_partition();
 if(!running||!boot||running->address!=boot->address)return ESP_ERR_INVALID_STATE;
 const esp_partition_t *target=esp_ota_get_next_update_partition(NULL);
 if(!target||target->address==running->address||target->address==boot->address)return ESP_ERR_NOT_FOUND;
 esp_ota_img_states_t state;esp_err_t e=esp_ota_get_state_partition(running,&state);
 if(e!=ESP_OK||state!=ESP_OTA_IMG_VALID)return ESP_ERR_INVALID_STATE;
 uint32_t floor;e=floor_read(&floor);if(e!=ESP_OK)return e;
 uint32_t current;if(pen_update_version_parse(esp_app_get_description()->version,&current))return ESP_ERR_INVALID_VERSION;
 pen_update_policy p={.minimum_version=floor,.running_version=current,
  .partition_bytes=target->size,.project=CONFIG_PEN_OTA_PROJECT,.hardware=CONFIG_PEN_OTA_HARDWARE,
  .enabled=true,.signatures_enforced=true,.rollback_enabled=true,.pending_verify=false};
 if(pen_update_start(&u->transaction,&p,m,s))return ESP_ERR_INVALID_ARG;
 u->manifest=*m;u->target=target;
 mbedtls_sha256_init(&u->digest);u->digest_open=true;
 if(mbedtls_sha256_starts(&u->digest,0)){pen_update_idf_abort(u);return ESP_FAIL;}
 e=esp_ota_begin(target,m->bytes,&u->handle);if(e!=ESP_OK){pen_update_idf_abort(u);return e;}
 u->open=true;return ESP_OK;
}
esp_err_t pen_update_idf_write(pen_update_idf *u,uint32_t offset,const void *data,size_t n,const pen_update_safety *s){
 if(!u||!data)return ESP_ERR_INVALID_ARG;
 if(!u->open)return ESP_ERR_INVALID_STATE;
 if(pen_update_chunk(&u->transaction,offset,n,s)){pen_update_idf_abort(u);return ESP_ERR_INVALID_ARG;}
 esp_err_t e=esp_ota_write(u->handle,data,n);
 if(e!=ESP_OK||mbedtls_sha256_update(&u->digest,data,n)){pen_update_idf_abort(u);return e==ESP_OK?ESP_FAIL:e;}
 return ESP_OK;
}
esp_err_t pen_update_idf_finish(pen_update_idf *u,const pen_update_safety *s){
 if(!u||!u->open)return ESP_ERR_INVALID_STATE;
 uint8_t digest[32];
 if(!pen_update_safe(s)||u->transaction.received!=u->manifest.bytes||mbedtls_sha256_finish(&u->digest,digest)||memcmp(digest,u->manifest.sha256,32)){
  pen_update_idf_abort(u);return ESP_ERR_OTA_VALIDATE_FAILED;
 }
 mbedtls_sha256_free(&u->digest);u->digest_open=false;
 /* With required SIGNED_ON_UPDATE, esp_ota_end performs vendor signature check. */
 esp_err_t e=esp_ota_end(u->handle);u->open=false;
 if(e!=ESP_OK){u->transaction.state=PEN_UPDATE_FAILED;return e;}
 esp_app_desc_t desc;uint32_t candidate_version;e=esp_ota_get_partition_description(u->target,&desc);
 bool descriptor=e==ESP_OK&&memchr(desc.project_name,0,sizeof(desc.project_name))&&
  !strcmp(desc.project_name,CONFIG_PEN_OTA_PROJECT)&&!pen_update_version_parse(desc.version,&candidate_version)&&candidate_version==u->manifest.version;
 if(pen_update_finish(&u->transaction,true,descriptor,s))return ESP_ERR_OTA_VALIDATE_FAILED;
 e=esp_ota_set_boot_partition(u->target);
 if(e!=ESP_OK)u->transaction.state=PEN_UPDATE_FAILED;
 return e;
}
esp_err_t pen_update_idf_boot_result(uint32_t passed,bool failed,bool allow_reboot,const pen_update_safety *s){
 if(!configuration_ok())return ESP_ERR_INVALID_STATE;
 const esp_partition_t *running=esp_ota_get_running_partition();if(!running)return ESP_ERR_NOT_FOUND;
 esp_ota_img_states_t state;esp_err_t e=esp_ota_get_state_partition(running,&state);
 if(e!=ESP_OK)return e;
 if(state!=ESP_OTA_IMG_PENDING_VERIFY)return ESP_ERR_INVALID_STATE;
 if(failed){
  if(!allow_reboot||!pen_update_safe(s))return ESP_ERR_INVALID_STATE;
  return esp_ota_mark_app_invalid_rollback_and_reboot();
 }
 if(!pen_update_boot_healthy(passed,s))return ESP_ERR_INVALID_STATE;
 /* Persistent software floor first. A reset before mark-valid still rolls back
    to known-good boot slot; floor gates future installations, not boot fallback. */
 uint32_t current;if(pen_update_version_parse(esp_app_get_description()->version,&current))return ESP_ERR_INVALID_VERSION;
 e=floor_commit(current);if(e!=ESP_OK)return e;
 return esp_ota_mark_app_valid_cancel_rollback();
}
