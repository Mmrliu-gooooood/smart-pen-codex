/* Exercise the public storage and application maintenance gates directly. */
#define main existing_maintenance_test_main
#include "test_application_maintenance.c"
#undef main
#include <limits.h>
static void store_case(int value){
 setup(1);uint8_t before[sizeof bytes];memcpy(before,bytes,sizeof bytes);
 int rc=pen_store_reclaim(&store,value);
 if(value==1){CHECK(rc==0&&erases==1&&!intent&&!store.log.next);}
 else{
  if(rc!=-3||erases)fprintf(stderr,"STORE unsafe safe_idle=%d rc=%d erases=%d\n",value,rc,erases);
  CHECK(rc==-3&&!erases&&!intent&&!store.log.faulted);
  CHECK(!memcmp(before,bytes,sizeof bytes)&&store.log.next==32);
 }
}
static void app_case(unsigned field,int value){
 setup(1);int gates[4]={1,1,0,1};gates[field]=value;
 uint8_t before[sizeof bytes];memcpy(before,bytes,sizeof bytes);
 int rc=pen_app_reclaim(&app,gates[0],gates[1],gates[2],gates[3]);
 int grant=field==2?value==0:value==1;
 if(grant){CHECK(rc==0&&erases==1&&!intent&&!store.log.next);}
 else{
  CHECK(rc==(field>=2&&value<0?-1:1));
  CHECK(!erases&&!intent&&!store.log.faulted&&!memcmp(before,bytes,sizeof bytes));
 }
}
static void recovery_case(int value){
 setup(1);uint8_t before[sizeof bytes];memcpy(before,bytes,sizeof bytes);
 intent=value;int rc=pen_store_open(&store,42);
 if(value==1){
  CHECK(rc==0&&erases==1&&!intent&&!store.log.next);
  CHECK(pen_store_open(&store,42)==0&&erases==1);
 }else if(value==0){CHECK(rc==0&&!erases&&!intent&&store.log.next==32&&!memcmp(before,bytes,sizeof bytes));}
 else{
  if(rc!=-1||erases)fprintf(stderr,"RECOVERY unknown intent=%d rc=%d erases=%d\n",value,rc,erases);
  CHECK(rc==-1&&!erases&&intent==value&&store.log.faulted&&!store.recording);
  CHECK(!memcmp(before,bytes,sizeof bytes));
 }
}
int main(int argc,char**argv){
 CHECK(argc==2);
 if(!strcmp(argv[1],"store")){
  store_case(2);
  for(int value=-255;value<=255;value++)store_case(value);
  store_case(INT_MIN);store_case(INT_MAX);store_case(-65536);store_case(65536);
  setup(0);CHECK(pen_store_reclaim(&store,1)==-3&&!erases&&!intent&&store.log.next==32);
  puts("storage reclaim: only safe_idle==1 grants; signed/boundary invalids and unACK retained PASS");
 }else if(!strcmp(argv[1],"recovery")){
  recovery_case(2);
  for(int value=-255;value<=255;value++)recovery_case(value);
  recovery_case(INT_MIN);recovery_case(INT_MAX);recovery_case(-65536);recovery_case(65536);
  puts("pure storage recovery: intent 0=no erase, 1=resume once, invalid signed integers fail closed PASS");
 }else{
  CHECK(!strcmp(argv[1],"app"));
  for(unsigned field=0;field<4;field++){
   for(int value=-255;value<=255;value++)app_case(field,value);
   app_case(field,INT_MIN);app_case(field,INT_MAX);app_case(field,-65536);app_case(field,65536);
  }
  setup(0);CHECK(pen_app_reclaim(&app,1,1,0,1)==-3&&!erases&&!intent&&store.log.next==32);
  /* Full but live recording is not a maintenance entry. */
  setup(1);app.replay_only=0;app.sleep_prepared=0;
  CHECK(pen_app_reclaim(&app,1,1,0,1)==-3&&!erases&&!intent);
  puts("application reclaim: exact pressure/IRQ/quiet and pending-zero; all integer boundaries PASS");
 }
 return 0;
}
