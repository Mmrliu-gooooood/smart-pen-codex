/* R2 alias/freshness regressions. Reuse unchanged actual pipeline fixture. */
#define main existing_pipeline_main
#include "test_application_pipeline.c"
#undef main
#include "activity_status.h"

static pen_app_activity_watch watch;
static unsigned checks;
static void same(const void*a,const void*b,size_t n){CHECK(!memcmp(a,b,n));checks++;}
static void load(int argc,char**argv,unsigned*u,unsigned*v){
 CHECK(argc==7);FILE*f=fopen(argv[1],"rb");CHECK(f);
 CHECK(fread(pixels,1,sizeof pixels,f)==sizeof pixels);CHECK(!fclose(f));
 *u=(unsigned)strtoul(argv[2],NULL,10);*v=(unsigned)strtoul(argv[3],NULL,10);
 expected_x=(unsigned)strtoul(argv[4],NULL,10);expected_y=(unsigned)strtoul(argv[5],NULL,10);
}
static void begin(pen_app_config*c){
 start(c);(void)step(100,1,PEN_FRAME_SENSOR,1,sizeof pixels);
 watch=(pen_app_activity_watch){0};pen_app_activity_status out;unsigned mask=99;
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask));
 CHECK(mask==PEN_ACTIVITY_INITIAL&&out.activity==PEN_ACTIVITY_TRACKING);
 CHECK(out.durable_reference_known&&out.durable_reference_seq==0);
}
int main(int argc,char**argv){
 unsigned u,v;load(argc,argv,&u,&v);pen_app_config c=config(u,v);begin(&c);
 const char*mode=argv[6];pen_app_activity_watch prior=watch;
 pen_app_activity_status out;memset(&out,0xa5,sizeof out);
 unsigned mask=99;int result;
 if(!strcmp(mode,"stable")||!strcmp(mode,"all")){
  result=pen_app_poll_activity(&app,&watch,&watch.previous,&mask);
  printf("stable out=&watch.previous: result=%d mask=%u watch_unchanged=%d\n",
         result,mask,!memcmp(&prior,&watch,sizeof watch));
  CHECK(result==-1&&mask==99);same(&watch,&prior,sizeof watch);
 }
 if(!strcmp(mode,"invalid")||!strcmp(mode,"all")){
  app.initialized=0;mask=99;
  result=pen_app_poll_activity(&app,&watch,&watch.previous,&mask);
  printf("invalid app, aliased output: result=%d mask=%u watch_unchanged=%d\n",
         result,mask,!memcmp(&prior,&watch,sizeof watch));
  CHECK(result==-1&&mask==99);same(&watch,&prior,sizeof watch);app.initialized=1;
 }
 if(!strcmp(mode,"nested")||!strcmp(mode,"all")){
  (void)step(110,2,PEN_FRAME_SENSOR,1,sizeof pixels);
  pen_app_activity_status saved_out=out;
  result=pen_app_poll_activity(&app,&watch,&out,&out.legacy.contact_faults);
  printf("changes inside output: result=%d reported_faults=%u\n",result,out.legacy.contact_faults);
  CHECK(result==-1);same(&out,&saved_out,sizeof out);same(&watch,&prior,sizeof watch);
 }
 if(strcmp(mode,"all"))return 0;

 /* Legitimate new durable event was not swallowed by the rejected alias. */
 mask=99;CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask));
 CHECK(mask==PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED&&out.durable_reference_seq==1);
 prior=watch;
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask)&&mask==0);
 same(&watch,&prior,sizeof watch);

 /* Ordinary independent buffers remain supported, including real transitions. */
 (void)step(120,0,PEN_FRAME_UNKNOWN,0,0);
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask));
 CHECK(mask==(PEN_ACTIVITY_STATE_CHANGED|PEN_ACTIVITY_DURABLE_REFERENCE_CHANGED));
 CHECK(out.activity==PEN_ACTIVITY_READY&&out.legacy.contact_faults==0);
 prior=watch;pen_app_activity_status saved_out=out;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&watch.previous.legacy.contact_faults)==-1);
 same(&watch,&prior,sizeof watch);same(&out,&saved_out,sizeof out);
 CHECK(pen_app_poll_activity(NULL,&watch,&watch.previous,NULL)==-1);
 same(&watch,&prior,sizeof watch);
 watch.initialized=2;prior=watch;mask=99;
 CHECK(pen_app_poll_activity(&app,&watch,&watch.previous,&mask)==-1&&mask==99);
 same(&watch,&prior,sizeof watch);watch.initialized=1;prior=watch;

 /* Unknown app lifetime does not inspect store or write ANY output. */
 app.initialized=0;mask=99;saved_out=out;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&mask)==-1&&mask==99);
 same(&out,&saved_out,sizeof out);
 same(&watch,&prior,sizeof watch);app.initialized=1;
 /* NULL/other ordinary errors retain clear-output/unchanged-watch policy. */
 CHECK(pen_app_poll_activity(NULL,&watch,&out,&mask)==-1&&!out.version&&!mask);
 same(&watch,&prior,sizeof watch);
 CHECK(pen_app_poll_activity(&app,&watch,NULL,&mask)==-1&&!mask);
 same(&watch,&prior,sizeof watch);
 CHECK(pen_app_poll_activity(&app,&watch,&out,NULL)==-1&&!out.version);
 same(&watch,&prior,sizeof watch);

 /* Legitimate unsigned fields are not allowed to alias changes output. */
 pen_app app_before=app;pen_store store_before=store;prior=watch;saved_out=out;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&app.last_contact_faults)==-1);
 same(&app,&app_before,sizeof app);same(&out,&saved_out,sizeof out);same(&watch,&prior,sizeof watch);
 CHECK(pen_app_poll_activity(&app,&watch,&out,&store.session_count)==-1);
 same(&store,&store_before,sizeof store);same(&out,&saved_out,sizeof out);same(&watch,&prior,sizeof watch);

 /* Aligned union members provide overlap without out-of-bounds access. The
  * rejected member is never dereferenced or written; active input is retained. */
 union {pen_app a;pen_app_activity_status out;pen_app_activity_watch w;} au;
 au.a=app;unsigned char au_saved[sizeof au];memcpy(au_saved,&au,sizeof au);mask=99;
 CHECK(pen_app_get_activity_status(&au.a,&au.out)==-1);same(&au,au_saved,sizeof au);
 CHECK(pen_app_poll_activity(&au.a,&watch,&au.out,&mask)==-1&&mask==99);
 same(&au,au_saved,sizeof au);same(&watch,&prior,sizeof watch);
 CHECK(pen_app_poll_activity(&au.a,&au.w,&out,&mask)==-1&&mask==99);
 same(&au,au_saved,sizeof au);same(&out,&saved_out,sizeof out);
 union {pen_store s;pen_app_activity_status out;pen_app_activity_watch w;} su;
 su.s=store;app.recorder.store=&su.s;unsigned char su_saved[sizeof su];memcpy(su_saved,&su,sizeof su);
 CHECK(pen_app_get_activity_status(&app,&su.out)==-1);same(&su,su_saved,sizeof su);
 CHECK(pen_app_poll_activity(&app,&watch,&su.out,&mask)==-1&&mask==99);
 same(&su,su_saved,sizeof su);same(&watch,&prior,sizeof watch);
 CHECK(pen_app_poll_activity(&app,&su.w,&out,&mask)==-1&&mask==99);
 same(&su,su_saved,sizeof su);same(&out,&saved_out,sizeof out);app.recorder.store=&store;

 /* A real failed reinitialization retains prior store; no output may mutate
  * that store even though initialized=0. The pointer need not be inspected. */
 CHECK(pen_app_init(&app,&store,&workspace,NULL)==-1&&!app.initialized);
 app_before=app;store_before=store;prior=watch;saved_out=out;mask=99;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&store.session_count)==-1);
 same(&store,&store_before,sizeof store);same(&app,&app_before,sizeof app);
 same(&watch,&prior,sizeof watch);same(&out,&saved_out,sizeof out);
 su.s=store;app.recorder.store=&su.s;memcpy(su_saved,&su,sizeof su);app_before=app;
 CHECK(pen_app_get_activity_status(&app,&su.out)==-1);same(&su,su_saved,sizeof su);
 CHECK(pen_app_poll_activity(&app,&su.w,&out,&mask)==-1&&mask==99);
 same(&su,su_saved,sizeof su);same(&app,&app_before,sizeof app);same(&out,&saved_out,sizeof out);
 CHECK(pen_app_poll_activity(&app,&watch,&su.out,&mask)==-1&&mask==99);
 same(&su,su_saved,sizeof su);same(&watch,&prior,sizeof watch);
 CHECK(pen_app_get_activity_status(&app,&out)==-1);same(&out,&saved_out,sizeof out);
 app.recorder.store=&store;app.initialized=2;mask=99;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&mask)==-1&&mask==99);
 same(&out,&saved_out,sizeof out);same(&watch,&prior,sizeof watch);

 /* Time passing outside the CP does not age a passive snapshot. No wall-clock
  * sleeps: the synthetic UI clock below deliberately advances without a step. */
 begin(&c);CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask)&&mask==0);
 prior=watch;saved_out=out;uint64_t ui_now=out.last_event_us;
 for(unsigned n=0;n<128;n++){
  ui_now+=1000000;CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask)&&mask==0);
  CHECK(out.activity==PEN_ACTIVITY_TRACKING&&out.last_event_us==100&&out.event_known);
  CHECK(ui_now-out.last_event_us>c.max_frame_gap_us);
  same(&out,&saved_out,sizeof out);same(&watch,&prior,sizeof watch);
 }
 /* Only processing a later ordered timer step changes the core freshness gate. */
 (void)step(ui_now,0,PEN_FRAME_UNKNOWN,1,0);
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&mask));
 CHECK(out.activity==PEN_ACTIVITY_FAULT&&out.last_event_us==ui_now);
 CHECK(out.legacy.contact_faults&PEN_CP_CONTACT_STUCK);
 CHECK(mask&PEN_ACTIVITY_STATE_CHANGED);
 printf("alias rejection, independent outputs, unchanged error baseline and passive freshness: %u byte-preservation checks PASS\n",checks);
 return 0;
}
