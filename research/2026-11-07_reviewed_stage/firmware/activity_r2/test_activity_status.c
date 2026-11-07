/* Reuse existing actual pipeline fixture and synthetic test-only pose mapper. */
#define main existing_pipeline_main
#include "test_application_pipeline.c"
#undef main
#include "activity_status.h"
#include <limits.h>

static unsigned reads,writes,syncs,fail_sync,fail_read,fail_write;
static int intent;
static pen_app_activity_watch watch;
static unsigned changes;
static unsigned checkpoints;
static int counted_read(void*c,size_t o,uint8_t*b,size_t n){reads++;return reads==fail_read?-1:rd(c,o,b,n);}
static int counted_write(void*c,size_t o,const uint8_t*b,size_t n){writes++;return writes==fail_write?-1:wr(c,o,b,n);}
static int counted_sync(void*c){syncs++;return syncs==fail_sync?-1:sy(c);}
static int get_intent(void*c,int*v){(void)c;*v=intent;return 0;}
static int set_intent(void*c,int v){(void)c;intent=v;return 0;}
static int erase_all(void*c){(void)c;memset(flash,255,sizeof flash);return 0;}
static void begin(pen_app_config*c){
 start(c);watch=(pen_app_activity_watch){0};reads=writes=syncs=fail_sync=fail_read=fail_write=0;intent=0;
 store.log.read=counted_read;store.log.program=counted_write;store.log.sync=counted_sync;
}
static pen_app_activity_status snapshot(enum pen_app_activity expected){
 pen_app_activity_status s;pen_app saved_app=app;pen_store saved_store=store;
 uint8_t saved_flash[sizeof flash];memcpy(saved_flash,flash,sizeof flash);
 unsigned saved_reads=reads,saved_writes=writes,saved_syncs=syncs;
 CHECK(!pen_app_poll_activity(&app,&watch,&s,&changes));
 CHECK(!memcmp(&app,&saved_app,sizeof app)&&!memcmp(&store,&saved_store,sizeof store));
 CHECK(!memcmp(saved_flash,flash,sizeof flash));
 CHECK(reads==saved_reads&&writes==saved_writes&&syncs==saved_syncs);
 CHECK(s.version==1&&s.activity==expected);checkpoints++;return s;
}
static pen_app_result event(uint64_t t,int raw,int irq,int ready,uint64_t id,int expected){
 pen_app_frame f={.gray=pixels,.length=sizeof pixels,.width=256,.height=256,.stride=256,
  .timestamp_us=t,.frame_id=id,.source_id=17,.origin=PEN_FRAME_SENSOR};
 pen_app_input i={.now_us=t,.raw_contact=(uint8_t)raw,.pickup_irq_low=(uint8_t)irq,
  .camera_ready=(uint8_t)ready,.usb_sleep_allowed=1,.frame=id?&f:NULL};
 pen_app_result r={0};CHECK(pen_app_step(&app,&i,&r)==expected);return r;
}
static void load_fixture(int argc,char**argv,unsigned*u,unsigned*v){
 CHECK(argc==6);FILE*f=fopen(argv[1],"rb");CHECK(f);
 CHECK(fread(pixels,1,sizeof pixels,f)==sizeof pixels);CHECK(!fclose(f));
 *u=(unsigned)strtoul(argv[2],NULL,10);*v=(unsigned)strtoul(argv[3],NULL,10);
 expected_x=(unsigned)strtoul(argv[4],NULL,10);expected_y=(unsigned)strtoul(argv[5],NULL,10);
}
int main(int argc,char**argv){
 unsigned u,v;load_fixture(argc,argv,&u,&v);pen_app_config c=config(u,v);
 c.contact.press_us=100;pen_app_activity_status s;pen_app_result r;
 begin(&c);s=snapshot(PEN_ACTIVITY_LOGICAL_ASLEEP);
 CHECK(changes==PEN_ACTIVITY_INITIAL&&s.legacy.recording&&!s.event_known&&!s.durable_reference_known);
 event(100,0,1,0,0,0);s=snapshot(PEN_ACTIVITY_PREPARING);
 CHECK(changes&PEN_ACTIVITY_STATE_CHANGED);CHECK(s.legacy.recording&&!s.pipeline_ready);
 event(110,0,0,1,0,0);s=snapshot(PEN_ACTIVITY_READY);
 CHECK(s.pipeline_ready&&!s.last_raw_contact&&!s.durable_reference_known&&!app.seen_frame);
 event(120,0,0,1,0,0);snapshot(PEN_ACTIVITY_READY);CHECK(changes==0);
 r=event(130,1,0,1,1,0);s=snapshot(PEN_ACTIVITY_CONFIRMING);
 CHECK(r.tip_accepted&&!r.recorder.recorded&&s.preconfirm_count==1&&!s.last_contact_confirmed);
 CHECK(!s.durable_reference_known&&s.legacy.recording&&s.pipeline_ready);
 r=event(230,1,0,1,2,0);s=snapshot(PEN_ACTIVITY_TRACKING);
 CHECK(r.recorder.recorded==2&&s.last_contact_confirmed&&!s.gap_required);
 CHECK(s.durable_reference_known&&s.durable_reference_session==123&&s.durable_reference_seq==1);
 CHECK(changes==(PEN_ACTIVITY_STATE_CHANGED|PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED));
 r=event(240,1,0,1,0,0);snapshot(PEN_ACTIVITY_TRACKING);
 CHECK(!r.recorder.recorded&&changes==0); /* Tracking != new durable point. */
 event(250,1,0,1,3,0);snapshot(PEN_ACTIVITY_TRACKING);
 CHECK(changes==PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED);
 bad_mapping=1;event(260,1,0,1,4,0);s=snapshot(PEN_ACTIVITY_CONTACT_GAP);
 CHECK(s.last_contact_confirmed&&s.gap_required&&s.pipeline_ready);
 CHECK(!(read_slot(3).flags&PEN_VALID));
 bad_mapping=0;event(270,1,0,1,5,0);snapshot(PEN_ACTIVITY_TRACKING);
 CHECK((read_slot(4).flags&(PEN_VALID|PEN_GAP))==(PEN_VALID|PEN_GAP));
 r=event(280,0,0,1,0,0);s=snapshot(PEN_ACTIVITY_READY);
 CHECK(r.recorder.recorded==1&&!s.last_raw_contact&&!s.last_contact_confirmed);
 CHECK(s.legacy.recording&&!(read_slot(5).flags&(PEN_VALID|PEN_CONTACT)));
 event(290,1,0,1,6,0);snapshot(PEN_ACTIVITY_CONFIRMING);
 event(300,0,0,1,0,0);snapshot(PEN_ACTIVITY_READY);
 CHECK(read_slot(6).flags==PEN_GAP); /* Short tap never promotes RAM sample. */
 r=event(10300,0,0,1,0,0);s=snapshot(PEN_ACTIVITY_LOGICAL_ASLEEP);
 CHECK(r.recorder.actions&PEN_CP_SLEEP_REQUEST);CHECK(s.legacy.recording&&!s.legacy.sleep_prepared);
 CHECK(!pen_app_cancel_sleep(&app,10301));snapshot(PEN_ACTIVITY_READY);
 r=event(20301,0,0,1,0,0);CHECK(r.recorder.actions&PEN_CP_SLEEP_REQUEST);
 CHECK(!pen_app_prepare_sleep(&app,0,1));s=snapshot(PEN_ACTIVITY_SLEEP_PREPARED);
 CHECK(!s.legacy.recording&&!s.pipeline_ready&&s.durable_reference_seq==6);
 CHECK(pen_app_cancel_sleep(&app,20302)==-1);snapshot(PEN_ACTIVITY_SLEEP_PREPARED);CHECK(changes==0);

 /* Confirmed physical-contact input is not proof of any valid coordinate. */
 c.contact.press_us=0;begin(&c);r=event(100,1,0,1,0,0);s=snapshot(PEN_ACTIVITY_CONTACT_GAP);
 CHECK(s.last_contact_confirmed&&!s.pipeline_ready&&r.recorder.recorded==1);
 CHECK(!(read_slot(0).flags&PEN_VALID));
 event(101,1,0,1,1,0);snapshot(PEN_ACTIVITY_TRACKING);
 r=event(2202,1,0,1,0,0);s=snapshot(PEN_ACTIVITY_CONTACT_GAP);
 CHECK((r.diagnostics&PEN_APP_STALE)&&!s.pipeline_ready&&s.gap_required);
 event(2203,1,0,1,2,0);snapshot(PEN_ACTIVITY_TRACKING);
 CHECK(read_slot(3).flags&PEN_GAP);
 event(2204,0,0,1,0,0);snapshot(PEN_ACTIVITY_READY);
 event(2205,0,0,0,0,0);snapshot(PEN_ACTIVITY_PREPARING);
 event(12205,0,0,0,0,0);s=snapshot(PEN_ACTIVITY_FAULT);
 CHECK(!s.legacy.recording&&(s.legacy.contact_faults&PEN_CP_CAMERA_TIMEOUT));

 /* Overflow contains explicit GAP, does not mean confirmed/active ink. */
 c.contact.press_us=100;begin(&c);
 for(unsigned n=0;n<9;n++)event(100+n,1,0,1,n+1,0);
 s=snapshot(PEN_ACTIVITY_CONFIRMING);CHECK(s.preconfirm_count==1&&!s.last_contact_confirmed);
 CHECK(s.durable_reference_seq==0&&read_slot(0).flags==(PEN_CONTACT|PEN_GAP));
 event(200,1,0,1,10,0);snapshot(PEN_ACTIVITY_TRACKING);

 /* Partial flush stops at capacity; recorder.faulted is not an I/O fault. */
 begin(&c);store.log.slots=1;event(100,1,0,1,1,0);
 r=event(200,1,0,1,2,-2);s=snapshot(PEN_ACTIVITY_REPLAY_ONLY);
 CHECK(r.recorder.recorded==1&&app.recorder.faulted&&!s.legacy.storage_fault);
 CHECK(!s.legacy.recording&&!s.pipeline_ready&&s.durable_reference_seq==0);
 CHECK(s.last_raw_contact&&s.last_contact_confirmed); /* Explicitly historical. */
 CHECK(!pen_app_prepare_replay_sleep(&app,1,1,0,1));snapshot(PEN_ACTIVITY_SLEEP_PREPARED);
 store.log.faulted=1;snapshot(PEN_ACTIVITY_FAULT); /* Real fault wins. */

 /* Sync failure may already have DONE bytes. Never infer success from slot use. */
 c.contact.press_us=0;
 for(unsigned cut=1;cut<=2;cut++){
  begin(&c);fail_sync=cut;event(100,1,0,1,1,-1);s=snapshot(PEN_ACTIVITY_FAULT);
  CHECK(!s.durable_reference_known&&s.legacy.slots_used==1&&!s.pipeline_ready);
  CHECK(!s.legacy.recording&&s.legacy.storage_fault);
  if(cut==2)CHECK(!memcmp(flash+60,"DONE",4));
  fail_sync=0;CHECK(!pen_store_open(&store,42));
  CHECK(!pen_app_init_replay(&app,&store,&workspace,&c));s=snapshot(PEN_ACTIVITY_REPLAY_ONLY);
  CHECK(s.durable_reference_known==(cut==2));
  if(cut==2)CHECK(s.durable_reference_seq==0&&s.durable_reference_session==123);
 }
 begin(&c);event(100,1,0,1,1,0);fail_sync=syncs+2;
 event(110,1,0,1,2,-1);s=snapshot(PEN_ACTIVITY_FAULT);
 CHECK(s.durable_reference_known&&s.durable_reference_seq==0); /* Failed second append excluded. */
 begin(&c);event(100,1,0,1,1,0);event(99,1,0,1,0,0);
 s=snapshot(PEN_ACTIVITY_FAULT);CHECK(s.legacy.contact_faults&PEN_CP_CLOCK);
 begin(&c);event(100,1,0,1,1,0);pen_store_stop(&store);snapshot(PEN_ACTIVITY_BLOCKED);

 /* Reopen can expose old-session durable data alongside a new open session. */
 begin(&c);event(100,1,0,1,1,0);pen_store_stop(&store);
 CHECK(!pen_store_begin(&store,124)&&!pen_app_init(&app,&store,&workspace,&c));
 s=snapshot(PEN_ACTIVITY_LOGICAL_ASLEEP);
 CHECK(s.legacy.recording_session==124&&s.durable_reference_session==123);
 event(110,1,0,1,2,0);s=snapshot(PEN_ACTIVITY_TRACKING);
 CHECK(s.durable_reference_session==124&&s.durable_reference_seq==0);
 /* Synthetic metadata edge, not billions of append operations. */
 store.last_seq[store.session_count-1]=UINT32_MAX;
 s=snapshot(PEN_ACTIVITY_TRACKING);CHECK(s.durable_reference_seq==UINT32_MAX);

 /* Actual read / ACK program / replay sleep sync faults override replay. */
 for(unsigned failure=0;failure<3;failure++){
  begin(&c);store.log.slots=1;event(100,1,0,1,1,0);event(110,1,0,1,2,-2);
  snapshot(PEN_ACTIVITY_REPLAY_ONLY);
  if(failure==0){fail_read=reads+1;CHECK(pen_app_pending(&app)==-1);}
  else if(failure==1){pen_sample p;CHECK(!pen_store_offer(&store,&p));
   fail_write=writes+1;CHECK(pen_store_ack(&store,p.session,p.seq,1)==-1);}
  else {fail_sync=syncs+1;CHECK(pen_app_prepare_replay_sleep(&app,1,1,0,1)==-1);}
  s=snapshot(PEN_ACTIVITY_FAULT);CHECK(s.durable_reference_known&&s.durable_reference_seq==0);
 }
 begin(&c);event(100,1,0,1,1,0);event(110,0,0,1,0,0);event(10110,0,0,1,0,0);
 fail_sync=syncs+1;CHECK(pen_app_prepare_sleep(&app,0,1)==-1);snapshot(PEN_ACTIVITY_FAULT);

 /* Successful authorized idle reclaim forgets old log reference, not history. */
 begin(&c);store.log.slots=1;event(100,1,0,1,1,0);event(110,1,0,1,2,-2);
 store.get_erase_intent=get_intent;store.set_erase_intent=set_intent;store.erase_all=erase_all;
 pen_sample offered;CHECK(!pen_store_offer(&store,&offered));
 CHECK(!pen_store_ack(&store,offered.session,offered.seq,1));snapshot(PEN_ACTIVITY_REPLAY_ONLY);
 CHECK(!pen_app_reclaim(&app,1,1,0,1));s=snapshot(PEN_ACTIVITY_SLEEP_PREPARED);
 CHECK(!s.durable_reference_known&&!s.durable_reference_session&&!s.durable_reference_seq);
 CHECK(changes&PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED);
 CHECK(!pen_store_begin(&store,124)&&!pen_app_init(&app,&store,&workspace,&c));
 watch=(pen_app_activity_watch){0};snapshot(PEN_ACTIVITY_LOGICAL_ASLEEP);CHECK(changes==PEN_ACTIVITY_INITIAL);

 /* Synthetic interleaved log accepted by reopen, never generated by writer.
  * Reference B0 is known durable, but is NOT the physically last slot A1. */
 begin(&c);pen_store_stop(&store);
 pen_sample p={.device=42,.session=123,.seq=0,.timestamp_us=100};
 CHECK(!pen_log_append(&store.log,&p));p.session=124;p.timestamp_us=110;
 CHECK(!pen_log_append(&store.log,&p));p.session=123;p.seq=1;p.timestamp_us=120;
 CHECK(!pen_log_append(&store.log,&p));CHECK(!pen_store_open(&store,42));
 CHECK(!pen_app_init_replay(&app,&store,&workspace,&c));s=snapshot(PEN_ACTIVITY_REPLAY_ONLY);
 CHECK(s.durable_reference_session==124&&s.durable_reference_seq==0);
 CHECK(read_slot(2).session==123&&read_slot(2).seq==1);

 /* Fault-on-invalid-source test belongs to the separate R3 boolean overlay. */
#ifdef TEST_BOOLEAN_OVERLAY
 begin(&c);event(100,2,0,1,1,-1);s=snapshot(PEN_ACTIVITY_FAULT);
 CHECK(!s.legacy.recording&&!s.durable_reference_known&&!s.event_known);
#endif
 /* Invalid query is fail-closed, does not leave a stale READY/TRACKING output. */
 pen_app saved=app;pen_app_activity_watch saved_watch=watch;
 CHECK(pen_app_get_activity_status(NULL,&s)==-1&&s.version==0&&s.activity==PEN_ACTIVITY_UNAVAILABLE);
 CHECK(pen_app_get_activity_status(&app,NULL)==-1);
 app.initialized=0;changes=99;pen_app_activity_status saved_status=s;
 CHECK(pen_app_poll_activity(&app,&watch,&s,&changes)==-1&&changes==99);
 CHECK(!memcmp(&s,&saved_status,sizeof s));
 CHECK(!memcmp(&watch,&saved_watch,sizeof watch));app=saved;
 unsigned count=store.session_count;store.session_count=PEN_STORE_MAX_SESSIONS+1;
 CHECK(pen_app_get_activity_status(&app,&s)==-1&&!s.version);store.session_count=count;
 pen_cp cp=app.recorder.contact;
 for(unsigned bad=0;bad<5;bad++){
  app.recorder.contact=cp;
  if(bad==0)app.recorder.contact.phase=(enum pen_cp_phase)99;
  if(bad==1)app.recorder.contact.raw=2;
  if(bad==2)app.recorder.contact.confirmed=2;
  if(bad==3)app.recorder.contact.started=2;
  if(bad==4)app.recorder.contact.buffered_count=PEN_CP_BUFFER+1;
  CHECK(pen_app_get_activity_status(&app,&s)==-1&&!s.version);
 }
 app.recorder.contact=cp;CHECK(pen_app_poll_activity(&app,NULL,&s,&changes)==-1&&!s.version&&!changes);
 CHECK(pen_app_poll_activity(&app,&watch,&s,NULL)==-1&&!s.version);
 watch.initialized=2;saved_watch=watch;changes=99;
 CHECK(pen_app_poll_activity(&app,&watch,&s,&changes)==-1&&!s.version&&!changes);
 CHECK(!memcmp(&watch,&saved_watch,sizeof watch));
 printf("activity snapshot: %u checkpoints; real pipeline/decoder, synthetic mapper and memory I/O; no mutation PASS\n",checkpoints);
 return 0;
}
