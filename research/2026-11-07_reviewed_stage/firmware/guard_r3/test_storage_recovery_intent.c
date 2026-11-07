/* Real storage_idf.c with existing host API doubles, not a target SDK build. */
#define main existing_storage_idf_test_main
#include "test_storage_idf_mock.c"
#undef main
#include <stdlib.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"intent FAIL %d: %s\n",__LINE__,#x);exit(1);}}while(0)
int main(void){
 for(unsigned value=0;value<=255;value++){
  writes=erases=0;init_fail=commit_fail=0;
  durable=(struct metadata){.intent=(uint8_t)value};stage=durable;
  memset(flash,value?0xa5:255,sizeof flash);uint8_t before[sizeof flash];memcpy(before,flash,sizeof flash);
  pen_storage_idf c;int rc=pen_storage_idf_open(&c,1,"pen_records",42);
  if(value==0){CHECK(rc==ESP_OK&&!erases&&!writes&&!memcmp(before,flash,sizeof flash));pen_storage_idf_close(&c);}
  else if(value==1){
   CHECK(rc==ESP_OK&&erases==1&&!writes&&!durable.intent&&!c.store.log.next);
   for(size_t n=0;n<sizeof flash;n++)CHECK(flash[n]==255);
   pen_storage_idf_close(&c);
   CHECK(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_OK&&erases==1);pen_storage_idf_close(&c);
  }else CHECK(rc==ESP_FAIL&&!erases&&!writes&&!c.enabled&&!memcmp(before,flash,sizeof flash));
 }
 puts("actual IDF recovery adapter HOST DOUBLE: intent 0=no erase; 1=resume once; 2..255 rejected unchanged PASS");
 return 0;
}
