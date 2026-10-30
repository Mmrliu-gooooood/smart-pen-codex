#include "pipeline.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} } while(0)
static uint8_t flash[64*64],pixels[256*256];
static pen_roi_workspace workspace;
static pen_store store;static pen_app app;static int bad_mapping,map_calls,send_calls,send_status,sync_fail;
static pen_sample sent;
static unsigned expected_x,expected_y;static uint64_t send_epoch=5;
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;if(o>sizeof flash||n>sizeof flash-o)return -1;memcpy(b,flash+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;if(o>sizeof flash||n>sizeof flash-o)return -1;for(size_t k=0;k<n;k++){if((flash[o+k]&b[k])!=b[k])return -1;flash[o+k]&=b[k];}return 0;}
static int sy(void*c){(void)c;return sync_fail?-1:0;}
/* TEST DOUBLE ONLY: asserts pixel decode, returns deliberately unrelated physical
 * coordinate. Not a lens/pose calibration and never linked into device app. */
static int mapper(void*c,const pen_app_frame*f,const pen_roi_opt_result*r,pen_tip_solution*t){
 (void)c;map_calls++;CHECK(r->decoded.x==expected_x&&r->decoded.y==expected_y);
 *t=(pen_tip_solution){.timestamp_us=f->timestamp_us,.frame_id=f->frame_id,.source_id=f->source_id,
 .calibration_revision=7,.page=99,.x_um=12345,.y_um=-4321,.confidence=900,.pose_valid=1};
 switch(bad_mapping){case 1:t->frame_id++;break;case 2:t->timestamp_us++;break;case 3:t->source_id++;break;
 case 4:t->calibration_revision++;break;case 5:t->page++;break;case 6:t->pose_valid=0;break;
 case 7:t->x_um=1000001;break;case 8:t->confidence=1001;break;case 9:return -1;
 case 10:t->confidence=1;break;default:break;}return 0;
}
static pen_app_config config(unsigned u,unsigned v){return (pen_app_config){
 .paper={710,1000,(uint8_t)u,(uint8_t)v},
 .contact={.press_us=0,.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750},
 .source_id=17,.calibration_revision=7,.page=99,.max_frame_gap_us=2000,
 .min_x_um=-1000000,.max_x_um=1000000,.min_y_um=-1000000,.max_y_um=1000000,
 .camera_qualified=1,.map_tip=mapper};}
