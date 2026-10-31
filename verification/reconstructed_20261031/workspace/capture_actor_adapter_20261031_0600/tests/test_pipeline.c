#include "adapter.h"
#include "board_provider.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t pixels[PEN_CAPTURE_BYTES],flash[64*64];static pen_roi_workspace work;static pen_store store;static pen_app app;static pen_capture cap;static pen_adapter a;static unsigned calls,frames,stub_calls,gives,errors;
static int controls[]={22};static int pw(void*x){(void)x;return 0;}
static pen_capture_profile profile={"HOST_SYNTHETIC","NO_ELECTRICAL_EVIDENCE",99,0x31,10000000,40000000,1,1,1,1,{1,2,3,4,5,6,7,8},9,10,11,12,13,14,controls,1,pw,pw,pw,NULL};
static int op(void*x,const pen_capture_profile*p,uint16_t*id,pen_capture_clock*k){(void)x;(void)p;*id=0x31;return pen_capture_clock_plan(10000000,k);}
static int close_cap(void*x){(void)x;return 0;}
static int take(void*x,uint32_t m,pen_capture_raw*r){(void)x;(void)m;*r=(pen_capture_raw){pixels,sizeof pixels,640,480,640,900000,pixels,1,1};return 0;}
static void give(void*x,void*o){(void)x;CHECK(o==pixels);gives++;}
static uint64_t now(void*x){(void)x;return 1000000;}
static pen_capture_backend ops={op,close_cap,take,give,now};
static int rd(void*x,size_t o,uint8_t*b,size_t n){(void)x;if(o>sizeof flash||n>sizeof flash-o)return -1;memcpy(b,flash+o,n);return 0;}
static int wr(void*x,size_t o,const uint8_t*b,size_t n){(void)x;if(o>sizeof flash||n>sizeof flash-o)return -1;for(size_t j=0;j<n;j++){if((flash[o+j]&b[j])!=b[j])return -1;flash[o+j]&=b[j];}return 0;}
static int sync_flash(void*x){(void)x;return 0;}
/* Explicit test-only rejecting mapper; demonstrates sidecar ABI without
 * granting camera qualification or producing a physical tip coordinate. */
static int stub_mapper(void*x,const pen_app_frame*f,const pen_roi_opt_result*r,pen_tip_solution*t){
 (void)r;stub_calls++;pen_capture_roi_origin o;CHECK(!pa_origin(x,f,&o));CHECK(o.left==440&&o.top==280&&o.full_stride==640);CHECK(o.parent_frame_id==f->frame_id&&o.source_id==99);memset(t,0,sizeof(*t));return -1;
}
static int consume(void*x,const pen_app_input*i){(void)x;calls++;if(i->frame){frames++;pen_tip_solution t;pen_roi_opt_result r={0};CHECK(stub_mapper(&a,i->frame,&r,&t)==-1);CHECK(!t.pose_valid);CHECK(i->frame->origin==PEN_FRAME_SYNTHETIC);}
 pen_app_result result;CHECK(!pen_app_step(&app,i,&result));CHECK(!result.tip_accepted);CHECK(!(result.recorder.actions&PEN_CP_SLEEP_REQUEST));return 0;
}
static void failure(void*x,int code){(void)x;CHECK(code<0);errors++;pen_store_stop(&store);}
int main(void){
 CHECK(pen_get_board_provider()==NULL);
 pen_app_config config={.paper={710,1000,0,0},.contact={.press_us=0,.camera_timeout_us=10000,.contact_stuck_us=100000,.irq_stuck_us=100000,.idle_us=10000,.min_confidence=750},.source_id=99,.page=99,.max_frame_gap_us=2000,.min_x_um=-1000000,.max_x_um=1000000,.min_y_um=-1000000,.max_y_um=1000000};
 pen_capture_app_disqualify(&config);CHECK(!config.camera_qualified&&!config.map_tip&&!config.calibration_revision);
 memset(flash,255,sizeof flash);store=(pen_store){.log={.read=rd,.program=wr,.sync=sync_flash,.slots=64}};CHECK(!pen_store_open(&store,42));CHECK(!pen_store_begin(&store,123));CHECK(!pen_app_init(&app,&store,&work,&config));
 pen_capture_construct(&cap,&ops,NULL);CHECK(!pen_capture_start_checked(&cap,&profile,1));CHECK(!pa_init(&a,&cap,consume,failure,NULL,1));pen_capture_view v;CHECK(!pen_capture_get(&cap,1,&v));
 CHECK(!pa_idle(&a,900010));CHECK(!pa_frame(&a,&v,440,280,200,200));CHECK(!pa_edge(&a,900000,1,0));CHECK(!pa_edge(&a,900020,0,0));CHECK(!pa_drain(&a,900020));
 CHECK(calls==4&&frames==1&&stub_calls==1&&gives==1&&!errors);
 pen_app_status status;CHECK(!pen_app_get_status(&app,&status));for(size_t j=0;j<status.slots_used;j++){pen_sample sample;CHECK(!pen_log_read(&store.log,j,&sample));CHECK(!(sample.flags&PEN_VALID)&&!sample.page&&!sample.x_um&&!sample.y_um);}
 CHECK(pa_edge(&a,900001,1,0)==PA_LATE);CHECK(errors==1&&!store.recording);CHECK(!pa_stop(&a));
 puts("PASS actual pipeline/storage/contact modules + NULL provider; synthetic sidecar mapper only; no VALID coordinates");
}
