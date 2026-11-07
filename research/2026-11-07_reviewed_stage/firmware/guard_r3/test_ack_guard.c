/* Real portable store/app code with existing explicit-CHECK memory callbacks. */
#define main existing_maintenance_test_main
#include "test_application_maintenance.c"
#undef main
#include <limits.h>
#include <stddef.h>
static unsigned writes,syncs,ack_ops,fail_at;
static int counted_write(void*c,size_t o,const uint8_t*b,size_t n){
 writes++;if(fail_at&&++ack_ops==fail_at)return -1;return wr(c,o,b,n);
}
static int counted_sync(void*c){syncs++;if(fail_at&&++ack_ops==fail_at)return -1;return sync_log(c);}
static void begin_one(void){
 memset(bytes,255,sizeof bytes);intent=erase_failure=erases=0;memset(&store,0,sizeof store);
 writes=syncs=ack_ops=fail_at=0;
 store.log=(pen_log){.read=rd,.program=counted_write,.sync=counted_sync,.slots=32};
 store.get_erase_intent=get;store.set_erase_intent=set;store.erase_all=erase;
 CHECK(pen_store_open(&store,42)==0&&pen_store_begin(&store,7)==0);
 pen_sample p={.timestamp_us=100,.flags=PEN_GAP};CHECK(pen_store_append(&store,&p,&p)==0);
 writes=syncs=0;
}
static void direct_case(int authenticated){
 begin_one();pen_sample p;CHECK(pen_store_offer(&store,&p)==0&&p.session==7&&p.seq==0);
 uint8_t before[sizeof bytes];memcpy(before,bytes,sizeof bytes);pen_store saved=store;
 int rc=pen_store_ack(&store,7,0,authenticated);
 if(rc==0){
  pen_store_stop(&store);CHECK(pen_store_open(&store,42)==0);
  int pending=pen_store_offer(&store,&p),reclaimed=pen_store_reclaim(&store,1);
  fprintf(stderr,"ACK IMPACT: authenticated=%d accepted; after reopen offer=%d; legitimate-idle reclaim=%d erases=%d\n",authenticated,pending,reclaimed,erases);
 }
 CHECK(rc==-3&&!writes&&!syncs&&!erases&&!intent);
 CHECK(!memcmp(before,bytes,sizeof bytes)&&!memcmp(&saved,&store,sizeof store));
 pen_store_stop(&store);CHECK(pen_store_open(&store,42)==0);
 CHECK(pen_store_reclaim(&store,1)==-3&&!erases&&!intent);
 CHECK(pen_store_offer(&store,&p)==0&&p.session==7&&p.seq==0);
 unsigned writes_before=writes,syncs_before=syncs;
 CHECK(pen_store_ack(&store,7,0,1)==0&&writes==writes_before+2&&syncs==syncs_before+2);
 CHECK(pen_store_open(&store,42)==0&&pen_store_offer(&store,&p)==1);
 CHECK(pen_store_reclaim(&store,1)==0&&erases==1&&!intent&&!store.log.next);
}
static void direct_tests(void){
 direct_case(2);
 for(int value=-255;value<=255;value++)if(value!=1)direct_case(value);
 direct_case(INT_MIN);direct_case(INT_MAX);direct_case(-65536);direct_case(65536);
 begin_one();CHECK(pen_store_ack(&store,7,0,1)==-3&&!writes&&!syncs); /* No offer. */
 pen_sample p;CHECK(pen_store_offer(&store,&p)==0);
 CHECK(pen_store_ack(&store,8,0,1)==-3&&pen_store_ack(&store,7,1,1)==-3&&!writes&&!syncs);
 CHECK(pen_store_ack(&store,7,0,1)==0);
 CHECK(pen_store_ack(&store,7,0,1)==-3&&writes==2&&syncs==2); /* Repeat cannot add writes. */
 /* Four ACK write/sync failure points. Final-sync failure is ambiguous: in
  * this synchronous memory fixture the complete ACK marker already persists. */
 for(unsigned phase=1;phase<=4;phase++){
  begin_one();CHECK(pen_store_offer(&store,&p)==0);fail_at=phase;
  CHECK(pen_store_ack(&store,7,0,1)==-1&&store.log.faulted);
  fail_at=0;pen_store_stop(&store);CHECK(pen_store_open(&store,42)==0);
  int pending=pen_store_offer(&store,&p);CHECK(pending==(phase==4?1:0));
  if(pending==0)CHECK(pen_store_ack(&store,7,0,1)==0);
  CHECK(pen_store_open(&store,42)==0&&pen_store_offer(&store,&p)==1);
  CHECK(pen_store_reclaim(&store,1)==0&&erases==1);
 }
 puts("store ACK: exact security=1; invalid facts preserve offer/media/replay, prevent reclaim; lawful retry and four write/sync failure points PASS");
}
static const size_t security_fields[]={offsetof(pen_link_security,encrypted),offsetof(pen_link_security,authenticated),offsetof(pen_link_security,bonded),offsetof(pen_link_security,approved_peer)};
static void app_tests(void){
 for(unsigned side=0;side<2;side++)for(unsigned field=0;field<4;field++)for(unsigned value=0;value<=255;value++)if(value!=1){
  begin_one();CHECK(pen_app_init(&app,&store,&workspace,&config)==0);
  CHECK(pen_app_offer(&app,&link,send_packet,NULL)==0);
  pen_link_security current=link,receipt=link;
  ((uint8_t*)(side?&receipt:&current))[security_fields[field]]=(uint8_t)value;
  uint8_t before[sizeof bytes];memcpy(before,bytes,sizeof bytes);pen_store saved=store;pen_app saved_app=app;
  CHECK(pen_app_ack(&app,&current,&receipt,7,0)==-3&&!writes&&!syncs&&!erases);
  CHECK(!memcmp(before,bytes,sizeof bytes)&&!memcmp(&saved,&store,sizeof store)&&!memcmp(&saved_app,&app,sizeof app));
  CHECK(pen_app_ack(&app,&link,&link,7,0)==0);
 }
 for(unsigned kind=0;kind<4;kind++){
  begin_one();CHECK(pen_app_init(&app,&store,&workspace,&config)==0);
  CHECK(pen_app_offer(&app,&link,send_packet,NULL)==0);pen_link_security current=link,receipt=link;
  if(kind==0)current.connection_epoch=0;
  if(kind==1)receipt.connection_epoch=0;
  if(kind==2)receipt.connection_epoch++;
  if(kind==3){current.connection_epoch++;receipt=current;}
  CHECK(pen_app_ack(&app,&current,&receipt,7,0)==-3&&!writes&&!syncs&&!erases);
  CHECK(pen_app_ack(&app,&link,&link,7,0)==0);
 }
 puts("existing application ACK boundary: 2040 current/receipt malformed boolean facts plus zero/stale epochs rejected; valid retry PASS");
}
int main(int argc,char**argv){CHECK(argc==2);if(!strcmp(argv[1],"store"))direct_tests();else{CHECK(!strcmp(argv[1],"app"));app_tests();}return 0;}
