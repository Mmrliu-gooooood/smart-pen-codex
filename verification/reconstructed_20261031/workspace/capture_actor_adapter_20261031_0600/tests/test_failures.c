#include "adapter.h"
#include "pen_capture_idf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks,gives,closes,notifications,calls;static int last_fault,sink_error,close_error,reenter;
static uint8_t bytes[PEN_CAPTURE_BYTES];static pen_capture capture;static pen_adapter adapter;
static int pins[]={22};static int power(void*x){(void)x;return 0;}
/* These numbers are a synthetic validator fixture, NOT a wiring proposal. */
static pen_capture_profile profile={"HOST_ONLY","NO_PHYSICAL_EVIDENCE",99,0x31,10000000,40000000,1,1,1,1,{1,2,3,4,5,6,7,8},9,10,11,12,13,14,pins,1,power,power,power,NULL};
static int op(void*x,const pen_capture_profile*p,uint16_t*id,pen_capture_clock*k){(void)x;(void)p;*id=0x31;return pen_capture_clock_plan(10000000,k);}
static int cl(void*x){(void)x;closes++;return close_error;}
static int tk(void*x,uint32_t m,pen_capture_raw*r){(void)x;(void)m;*r=(pen_capture_raw){bytes,sizeof bytes,640,480,640,900000,bytes,1,1};return 0;}
static void gv(void*x,void*o){(void)x;CHECK(o==bytes);gives++;}
static uint64_t nw(void*x){(void)x;return 1000000;}
static pen_capture_backend ops={op,cl,tk,gv,nw};
static unsigned expected_left,expected_top;static const uint8_t*expected_gray;
static uint64_t seen[32];static uint8_t contact[32];
static void fault(void*,int);
static int sink(void*x,const pen_app_input*i){(void)x;CHECK(calls<32);seen[calls]=i->now_us;contact[calls]=i->raw_contact;calls++;
 CHECK(i->usb_sleep_allowed==0); /* candidate never requests sleep authorization */
 if(reenter){CHECK(pa_init(&adapter,&capture,sink,fault,NULL,1)==PA_STATE);CHECK(pa_edge(&adapter,i->now_us+1,1,0)==PA_STATE);CHECK(pa_drain(&adapter,i->now_us)==PA_STATE);CHECK(pa_stop(&adapter)==PA_STATE);}
 if(i->frame){pen_capture_roi_origin origin;pen_app_frame copy=*i->frame;CHECK(!pa_origin(&adapter,i->frame,&origin));CHECK(origin.left==expected_left&&origin.top==expected_top);CHECK(i->frame->gray==expected_gray);CHECK(pa_origin(&adapter,&copy,&origin)==PA_LEASE);CHECK(!origin.parent_frame_id);}
 return sink_error;}
