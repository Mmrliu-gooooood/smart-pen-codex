#include "pen_capture.h"
#include "pen_capture_app.h"
#include "pen_capture_idf.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);assert(x);}} while(0)
static uint8_t bytes[PEN_CAPTURE_BYTES];
static int ctl[]={22};
static int power(void *x){(void)x;return 0;}
/* Deliberately synthetic pin integers, not a board wiring example. */
static pen_capture_profile profile={"HOST_TEST_ONLY","synthetic-test-not-electrical-evidence",99,
 PEN_CAPTURE_SENSOR_PID,10000000,40000000,1,1,1,1,{1,2,3,4,5,6,7,8},9,10,11,12,13,14,ctl,1,power,power,power,NULL};
typedef struct {int opens,closes,takes,gives,open_rc,close_rc,take_rc;uint16_t pid;
 pen_capture_clock clock;pen_capture_raw raw;uint64_t now;} fake;
static int op(void *v,const pen_capture_profile*p,uint16_t *id,pen_capture_clock*c){fake*f=v;(void)p;f->opens++;*id=f->pid;*c=f->clock;return f->open_rc;}
static int cl(void*v){fake*f=v;f->closes++;return f->close_rc;}
static int tk(void*v,uint32_t ms,pen_capture_raw*r){fake*f=v;CHECK(ms&&ms<=200);f->takes++;*r=f->raw;return f->take_rc;}
static void gv(void*v,void*owner){fake*f=v;CHECK(owner==bytes);f->gives++;}
static uint64_t nw(void*v){return ((fake*)v)->now;}
static pen_capture_backend ops={op,cl,tk,gv,nw};
static void setup(pen_capture*c,fake*f){memset(f,0,sizeof(*f));f->pid=0x31;f->now=1000000;
 pen_capture_clock_plan(10000000,&f->clock);f->raw=(pen_capture_raw){bytes,sizeof(bytes),640,480,640,900000,bytes,1,1};pen_capture_construct(c,&ops,f);}
static void started(pen_capture*c,fake*f){setup(c,f);CHECK(!pen_capture_start_checked(c,&profile,1));}
static void clocks(void){pen_capture_clock c;CHECK(pen_capture_clock_plan(0,&c)==PC_CLOCK);CHECK(!pen_capture_clock_plan(10000000,&c));CHECK(c.divider==16&&c.actual_hz==10000000);CHECK(pen_capture_clock_plan(24000000,&c)==PC_CLOCK);CHECK(c.divider==6&&c.actual_hz==26666666&&c.remainder==4);CHECK(pen_capture_clock_plan(1,&c)==PC_CLOCK);CHECK(pen_capture_clock_plan(UINT32_MAX,&c)==PC_CLOCK);CHECK(pen_capture_clock_plan(10000000,NULL)==PC_CLOCK);}
static void profiles(void){pen_capture_profile p;pen_capture c;fake f;CHECK(!pen_capture_profile_validate(&profile));CHECK(pen_capture_profile_validate(NULL)==PC_PROFILE);
 for(int field=0;field<17;field++){p=profile;switch(field){case 0:p.name=NULL;break;case 1:p.review_reference="";break;case 2:p.source_id=0;break;case 3:p.electrical_reviewed=0;break;case 4:p.scope_reviewed=0;break;case 5:p.psram_reviewed=0;break;case 6:p.power_sequence_reviewed=0;break;case 7:p.expected_pid=0x35;break;case 8:p.requested_xclk_hz=24000000;break;case 9:p.measured_pclk_hz=40000001;break;case 10:p.measured_pclk_hz=0;break;case 11:p.d[1]=p.d[0];break;case 12:p.pclk=-1;break;case 13:p.xclk=49;break;case 14:p.power_off=NULL;break;case 15:p.control_count=0;break;case 16:p.control_gpios=p.d;break;}
 setup(&c,&f);CHECK(pen_capture_start_checked(&c,&p,1)<0);CHECK(!f.opens&&!f.closes&&!f.takes);}
 const char*names[]={NULL,"","SC035HGS","SC031GS","AI30PIN","generic24","HOST_TEST_ONLY"};for(unsigned i=0;i<sizeof(names)/sizeof(*names);i++)CHECK(!pen_capture_reviewed_profile(names[i]));
 setup(&c,&f);CHECK(pen_capture_start_checked(&c,&profile,0)==PC_DISABLED);CHECK(!f.opens);}
