#include "partition_profile.h"
#include "partition_profile_idf.h"
#include "esp_flash.h"
#include "esp_partition.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAILED line %d: %s\n",__LINE__,#x);exit(1);} }while(0)
static const pen_partition_description valid[6]={
 {"nvs",0x9000,0x6000,1,2,0,0},{"otadata",0xf000,0x2000,1,0,0,0},
 {"phy_init",0x11000,0x1000,1,1,0,0},{"ota_0",0x20000,0x200000,0,0x10,0,0},
 {"ota_1",0x220000,0x200000,0,0x11,0,0},{"pen_records",0x420000,0x3e0000,1,0x40,0,0}
};
static esp_flash_t main_chip={1},other_chip={2};
esp_flash_t *esp_flash_default_chip=&main_chip;
static esp_partition_t table[7],current;
static uint32_t physical,logical;
static int physical_error,logical_error,calls,releases,count,null_part,null_running;
struct mock_iterator{int index;};static struct mock_iterator iterator;
esp_err_t esp_flash_get_physical_size(esp_flash_t*p,uint32_t*out){CHECK(p==NULL);calls++;*out=physical;return physical_error;}
esp_err_t esp_flash_get_size(esp_flash_t*p,uint32_t*out){CHECK(p==NULL);calls++;*out=logical;return logical_error;}
esp_partition_iterator_t esp_partition_find(uint8_t t,uint8_t s,const char*n){CHECK(t==255&&s==255&&n==NULL);calls++;iterator.index=0;return count?&iterator:NULL;}
const esp_partition_t *esp_partition_get(esp_partition_iterator_t it){CHECK(it==&iterator);calls++;return null_part?NULL:&table[it->index];}
esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t it){CHECK(it==&iterator);calls++;return ++it->index<count?it:NULL;}
void esp_partition_iterator_release(esp_partition_iterator_t it){CHECK(it==&iterator);calls++;releases++;}
const esp_partition_t *esp_ota_get_running_partition(void){calls++;return null_running?NULL:&current;}
static void reset(void){physical=logical=0x800000;physical_error=logical_error=calls=releases=null_part=null_running=0;count=6;
 memset(table,0,sizeof table);
 for(int i=0;i<6;i++){table[i].flash_chip=&main_chip;table[i].type=valid[i].type;table[i].subtype=valid[i].subtype;table[i].address=valid[i].address;table[i].size=valid[i].size;table[i].erase_size=4096;strcpy(table[i].label,valid[i].label);}
 current=table[3];
}
int main(void){
 pen_partition_description a[7]; memcpy(a,valid,sizeof valid);
 CHECK(pen_profile8_validate(0x800000,0x800000,a,6)==0);
 for(int i=0;i<3;i++){pen_partition_description p=a[i];a[i]=a[5-i];a[5-i]=p;}
 CHECK(pen_profile8_validate(0x800000,0x800000,a,6)==0);memcpy(a,valid,sizeof valid);
 CHECK(pen_profile8_validate(0,0x800000,a,6)!=0);CHECK(pen_profile8_validate(0x1000000,0x800000,a,6)!=0);
 CHECK(pen_profile8_validate(0x400000,0x800000,a,6)!=0);CHECK(pen_profile8_validate(0x800000,0x1000000,a,6)!=0);
 CHECK(pen_profile8_validate(0x800000,0x800000,NULL,6)!=0);CHECK(pen_profile8_validate(0x800000,0x800000,a,5)!=0);
 CHECK(pen_profile8_validate(0x800000,0x800000,a,7)!=0);
 for(int i=0;i<6;i++){
  memcpy(a,valid,sizeof valid);a[i].address+=4096;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].size-=4096;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].subtype^=1;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].type^=1;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].encrypted=1;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].readonly=1;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
  memcpy(a,valid,sizeof valid);a[i].label="unknown";CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
 }
 memcpy(a,valid,sizeof valid);a[5]=a[4];CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
 memcpy(a,valid,sizeof valid);a[5].address=0xfffff000;a[5].size=0x2000;CHECK(pen_profile8_validate(0x800000,0x800000,a,6)!=0);
 reset();
#if TEST_PROFILE_ENABLED
 CHECK(pen_application_partition_guard()==ESP_OK);CHECK(releases==0);
 current=table[4];CHECK(pen_application_partition_guard()==ESP_OK);
 reset();physical=0x1000000;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();logical=0x400000;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();physical_error=-77;CHECK(pen_application_partition_guard()==-77);CHECK(calls==1);
 reset();logical_error=-78;CHECK(pen_application_partition_guard()==-78);CHECK(calls==2);
 reset();count=7;table[6]=table[0];CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);CHECK(releases==1);
 reset();count=0;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();null_part=1;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);CHECK(releases==1);
 reset();table[0].flash_chip=&other_chip;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);CHECK(releases==1);
 reset();table[5].readonly=true;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();table[5].erase_size=8192;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();null_running=1;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();current=table[0];CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();current.flash_chip=&other_chip;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();current.readonly=true;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();current.encrypted=true;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();current.address+=65536;CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
 reset();strcpy(current.label,"factory");CHECK(pen_application_partition_guard()==ESP_ERR_INVALID_STATE);
#else
 (void)other_chip;
 CHECK(pen_application_partition_guard()==ESP_ERR_NOT_SUPPORTED);CHECK(calls==0);
#endif
 puts("profile8 pure validator and IDF read-only guard tests passed");return 0;
}
