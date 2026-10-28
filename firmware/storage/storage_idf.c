#include "storage_idf.h"
#include "sdkconfig.h"
#include "nvs_flash.h"
#include <string.h>
static int bounds(pen_storage_idf*c,size_t o,size_t n){return c->enabled&&c->partition&&o<=c->partition->size&&n<=c->partition->size-o;}
static int read_part(void*ctx,size_t o,uint8_t*b,size_t n){pen_storage_idf*c=ctx;return bounds(c,o,n)&&esp_partition_read(c->partition,o,b,n)==ESP_OK?0:-1;}
static int write_part(void*ctx,size_t o,const uint8_t*b,size_t n){
 pen_storage_idf*c=ctx;uint8_t old[64],check[64];if(!bounds(c,o,n)||n>sizeof old||read_part(c,o,old,n))return -1;
 for(size_t i=0;i<n;i++)if((old[i]&b[i])!=b[i])return -1;
 if(esp_partition_write(c->partition,o,b,n)!=ESP_OK||read_part(c,o,check,n)||memcmp(check,b,n))return -1;
 return 0;
}
/* esp_partition_write is synchronous; readback above detects write errors.
   This cannot guarantee sufficient supply hold-up: physical cuts remain tests. */
static int sync_part(void*ctx){return ((pen_storage_idf*)ctx)->enabled?0:-1;}
static int get_intent(void*ctx,int*v){pen_storage_idf*c=ctx;uint8_t value=0;esp_err_t e=nvs_get_u8(c->nvs,"erase_pending",&value);if(e!=ESP_OK&&e!=ESP_ERR_NVS_NOT_FOUND)return -1;if(value>1)return -1;*v=value;return 0;}
static int set_intent(void*ctx,int v){pen_storage_idf*c=ctx;return nvs_set_u8(c->nvs,"erase_pending",(uint8_t)v)==ESP_OK&&nvs_commit(c->nvs)==ESP_OK?0:-1;}
static int erase_part(void*ctx){pen_storage_idf*c=ctx;return c->enabled&&esp_partition_erase_range(c->partition,0,c->partition->size)==ESP_OK?0:-1;}
esp_err_t pen_storage_idf_open(pen_storage_idf*c,int enabled,const char*label,uint32_t device){
 if(!c)return ESP_ERR_INVALID_ARG;
 memset(c,0,sizeof(*c));
 int configured=0;
#ifdef CONFIG_PEN_FLASH_RECORDING
 configured=1;
#endif
 if(!configured)return ESP_ERR_NOT_SUPPORTED;
 if(!enabled||!label||strcmp(label,"pen_records"))return ESP_ERR_INVALID_ARG;
 c->partition=esp_partition_find_first(ESP_PARTITION_TYPE_DATA,ESP_PARTITION_SUBTYPE_ANY,label);
 if(!c->partition||c->partition->encrypted||c->partition->size<4096||c->partition->size%4096||c->partition->address%4096)return ESP_ERR_INVALID_STATE;
 esp_err_t error=nvs_flash_init();if(error!=ESP_OK)return error; /* never autoerase bonds/epochs */
 error=nvs_open("pen_store",NVS_READWRITE,&c->nvs);if(error!=ESP_OK)return error;c->nvs_opened=1;c->enabled=1;
 /* Bind recovery metadata to this exact partition to avoid stale erase intents. */
 uint64_t binding=((uint64_t)c->partition->address<<32)|c->partition->size,old=0;
 error=nvs_get_u64(c->nvs,"partition",&old);
 if(error==ESP_ERR_NVS_NOT_FOUND){error=nvs_set_u64(c->nvs,"partition",binding);if(error==ESP_OK)error=nvs_commit(c->nvs);}
 else if(error==ESP_OK&&old!=binding)error=ESP_ERR_INVALID_STATE;
 if(error!=ESP_OK){pen_storage_idf_close(c);return error;}
 c->store.log=(pen_log){.ctx=c,.read=read_part,.program=write_part,.sync=sync_part,.slots=c->partition->size/64};
 c->store.meta_ctx=c;c->store.get_erase_intent=get_intent;c->store.set_erase_intent=set_intent;c->store.erase_all=erase_part;
 if(pen_store_open(&c->store,device)){pen_storage_idf_close(c);return ESP_FAIL;}return ESP_OK;
}
esp_err_t pen_storage_idf_begin_boot(pen_storage_idf*c,uint64_t*epoch){
 if(!c||!epoch)return ESP_ERR_INVALID_ARG;
 if(!c->enabled||c->store.recording)return ESP_ERR_INVALID_STATE;
 uint64_t value=0;esp_err_t error=nvs_get_u64(c->nvs,"boot_epoch",&value);
 if(error!=ESP_OK&&error!=ESP_ERR_NVS_NOT_FOUND)return error;
 if(value==UINT64_MAX)return ESP_ERR_INVALID_STATE;
 value++;
 error=nvs_set_u64(c->nvs,"boot_epoch",value);if(error==ESP_OK)error=nvs_commit(c->nvs);
 if(error!=ESP_OK)return error;
 if(pen_store_begin(&c->store,value))return ESP_ERR_INVALID_STATE;
 *epoch=value;return ESP_OK;
}
void pen_storage_idf_close(pen_storage_idf*c){if(!c)return;c->enabled=0;if(c->nvs_opened)nvs_close(c->nvs);c->nvs_opened=0;c->store.log.faulted=1;c->store.recording=0;}
static uint64_t get(const uint8_t*p,unsigned n){uint64_t v=0;for(unsigned i=0;i<n;i++)v|=(uint64_t)p[i]<<(i*8);return v;}
int pen_storage_idf_ack(pen_storage_idf*c,const uint8_t*b,size_t n,int encrypted,int authenticated,int bonded,int approved){
 if(!c||!b||!c->enabled||!encrypted||!authenticated||!bonded||!approved||n!=20)return -3;
 if(b[0]!='A'||b[1]!='K'||b[2]!=1||b[3]||get(b+16,4)!=pen_crc32(b,16))return -3;
 return pen_store_ack(&c->store,get(b+4,8),(uint32_t)get(b+12,4),1);
}
int pen_storage_idf_fragments(pen_storage_idf*c,uint8_t out[3][20]){
 if(!c||!out||!c->enabled)return -1;
 pen_sample p;int result=pen_store_offer(&c->store,&p);if(result)return result;
 uint8_t b[48];if(pen_encode(b,&p))return -1;
 for(unsigned i=0;i<3;i++){out[i][0]=0xb1;out[i][1]=(uint8_t)i;out[i][2]=(uint8_t)p.seq;out[i][3]=(uint8_t)(p.seq>>8);memcpy(out[i]+4,b+i*16,16);}return 0;
}
