#include "storage_idf.h"
#include "sdkconfig.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned writes,erases;static int init_fail,commit_fail;
static uint8_t flash[4096];static esp_partition_t part={.address=0x200000,.size=4096};
static struct metadata {uint64_t partition,epoch;uint8_t intent;} durable,stage;
const esp_partition_t *esp_partition_find_first(int t,int sub,const char*l){(void)t;(void)sub;return !strcmp(l,"pen_records")?&part:NULL;}
esp_err_t esp_partition_read(const esp_partition_t*p,size_t o,void*b,size_t n){(void)p;assert(o+n<=sizeof flash);memcpy(b,flash+o,n);return ESP_OK;}
esp_err_t esp_partition_write(const esp_partition_t*p,size_t o,const void*b,size_t n){(void)p;const uint8_t*q=b;assert(o+n<=sizeof flash);writes++;for(size_t i=0;i<n;i++){assert((flash[o+i]&q[i])==q[i]);flash[o+i]&=q[i];}return ESP_OK;}
esp_err_t esp_partition_erase_range(const esp_partition_t*p,size_t o,size_t n){(void)p;assert(o==0&&n==4096);erases++;memset(flash,255,sizeof flash);return ESP_OK;}
esp_err_t nvs_flash_init(void){return init_fail?ESP_FAIL:ESP_OK;}
esp_err_t nvs_open(const char*n,int m,nvs_handle_t*h){assert(!strcmp(n,"pen_store"));(void)m;*h=1;stage=durable;return ESP_OK;}
void nvs_close(nvs_handle_t h){(void)h;stage=durable;}
esp_err_t nvs_get_u8(nvs_handle_t h,const char*k,uint8_t*v){(void)h;assert(!strcmp(k,"erase_pending"));*v=stage.intent;return ESP_OK;}
esp_err_t nvs_set_u8(nvs_handle_t h,const char*k,uint8_t v){(void)h;assert(!strcmp(k,"erase_pending"));stage.intent=v;return ESP_OK;}
esp_err_t nvs_get_u64(nvs_handle_t h,const char*k,uint64_t*v){(void)h;*v=!strcmp(k,"partition")?stage.partition:stage.epoch;return *v?ESP_OK:ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_set_u64(nvs_handle_t h,const char*k,uint64_t v){(void)h;if(!strcmp(k,"partition"))stage.partition=v;else stage.epoch=v;return ESP_OK;}
esp_err_t nvs_commit(nvs_handle_t h){(void)h;if(commit_fail)return ESP_FAIL;durable=stage;return ESP_OK;}
static void put(uint8_t*b,uint64_t v,unsigned n){for(unsigned i=0;i<n;i++)b[i]=(uint8_t)(v>>(i*8));}
int main(void){
 memset(flash,255,sizeof flash);pen_storage_idf c;
#ifndef CONFIG_PEN_FLASH_RECORDING
 assert(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_ERR_NOT_SUPPORTED);assert(!writes&&!erases);puts("storage IDF disabled: zero writes PASS");return 0;
#else
 assert(pen_storage_idf_open(&c,0,"pen_records",42)==ESP_ERR_INVALID_ARG);
 assert(pen_storage_idf_open(&c,1,"nvs",42)==ESP_ERR_INVALID_ARG);
 part.encrypted=true;assert(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_ERR_INVALID_STATE);part.encrypted=false;
 init_fail=1;assert(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_FAIL);init_fail=0;assert(!erases);
 assert(!pen_storage_idf_open(&c,1,"pen_records",42));uint64_t epoch=0;commit_fail=1;assert(pen_storage_idf_begin_boot(&c,&epoch)==ESP_FAIL);assert(!c.store.recording&&!durable.epoch);commit_fail=0;pen_storage_idf_close(&c);
 assert(!pen_storage_idf_open(&c,1,"pen_records",42));assert(!pen_storage_idf_begin_boot(&c,&epoch)&&epoch==1);
 pen_sample p={.flags=PEN_GAP,.timestamp_us=10},q;assert(!pen_store_append(&c.store,&p,&q)&&q.session==1&&q.seq==0);
 uint8_t fragments[3][20],record[48],ack[20]={'A','K',1,0};assert(!pen_storage_idf_fragments(&c,fragments));for(unsigned i=0;i<3;i++){assert(fragments[i][0]==0xb1&&fragments[i][1]==i);memcpy(record+16*i,fragments[i]+4,16);}assert(!pen_decode(&q,record));
 put(ack+4,epoch,8);put(ack+12,0,4);put(ack+16,pen_crc32(ack,16),4);
 for(unsigned i=0;i<4;i++){int sec[4]={1,1,1,1};sec[i]=0;assert(pen_storage_idf_ack(&c,ack,20,sec[0],sec[1],sec[2],sec[3])==-3);}
 assert(!pen_storage_idf_ack(&c,ack,20,1,1,1,1));assert(pen_storage_idf_fragments(&c,fragments)==1);
 pen_store_stop(&c.store);commit_fail=1;assert(pen_store_reclaim(&c.store,1)==-1&&!erases);commit_fail=0;pen_storage_idf_close(&c);
 assert(!pen_storage_idf_open(&c,1,"pen_records",42));assert(!pen_store_reclaim(&c.store,1)&&erases==1);assert(!pen_storage_idf_begin_boot(&c,&epoch)&&epoch==2);pen_storage_idf_close(&c);
 puts("storage actual IDF adapter mocked APIs: disabled/security/NVS/epoch/readback/ACK/reclaim PASS");return 0;
#endif
}