static void start(pen_app_config*c){
 memset(flash,255,sizeof flash);store=(pen_store){.log={.read=rd,.program=wr,.sync=sy,.slots=64}};
 sync_fail=bad_mapping=map_calls=send_calls=send_status=0;send_epoch=5;
 CHECK(pen_store_open(&store,42)==0);CHECK(pen_store_begin(&store,123)==0);CHECK(pen_app_init(&app,&store,&workspace,c)==0);
}
static pen_app_result step(uint64_t now,uint64_t id,int origin,int raw,size_t length){
 pen_app_frame f={.gray=pixels,.length=length,.width=256,.height=256,.stride=256,
 .timestamp_us=now,.frame_id=id,.source_id=17,.origin=(enum pen_frame_origin)origin};
 pen_app_input i={.now_us=now,.raw_contact=(uint8_t)raw,.camera_ready=1,.usb_sleep_allowed=1,.frame=id?&f:NULL};
 pen_app_result r;CHECK(pen_app_step(&app,&i,&r)==0);return r;
}
static pen_sample read_slot(size_t n){pen_sample s;CHECK(pen_log_read(&store.log,n,&s)==0);return s;}
static int send_packet(void*c,const uint8_t*b,size_t n,uint64_t epoch){(void)c;CHECK(epoch==send_epoch);send_calls++;CHECK(n==48);CHECK(pen_decode(&sent,b)==0);return send_status;}
int main(int argc,char**argv){
 CHECK(argc==6);FILE*f=fopen(argv[1],"rb");CHECK(f);CHECK(fread(pixels,1,sizeof pixels,f)==sizeof pixels);CHECK(fclose(f)==0);
 unsigned u=(unsigned)strtoul(argv[2],NULL,10),v=(unsigned)strtoul(argv[3],NULL,10);
 expected_x=(unsigned)strtoul(argv[4],NULL,10);expected_y=(unsigned)strtoul(argv[5],NULL,10);
 pen_app_config c=config(u,v);pen_app_result r;pen_sample p;
 start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);CHECK(r.decoded&&r.tip_accepted&&r.recorder.recorded==1);
 p=read_slot(0);CHECK((p.flags&(PEN_VALID|PEN_CONTACT|PEN_GAP))==7&&p.x_um==12345&&p.y_um==-4321&&p.page==99);
 pen_link_security security={1,1,1,1,5},bad={1,1,0,1,5};
 CHECK(pen_app_pending(&app)==1&&!store.offering);
 CHECK(pen_app_ack(&app,&security,&security,123,0)==-3);
 CHECK(pen_app_offer(&app,&bad,send_packet,NULL)==-3&&!send_calls);
 send_status=1;CHECK(pen_app_offer(&app,&security,send_packet,NULL)==1&&sent.seq==0);
 CHECK(pen_app_ack(&app,&security,&security,123,0)==-3); /* busy did not send */
 send_status=0;CHECK(pen_app_offer(&app,&security,send_packet,NULL)==0&&sent.seq==0);
 CHECK(pen_app_ack(&app,&bad,&security,123,0)==-3);
 CHECK(pen_app_ack(&app,&security,&bad,123,0)==-3);
 pen_link_security old=security;old.connection_epoch++;CHECK(pen_app_ack(&app,&security,&old,123,0)==-3);CHECK(pen_app_ack(&app,&security,&security,124,0)==-3);
 CHECK(pen_app_ack(&app,&security,&security,123,1)==-3);CHECK(pen_app_ack(&app,&security,&security,123,0)==0);
 CHECK(pen_app_offer(&app,&security,send_packet,NULL)==1);
 CHECK(pen_app_pending(&app)==0);
 r=step(110,1,PEN_FRAME_SENSOR,1,sizeof pixels);CHECK((r.diagnostics&PEN_APP_BAD_FRAME)&&!r.tip_accepted);p=read_slot(1);CHECK(!(p.flags&PEN_VALID));
 r=step(120,2,PEN_FRAME_SENSOR,1,sizeof pixels);p=read_slot(2);CHECK((p.flags&(PEN_VALID|PEN_GAP))==(PEN_VALID|PEN_GAP));
 r=step(2200,0,0,1,0);CHECK(r.diagnostics&PEN_APP_STALE);p=read_slot(3);CHECK(!(p.flags&PEN_VALID)&&(p.flags&PEN_GAP));
 r=step(2300,3,PEN_FRAME_SENSOR,1,sizeof pixels);p=read_slot(4);CHECK((p.flags&(PEN_VALID|PEN_GAP))==(PEN_VALID|PEN_GAP));
 r=step(2400,0,0,0,0);p=read_slot(5);CHECK(!(p.flags&(PEN_VALID|PEN_CONTACT)));
 for(int mode=1;mode<=10;mode++){start(&c);bad_mapping=mode;r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);CHECK(r.decoded&&!r.tip_accepted&&(r.diagnostics&PEN_APP_MAPPING_REJECTED));p=read_slot(0);CHECK(!(p.flags&PEN_VALID)&&!p.page&&!p.x_um);}
 start(&c);r=step(100,1,PEN_FRAME_SYNTHETIC,1,sizeof pixels);CHECK(r.decoded&&!map_calls&&!r.tip_accepted);CHECK(!(read_slot(0).flags&PEN_VALID));
 start(&c);r=step(100,1,PEN_FRAME_UNKNOWN,1,sizeof pixels);CHECK(!r.decoded&&!map_calls&&(r.diagnostics&PEN_APP_BAD_FRAME));
 c.camera_qualified=0;c.map_tip=NULL;start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);CHECK(r.decoded&&!r.tip_accepted&&(r.diagnostics&PEN_APP_UNQUALIFIED));CHECK(!(read_slot(0).flags&PEN_VALID));
 c=config(u,v);start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,1);CHECK(!r.tip_accepted&&(r.diagnostics&PEN_APP_DECODE_FAILED));
 c.map_tip=NULL;CHECK(pen_app_init(&app,&store,&workspace,&c)==-1&&!app.initialized);c=config(u,v);
 for(unsigned mode=0;mode<5;mode++){
  start(&c);pen_app_frame badf={.gray=pixels,.length=sizeof pixels,.width=256,.height=256,.stride=256,.timestamp_us=100,.frame_id=1,.source_id=17,.origin=PEN_FRAME_SENSOR};
  if(mode==0)badf.source_id++;
  if(mode==1)badf.timestamp_us++;
  if(mode==2)badf.stride=255;
  if(mode==3)badf.width=257;
  if(mode==4)badf.frame_id=0;
  pen_app_input badin={.now_us=100,.raw_contact=1,.camera_ready=1,.usb_sleep_allowed=1,.frame=&badf};
  CHECK(!pen_app_step(&app,&badin,&r)&&!r.tip_accepted&&!map_calls);CHECK(!(read_slot(0).flags&PEN_VALID));
 }
 start(&c);CHECK(pen_app_step(&app,NULL,&r)==-1&&app.recorder.faulted&&!store.recording);
 start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);sync_fail=1;
 pen_app_input i={.now_us=110,.raw_contact=0,.camera_ready=1,.usb_sleep_allowed=1};
 CHECK(pen_app_step(&app,&i,&r)<0&&app.recorder.faulted&&!store.recording);
 CHECK(!(r.recorder.actions&PEN_CP_SLEEP_REQUEST));
 /* Capacity/full is explicit, durable-only and not a silent live trajectory. */
 start(&c);store.log.slots=1;r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);
 pen_app_frame fullf={.gray=pixels,.length=sizeof pixels,.width=256,.height=256,.stride=256,.timestamp_us=200,.frame_id=2,.source_id=17,.origin=PEN_FRAME_SENSOR};
 pen_app_input fullin={.now_us=200,.raw_contact=1,.camera_ready=1,.usb_sleep_allowed=1,.frame=&fullf};
 CHECK(pen_app_step(&app,&fullin,&r)==-2&&!r.tip_accepted&&r.recorder.storage_error==-2);
 pen_app_status status;CHECK(!pen_app_get_status(&app,&status)&&status.last_error==-2&&!status.recording&&status.slots_total==1&&status.slots_used==1);
 /* Durable offline backlog does not prevent idle sleep. Dirty transactions do. */
 start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);r=step(200,0,0,0,0);
 pen_app_input idle={.now_us=10200,.camera_ready=1,.usb_sleep_allowed=1,.storage_pending=1};
 CHECK(!pen_app_step(&app,&idle,&r)&&!(r.recorder.actions&PEN_CP_SLEEP_REQUEST));
 idle.now_us=10300;idle.storage_pending=0;CHECK(!pen_app_step(&app,&idle,&r)&&(r.recorder.actions&PEN_CP_SLEEP_REQUEST));
 CHECK(pen_app_pending(&app)==1);CHECK(pen_app_offer(&app,&security,send_packet,NULL)==0);
 uint8_t retained[sizeof flash];memcpy(retained,flash,sizeof flash);
 CHECK(pen_app_prepare_sleep(&app,1,1)==1&&store.recording);
 CHECK(pen_app_prepare_sleep(&app,0,0)==1&&store.recording);
 CHECK(pen_app_prepare_sleep(&app,0,1)==0&&!store.recording&&!store.offering);
 CHECK(!memcmp(retained,flash,sizeof flash));
 CHECK(pen_app_ack(&app,&security,&security,123,0)==-3);
 CHECK(pen_app_offer(&app,&security,send_packet,NULL)==-3);
 CHECK(pen_app_step(&app,&idle,&r)==-1);
 CHECK(!pen_store_open(&store,42)&&!pen_store_begin(&store,124));
 CHECK(!pen_app_init(&app,&store,&workspace,&c));
 CHECK(pen_app_ack(&app,&security,&security,123,0)==-3); /* no old ticket after wake */
 pen_link_security reconnected=security;reconnected.connection_epoch=6;send_epoch=6;
 CHECK(pen_app_offer(&app,&reconnected,send_packet,NULL)==0&&sent.session==123&&sent.seq==0&&sent.x_um==12345);
 CHECK(pen_app_ack(&app,&reconnected,&security,123,0)==-3);
 CHECK(pen_app_ack(&app,&reconnected,&reconnected,123,0)==0);
 start(&c);r=step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);r=step(200,0,0,0,0);r=step(10200,0,0,0,0);
 CHECK(r.recorder.actions&PEN_CP_SLEEP_REQUEST);sync_fail=1;
 CHECK(pen_app_prepare_sleep(&app,0,1)==-1&&!app.sleep_prepared&&store.log.faulted&&!store.recording);
 puts("application pipeline: real Gray8 decode + explicit test-only mapper, rejection gates, contact/stale GAP, durable replay exact ACK, storage fault PASS");return 0;
}
