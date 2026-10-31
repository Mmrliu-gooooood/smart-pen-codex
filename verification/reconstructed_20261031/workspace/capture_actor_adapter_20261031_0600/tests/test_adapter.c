#include "adapter.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint8_t pixels[PEN_CAPTURE_BYTES];static unsigned gives,closes;static pen_capture c;static pen_adapter a;static uint64_t stamp=900000;
static int ctrl[]={22};static int power(void*x){(void)x;return 0;}
static pen_capture_profile profile={"HOST_ONLY","SYNTHETIC_NO_WIRING",99,0x31,10000000,40000000,1,1,1,1,{1,2,3,4,5,6,7,8},9,10,11,12,13,14,ctrl,1,power,power,power,NULL};
static int op(void*x,const pen_capture_profile*p,uint16_t*id,pen_capture_clock*k){(void)x;(void)p;*id=0x31;return pen_capture_clock_plan(10000000,k);}
static int cl(void*x){(void)x;closes++;return 0;}
static int take(void*x,uint32_t ms,pen_capture_raw*r){(void)x;(void)ms;*r=(pen_capture_raw){pixels,sizeof pixels,640,480,640,stamp,pixels,1,1};return 0;}
static void give(void*x,void*owner){(void)x;CHECK(owner==pixels);gives++;}
static uint64_t now(void*x){(void)x;return 1000000;}
static pen_capture_backend ops={op,cl,take,give,now};
static int steal;static unsigned frame_calls;static pen_app_frame saved;static pen_capture_roi_origin origin;
static uint64_t times[32]; static uint8_t contacts[32]; static unsigned calls;
static int sink(void*x,const pen_app_input*i){(void)x;if(c.state==PC_RUNNING||c.state==PC_HELD)CHECK(i->camera_ready==1);times[calls]=i->now_us;contacts[calls]=i->raw_contact;calls++;
 if(i->frame){frame_calls++;CHECK(i->now_us==900000&&i->raw_contact==1);CHECK(i->frame->origin==PEN_FRAME_SYNTHETIC);CHECK(i->frame->gray==pixels+280*640+440);CHECK(i->frame->stride==640&&i->frame->length==127560);CHECK(!pa_origin(&a,i->frame,&origin));CHECK(origin.left==440&&origin.top==280&&origin.parent_frame_id==1);saved=*i->frame;CHECK(!gives);
 if(steal){CHECK(!pen_capture_release(&c,i->frame->frame_id));CHECK(pa_origin(&a,i->frame,&origin)==PA_LEASE);}}
 return 0;}
static void fault(void*x,int e){(void)x;(void)e;}
int main(void){CHECK(pa_init(&a,&c,sink,fault,NULL,0)==PA_DISABLED);CHECK(pa_init(&a,&c,sink,fault,NULL,1)==PA_OK);CHECK(!pa_edge(&a,300,0,0));CHECK(!pa_edge(&a,100,1,0));CHECK(!pa_idle(&a,200));CHECK(!pa_drain(&a,250));CHECK(calls==2&&times[0]==100&&times[1]==200&&contacts[0]==1&&contacts[1]==1);CHECK(!pa_drain(&a,300));CHECK(calls==3&&times[2]==300&&contacts[2]==0);
 CHECK(!pa_stop(&a));calls=0;CHECK(!pa_init(&a,&c,sink,fault,NULL,1));pen_capture_construct(&c,&ops,NULL);CHECK(!pen_capture_start_checked(&c,&profile,1));pen_capture_view view;CHECK(!pen_capture_get(&c,1,&view));
 CHECK(!pa_frame(&a,&view,440,280,200,200));CHECK(!pa_edge(&a,900000,1,0));CHECK(!pa_drain(&a,900000));CHECK(frame_calls==1&&calls==2&&gives==1);CHECK(pa_origin(&a,&saved,&origin)==PA_LEASE);CHECK(!origin.parent_frame_id);CHECK(!pa_stop(&a));CHECK(closes==1);
 calls=frame_calls=gives=closes=0;steal=1;pen_capture_construct(&c,&ops,NULL);CHECK(!pen_capture_start_checked(&c,&profile,1));CHECK(!pa_init(&a,&c,sink,fault,NULL,1));CHECK(!pen_capture_get(&c,1,&view));CHECK(!pa_frame(&a,&view,440,280,200,200));CHECK(!pa_edge(&a,900000,1,0));CHECK(pa_drain(&a,900000)==PA_LEASE);CHECK(gives==1&&closes==1);puts("PASS invalidated-binding slice");}