static void fault(void*x,int e){(void)x;notifications++;last_fault=e;CHECK(pa_idle(&adapter,999999)==PA_STATE);}
static void setup(void){memset(&adapter,0,sizeof adapter);expected_left=expected_top=0;expected_gray=bytes;gives=closes=notifications=calls=0;sink_error=close_error=reenter=last_fault=0;pen_capture_construct(&capture,&ops,NULL);CHECK(!pen_capture_start_checked(&capture,&profile,1));CHECK(!pa_init(&adapter,&capture,sink,fault,NULL,1));}
static pen_capture_view frame(void){pen_capture_view v;CHECK(!pen_capture_get(&capture,1,&v));return v;}
int main(void){
 const char* names[]={NULL,"","SC031GS","SC035HGS","HOST_ONLY","generic24"};
 for(size_t k=0;k<sizeof names/sizeof names[0];k++)CHECK(!pen_capture_reviewed_profile(names[k]));
 setup();CHECK(!pa_drain(&adapter,100));CHECK(pa_edge(&adapter,100,1,0)==PA_LATE);CHECK(notifications==1&&last_fault==PA_LATE&&closes==1);CHECK(pa_idle(&adapter,200)==PA_STATE);CHECK(calls==0);CHECK(!pa_stop(&adapter));
 setup();CHECK(!pa_drain(&adapter,100));CHECK(pa_drain(&adapter,99)==PA_LATE);CHECK(notifications==1);CHECK(!pa_stop(&adapter));
 setup();CHECK(pa_edge(&adapter,0,1,0)==PA_INPUT);CHECK(calls==0&&notifications==1);CHECK(!pa_stop(&adapter));
 setup();CHECK(pa_edge(&adapter,1,2,0)==PA_INPUT);CHECK(notifications==1);CHECK(!pa_stop(&adapter));
 setup();pen_capture_view v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));CHECK(pa_init(&adapter,&capture,sink,fault,NULL,1)==PA_STATE);CHECK(!gives);
 for(unsigned k=0;k<PA_CAPACITY-1;k++)CHECK(!pa_edge(&adapter,900001+k,1,0));
 CHECK(pa_idle(&adapter,900010)==PA_FULL);CHECK(gives==1&&closes==1&&notifications==1&&calls==0);CHECK(pa_drain(&adapter,900020)==PA_STATE);CHECK(!pa_stop(&adapter));CHECK(gives==1);
 setup();v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));CHECK(pa_frame(&adapter,&v,0,0,96,96)==PA_LEASE);CHECK(gives==1&&closes==1);CHECK(!pa_stop(&adapter));
 setup();v=frame();expected_left=20;expected_top=10;expected_gray=bytes+6420;CHECK(!pa_frame(&adapter,&v,20,10,96,96));CHECK(!pa_drain(&adapter,900000));CHECK(calls==1&&gives==1);CHECK(!pa_stop(&adapter));
 for(unsigned field=0;field<3;field++){setup();v=frame();if(field==0)v.source_id++;if(field==1)v.frame_id++;if(field==2)v.timestamp_us++;CHECK(pa_frame(&adapter,&v,0,0,96,96)==PA_LEASE);CHECK(gives==1&&calls==0&&notifications==1);CHECK(!pa_stop(&adapter));}
 setup();v=frame();v.synthetic=0;CHECK(pa_frame(&adapter,&v,0,0,96,96)==PA_LEASE);CHECK(gives==1&&notifications==1);CHECK(!pa_stop(&adapter));
 setup();v=frame();CHECK(pa_frame(&adapter,&v,600,400,96,96)==PA_LEASE);CHECK(gives==1);CHECK(!pa_stop(&adapter));
 setup();v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));sink_error=-1;CHECK(pa_drain(&adapter,900000)==PA_SINK);CHECK(calls==1&&gives==1&&closes==1&&notifications==1);CHECK(!pa_stop(&adapter));
 setup();v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));CHECK(!pa_stop(&adapter));CHECK(gives==1&&closes==1&&calls==0);CHECK(!pa_stop(&adapter));CHECK(gives==1&&closes==1);
 setup();v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));CHECK(!pen_capture_release(&capture,v.frame_id));CHECK(pa_drain(&adapter,900000)==PA_LEASE);CHECK(calls==0&&gives==1);CHECK(!pa_stop(&adapter));
 setup();reenter=1;CHECK(!pa_idle(&adapter,100));CHECK(!pa_edge(&adapter,100,1,0));CHECK(!pa_edge(&adapter,100,0,0));CHECK(!pa_edge(&adapter,99,1,0));CHECK(!pa_drain(&adapter,100));CHECK(calls==4&&seen[0]==99&&seen[1]==100&&seen[2]==100&&seen[3]==100);CHECK(contact[0]==1&&contact[1]==1&&contact[2]==0&&contact[3]==0);CHECK(!notifications);CHECK(!pa_stop(&adapter));
 /* All six permutations converge; cutoff leaves future event queued. */
 const unsigned order[6][3]={{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
 for(unsigned k=0;k<6;k++){setup();for(unsigned j=0;j<3;j++)CHECK(!pa_edge(&adapter,100+order[k][j]*10,(uint8_t)(order[k][j]%2),0));CHECK(!pa_drain(&adapter,110));CHECK(calls==2&&seen[0]==100&&seen[1]==110);CHECK(!pa_drain(&adapter,120));CHECK(calls==3&&seen[2]==120);CHECK(!pa_stop(&adapter));}
 setup();close_error=-1;v=frame();CHECK(!pa_frame(&adapter,&v,0,0,96,96));CHECK(pa_stop(&adapter)==PA_LEASE);CHECK(gives==1&&closes==1&&notifications==1);CHECK(pa_edge(&adapter,900001,1,0)==PA_STATE);
 CHECK(pa_init(NULL,&capture,sink,fault,NULL,1)==PA_INPUT);CHECK(pa_origin(NULL,NULL,NULL)==PA_INPUT);CHECK(pa_stop(NULL)==PA_STATE);
 printf("PASS %u failure/ordering assertions; synthetic only\n",checks);
}