static void normal(void){pen_capture c;fake f;pen_capture_view v,b;pen_app_frame a;pen_app_config config;started(&c,&f);CHECK(pen_capture_start_checked(&c,&profile,1)==PC_STATE);CHECK(!pen_capture_get(&c,100,&v));CHECK(v.gray==bytes&&v.length==307200&&v.stride==640&&v.frame_id==1);CHECK(!pen_capture_app_frame(&c,&v,&a));CHECK(a.origin==PEN_FRAME_SYNTHETIC&&a.timestamp_us==900000);CHECK(pen_capture_get(&c,100,&b)==PC_STATE);CHECK(!b.gray);CHECK(pen_capture_release(&c,2)==PC_OWNERSHIP);CHECK(!f.gives);CHECK(!pen_capture_release(&c,v.frame_id));CHECK(f.gives==1);CHECK(pen_capture_release(&c,1)==PC_OWNERSHIP);CHECK(pen_capture_app_frame(&c,&v,&a)==PC_OWNERSHIP);CHECK(!a.gray);
 f.raw.timestamp_us=950000;CHECK(!pen_capture_get(&c,200,&v));CHECK(v.frame_id==2);CHECK(!pen_capture_stop(&c));CHECK(f.gives==2&&f.closes==1);CHECK(!pen_capture_stop(&c));CHECK(f.closes==1);memset(&config,255,sizeof(config));pen_capture_app_disqualify(&config);CHECK(!config.camera_qualified&&!config.map_tip&&!config.calibration_revision);CHECK(!pen_capture_start_checked(&c,&profile,1));f.raw.timestamp_us=990000;CHECK(!pen_capture_get(&c,100,&v));CHECK(v.frame_id==3);CHECK(!pen_capture_stop(&c));}
static void rois(void){pen_capture c;fake f;pen_capture_view v;pen_app_frame a;pen_capture_roi_origin origin;
 started(&c,&f);CHECK(!pen_capture_get(&c,100,&v));
 CHECK(!pen_capture_app_roi(&c,&v,440,280,200,200,&a,&origin));
 CHECK(a.gray==bytes+280*640+440&&a.width==200&&a.height==200&&a.stride==640&&a.length==199*640+200);
 CHECK(origin.left==440&&origin.top==280&&origin.full_width==640&&origin.full_height==480&&origin.parent_frame_id==v.frame_id);
 CHECK(pen_capture_app_roi(&c,&v,441,280,200,200,&a,&origin)==PC_FRAME);CHECK(!a.gray);
 CHECK(pen_capture_app_roi(&c,&v,0,0,95,200,&a,&origin)==PC_FRAME);
 CHECK(pen_capture_app_roi(&c,&v,0,0,200,257,&a,&origin)==PC_FRAME);
 CHECK(pen_capture_app_roi(&c,&v,UINT32_MAX,UINT32_MAX,200,200,&a,&origin)==PC_FRAME);
 CHECK(!pen_capture_release(&c,v.frame_id));CHECK(pen_capture_app_roi(&c,&v,0,0,200,200,&a,&origin)==PC_OWNERSHIP);CHECK(!pen_capture_stop(&c));}
static void failures(void){pen_capture c;fake f;pen_capture_view v;
 for(int which=0;which<14;which++){started(&c,&f);switch(which){case 0:f.raw.data=NULL;break;case 1:f.raw.bytes--;break;case 2:f.raw.bytes++;break;case 3:f.raw.width=639;break;case 4:f.raw.height=481;break;case 5:f.raw.stride=641;break;case 6:f.raw.gray8=0;break;case 7:f.raw.timestamp_us=0;break;case 8:f.raw.timestamp_us=f.now+1;break;case 9:f.raw.timestamp_us=f.now-200001;break;case 10:f.raw.owner=NULL;break;case 11:c.next_frame_id=UINT64_MAX;break;case 12:c.last_timestamp_us=f.raw.timestamp_us;break;case 13:f.take_rc=PC_DRIVER;break;}
 CHECK(pen_capture_get(&c,100,&v)<0);CHECK(!v.gray&&c.state==PC_FAULT&&f.closes==1);CHECK(f.gives==(which==10?0:1));CHECK(pen_capture_get(&c,100,&v)==PC_STATE);CHECK(pen_capture_start_checked(&c,&profile,1)==PC_STATE);CHECK(!pen_capture_stop(&c));}
 started(&c,&f);CHECK(pen_capture_get(&c,0,&v)==PC_MODE);CHECK(pen_capture_get(&c,201,&v)==PC_MODE);CHECK(!f.takes);f.take_rc=PC_TIMEOUT;f.raw.owner=NULL;CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT_FATAL);CHECK(c.state==PC_FAULT&&f.closes==1);
 for(int which=0;which<3;which++){setup(&c,&f);if(which==0)f.open_rc=PC_MEMORY;if(which==1)f.pid=0x35;if(which==2)f.clock.actual_hz=26666666;CHECK(pen_capture_start_checked(&c,&profile,1)<0);CHECK(c.state==PC_FAULT&&f.closes==1);}
 started(&c,&f);CHECK(!pen_capture_get(&c,1,&v));f.close_rc=-1;CHECK(pen_capture_stop(&c)==PC_DRIVER);CHECK(c.state==PC_FAULT&&c.cleanup_failed);CHECK(pen_capture_stop(&c)==PC_DRIVER);CHECK(pen_capture_start_checked(&c,&profile,1)==PC_STATE);CHECK(f.closes==1&&f.gives==1);
}
int main(void){clocks();profiles();normal();rois();failures();printf("PASS %u assertions: portable capture and exact app-header bridge (SYNTHETIC ONLY)\n",checks);}
