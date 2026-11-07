/* Actual storage_idf.c with the repository's host API doubles, assertions on. */
#define main existing_storage_idf_test_main
#include "test_storage_idf_mock.c"
#undef main
#include <limits.h>
#include <stdlib.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"IDF ACK FAIL %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t good_ack[20];
static void start_one(pen_storage_idf*c){
 writes=erases=0;init_fail=commit_fail=0;durable=(struct metadata){0};stage=durable;
 memset(flash,255,sizeof flash);CHECK(pen_storage_idf_open(c,1,"pen_records",42)==ESP_OK);
 uint64_t epoch=0;CHECK(pen_storage_idf_begin_boot(c,&epoch)==ESP_OK&&epoch==1);
 pen_sample p={.flags=PEN_GAP,.timestamp_us=100};CHECK(pen_store_append(&c->store,&p,&p)==0);
 uint8_t fragments[3][20];CHECK(pen_storage_idf_fragments(c,fragments)==0);
 memset(good_ack,0,sizeof good_ack);good_ack[0]='A';good_ack[1]='K';good_ack[2]=1;
 put(good_ack+4,epoch,8);put(good_ack+12,0,4);put(good_ack+16,pen_crc32(good_ack,16),4);writes=0;
}
static void invalid_security(unsigned field,int value){
 pen_storage_idf c;start_one(&c);int security[4]={1,1,1,1};security[field]=value;
 uint8_t before[sizeof flash];memcpy(before,flash,sizeof flash);pen_store saved=c.store;
 int rc=pen_storage_idf_ack(&c,good_ack,20,security[0],security[1],security[2],security[3]);
 if(rc==0){
  pen_storage_idf_close(&c);CHECK(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_OK);
  uint8_t fragments[3][20];int pending=pen_storage_idf_fragments(&c,fragments);
  int reclaimed=pen_store_reclaim(&c.store,1);
  fprintf(stderr,"IDF ACK IMPACT: field=%u fact=%d accepted; reopen fragments=%d; legitimate-idle reclaim=%d erases=%u\n",field,value,pending,reclaimed,erases);
 }
 CHECK(rc==-3&&!writes&&!erases&&!memcmp(before,flash,sizeof flash)&&!memcmp(&saved,&c.store,sizeof saved));
 pen_storage_idf_close(&c);CHECK(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_OK);
 CHECK(pen_store_reclaim(&c.store,1)==-3&&!erases);
 uint8_t fragments[3][20];CHECK(pen_storage_idf_fragments(&c,fragments)==0);
 CHECK(pen_storage_idf_ack(&c,good_ack,20,1,1,1,1)==0&&writes==2);
 pen_storage_idf_close(&c);CHECK(pen_storage_idf_open(&c,1,"pen_records",42)==ESP_OK);
 CHECK(pen_storage_idf_fragments(&c,fragments)==1&&pen_store_reclaim(&c.store,1)==0&&erases==1);
 pen_storage_idf_close(&c);
}
int main(void){
 invalid_security(0,2);
 for(unsigned field=0;field<4;field++){
  for(int value=-255;value<=255;value++)if(value!=1)invalid_security(field,value);
  invalid_security(field,INT_MIN);invalid_security(field,INT_MAX);invalid_security(field,-65536);invalid_security(field,65536);
 }
 /* Keep packet format, exact offered identity and disabled-context rejection. */
 for(unsigned mode=0;mode<10;mode++){
  pen_storage_idf c;start_one(&c);uint8_t packet[20];memcpy(packet,good_ack,20);size_t length=20;
  if(mode==0)packet[0]='X';
  if(mode==1)packet[1]='X';
  if(mode==2)packet[2]=2;
  if(mode==3)packet[3]=1;
  if(mode==4)packet[16]^=1;
  if(mode==5){put(packet+4,2,8);put(packet+16,pen_crc32(packet,16),4);}
  if(mode==6){put(packet+12,1,4);put(packet+16,pen_crc32(packet,16),4);}
  if(mode==7)length=19;
  if(mode==8)length=21;
  if(mode==9)c.enabled=0;
  uint8_t before[sizeof flash];memcpy(before,flash,sizeof flash);
  CHECK(pen_storage_idf_ack(&c,packet,length,1,1,1,1)==-3&&!writes&&!erases&&!memcmp(before,flash,sizeof flash));
  c.enabled=1;CHECK(pen_storage_idf_ack(&c,good_ack,20,1,1,1,1)==0);
  CHECK(pen_storage_idf_ack(&c,good_ack,20,1,1,1,1)==-3&&writes==2);
  pen_storage_idf_close(&c);
 }
 CHECK(pen_storage_idf_ack(NULL,good_ack,20,1,1,1,1)==-3);
 puts("actual IDF ACK HOST DOUBLE: four security facts require exact 1; byte-for-byte retention, reboot/replay and valid ACK/reclaim; packet compatibility PASS");
 return 0;
}
