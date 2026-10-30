#include "partition_profile_idf.h"
#include "partition_profile.h"
#include "sdkconfig.h"
#ifdef CONFIG_PEN_APP_FLASH8_PROFILE
#include "esp_flash.h"
#include "esp_partition.h"
#include "esp_ota_ops.h"
#include <string.h>
#endif
esp_err_t pen_application_partition_guard(void) {
#ifndef CONFIG_PEN_APP_FLASH8_PROFILE
 return ESP_ERR_NOT_SUPPORTED;
#else
 uint32_t physical=0,logical=0;
 esp_err_t error=esp_flash_get_physical_size(NULL,&physical);
 if(error!=ESP_OK) return error;
 error=esp_flash_get_size(NULL,&logical);
 if(error!=ESP_OK) return error;
 pen_partition_description parts[PEN_PROFILE8_PARTITIONS];
 size_t count=0;
 esp_partition_iterator_t it=esp_partition_find(ESP_PARTITION_TYPE_ANY,ESP_PARTITION_SUBTYPE_ANY,NULL);
 while(it) {
  if(count>=PEN_PROFILE8_PARTITIONS) {esp_partition_iterator_release(it);return ESP_ERR_INVALID_STATE;}
  const esp_partition_t *p=esp_partition_get(it);
  if(!p || p->flash_chip!=esp_flash_default_chip || p->erase_size!=4096) {esp_partition_iterator_release(it);return ESP_ERR_INVALID_STATE;}
  parts[count++]=(pen_partition_description){p->label,p->address,p->size,p->type,p->subtype,p->encrypted,p->readonly};
  it=esp_partition_next(it);
 }
 if(pen_profile8_validate(physical,logical,parts,count)) return ESP_ERR_INVALID_STATE;
 const esp_partition_t *running=esp_ota_get_running_partition();
 if(!running || running->flash_chip!=esp_flash_default_chip || running->readonly || running->encrypted || running->type!=ESP_PARTITION_TYPE_APP || running->size!=0x200000 ||
    !((running->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_0 && running->address==0x20000 && !strcmp(running->label,"ota_0")) ||
      (running->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_1 && running->address==0x220000 && !strcmp(running->label,"ota_1")))) return ESP_ERR_INVALID_STATE;
 return ESP_OK;
#endif
}
