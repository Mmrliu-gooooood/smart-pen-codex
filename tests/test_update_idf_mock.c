/* SDK call-order/fault simulator only. Fake digest/signature routines do NOT
   establish cryptographic correctness or physical power-cut behavior. */
#include "update_idf.h"
#include "nvs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static esp_partition_t run={0x10000,4096},target={0x20000,4096};
static esp_app_desc_t running_desc={.version="1",.project_name="smartpen-p1"},candidate={.version="2",.project_name="smartpen-p1"};
static esp_ota_img_states_t state;
static unsigned begin_calls,abort_calls,end_calls,select_calls,valid_calls,rollback_calls,commit_calls;
static int write_fail,end_fail,digest_bad,commit_fail,alias_target,different_boot;
static uint32_t floor_value;
const esp_app_desc_t *esp_app_get_description(void){return &running_desc;}
const esp_partition_t *esp_ota_get_running_partition(void){return &run;}
const esp_partition_t *esp_ota_get_boot_partition(void){return different_boot?&target:&run;}
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *p){(void)p;return alias_target?&run:&target;}
esp_err_t esp_ota_get_state_partition(const esp_partition_t *p,esp_ota_img_states_t *s){(void)p;*s=state;return ESP_OK;}
esp_err_t esp_ota_begin(const esp_partition_t *p,size_t n,esp_ota_handle_t *h){assert(p==&target&&n==100);begin_calls++;*h=1;return ESP_OK;}
esp_err_t esp_ota_write(esp_ota_handle_t h,const void *p,size_t n){assert(h==1&&p&&n);return write_fail?ESP_FAIL:ESP_OK;}
esp_err_t esp_ota_end(esp_ota_handle_t h){assert(h==1);end_calls++;return end_fail?ESP_ERR_OTA_VALIDATE_FAILED:ESP_OK;}
esp_err_t esp_ota_abort(esp_ota_handle_t h){assert(h==1);abort_calls++;return ESP_OK;}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *p){assert(p==&target&&end_calls==1);select_calls++;return ESP_OK;}
esp_err_t esp_ota_get_partition_description(const esp_partition_t *p,esp_app_desc_t *d){assert(p==&target);*d=candidate;return ESP_OK;}
esp_err_t esp_ota_mark_app_valid_cancel_rollback(void){assert(commit_calls==1&&!commit_fail);valid_calls++;return ESP_OK;}
esp_err_t esp_ota_mark_app_invalid_rollback_and_reboot(void){rollback_calls++;return ESP_FAIL; /* real device resets on success */}
esp_err_t nvs_open(const char *n,int mode,nvs_handle_t *h){assert(!strcmp(n,"pen_update"));(void)mode;*h=1;return ESP_OK;}
esp_err_t nvs_get_u32(nvs_handle_t h,const char*k,uint32_t*v){assert(h==1&&!strcmp(k,"floor"));*v=floor_value;return ESP_OK;}
esp_err_t nvs_set_u32(nvs_handle_t h,const char*k,uint32_t v){assert(h==1&&!strcmp(k,"floor"));floor_value=v;return ESP_OK;}
esp_err_t nvs_commit(nvs_handle_t h){assert(h==1);commit_calls++;return commit_fail?ESP_FAIL:ESP_OK;}
void nvs_close(nvs_handle_t h){assert(h==1);}
void mbedtls_sha256_init(mbedtls_sha256_context*c){c->n=0;}
void mbedtls_sha256_free(mbedtls_sha256_context*c){(void)c;}
int mbedtls_sha256_starts(mbedtls_sha256_context*c,int is224){(void)c;assert(!is224);return 0;}
int mbedtls_sha256_update(mbedtls_sha256_context*c,const unsigned char*d,size_t n){assert(d);c->n+=(unsigned)n;return 0;}
int mbedtls_sha256_finish(mbedtls_sha256_context*c,unsigned char*d){assert(c->n==100);memset(d,digest_bad?1:0,32);return 0;}
static pen_update_safety safe={true,true,true,true,true};
static pen_update_manifest manifest={100,2,"smartpen-p1","smartpen-p1",{0}};
static unsigned char bytes[100];
static void reset(void){state=ESP_OTA_IMG_VALID;begin_calls=abort_calls=end_calls=select_calls=valid_calls=rollback_calls=commit_calls=0;write_fail=end_fail=digest_bad=commit_fail=alias_target=different_boot=0;floor_value=1;candidate=(esp_app_desc_t){.version="2",.project_name="smartpen-p1"};strcpy(running_desc.version,"1");}
int main(void){
 reset();pen_update_idf u={0};assert(!pen_update_idf_begin(&u,&manifest,&safe));assert(!pen_update_idf_write(&u,0,bytes,40,&safe));assert(!pen_update_idf_write(&u,40,bytes+40,60,&safe));assert(!pen_update_idf_finish(&u,&safe));assert(select_calls==1&&!valid_calls&&!rollback_calls);
 for(unsigned i=0;i<3;i++){reset();u=(pen_update_idf){0};if(i==0)alias_target=1;if(i==1)different_boot=1;if(i==2)state=ESP_OTA_IMG_PENDING_VERIFY;assert(pen_update_idf_begin(&u,&manifest,&safe));assert(!begin_calls);}
 for(unsigned i=0;i<4;i++){reset();u=(pen_update_idf){0};assert(!pen_update_idf_begin(&u,&manifest,&safe));assert(!pen_update_idf_write(&u,0,bytes,100,&safe));if(i==0)digest_bad=1;if(i==1)end_fail=1;if(i==2)candidate.project_name[0]='x';if(i==3)candidate.version[0]='3';assert(pen_update_idf_finish(&u,&safe));assert(!select_calls);}
 reset();u=(pen_update_idf){0};assert(!pen_update_idf_begin(&u,&manifest,&safe));write_fail=1;assert(pen_update_idf_write(&u,0,bytes,100,&safe));assert(abort_calls==1&&!select_calls);assert(pen_update_idf_finish(&u,&safe));
 reset();u=(pen_update_idf){0};assert(!pen_update_idf_begin(&u,&manifest,&safe));assert(!pen_update_idf_write(&u,0,bytes,50,&safe));assert(pen_update_idf_finish(&u,&safe));assert(!end_calls&&!select_calls&&abort_calls==1);
 for(unsigned cut=0;cut<100;cut++){reset();u=(pen_update_idf){0};assert(!pen_update_idf_begin(&u,&manifest,&safe));if(cut)assert(!pen_update_idf_write(&u,0,bytes,cut,&safe));pen_update_idf_abort(&u);assert(!select_calls&&!valid_calls&&abort_calls==1);}
 reset();state=ESP_OTA_IMG_PENDING_VERIFY;strcpy(running_desc.version,"2");assert(pen_update_idf_boot_result(15,false,false,&safe));assert(!valid_calls&&!commit_calls);assert(!pen_update_idf_boot_result(31,false,false,&safe));assert(valid_calls==1&&floor_value==2);
 reset();state=ESP_OTA_IMG_PENDING_VERIFY;commit_fail=1;assert(pen_update_idf_boot_result(31,false,false,&safe));assert(!valid_calls);
 reset();state=ESP_OTA_IMG_PENDING_VERIFY;assert(pen_update_idf_boot_result(0,true,false,&safe));assert(!rollback_calls);assert(pen_update_idf_boot_result(0,true,true,&safe));assert(rollback_calls==1&&!valid_calls);
 puts("SDK mock: inactive slot, digest/signature/descriptor rejection, truncation, write fault, durable floor before health commit, explicit rollback PASS");return 0;
}
