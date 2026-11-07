/* Independent R2 range/lifecycle tests, host only. Include actual sidecar to
 * test its private overlap helper without replacing the production algorithm. */
#define main inherited_pipeline_main
#include "test_application_pipeline.c"
#undef main
#include REVIEW_SIDECAR_SOURCE
#include <stddef.h>

static unsigned long range_checks;
static void range_matrix(void){
 unsigned char arena[4096];
 const size_t sizes[]={1,sizeof(unsigned),8,sizeof(pen_app_activity_status),
  sizeof(pen_app_activity_watch),sizeof(pen_app),sizeof(pen_store)};
 CHECK(sizeof(pen_app)+128<sizeof arena&&sizeof(pen_store)+128<sizeof arena);
 for(size_t x=0;x<128;x++)for(size_t y=0;y<128;y++)
  for(unsigned m=0;m<sizeof sizes/sizeof sizes[0];m++)
   for(unsigned n=0;n<sizeof sizes/sizeof sizes[0];n++){
    size_t pn=sizes[m],qn=sizes[n];
    int expected=x<y+qn&&y<x+pn; /* Small offsets: neither sum can overflow. */
    CHECK(overlaps(arena+x,pn,arena+y,qn)==expected);range_checks++;
   }
 CHECK(!overlaps(NULL,8,arena,8)&&!overlaps(arena,8,NULL,8));
 CHECK(!overlaps(arena,8,arena+8,8));
 CHECK(!overlaps(arena+8,8,arena,8));
 CHECK(overlaps(arena,9,arena+8,8)&&overlaps(arena+8,8,arena,9));
 printf("range helper: %lu checks incl. both directions, containment and exact adjacency PASS\n",range_checks);
}
int main(void){
 range_matrix();pen_app_config c=config(0,0);start(&c);
 pen_app_activity_watch watch={0};pen_app_activity_status out;
 unsigned changes=99;
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&changes));
 CHECK(changes==PEN_ACTIVITY_INITIAL&&out.activity==PEN_ACTIVITY_LOGICAL_ASLEEP);
 pen_app_activity_watch prior=watch;

 /* Partial union overlaps are aligned and backed by complete declared objects;
  * rejected output members are only addressed, never read or written. */
 union {pen_app_activity_watch w;struct {uint64_t pad;pen_app_activity_status out;} shifted;} one;
 one.w=watch;unsigned char saved_one[sizeof one];memcpy(saved_one,&one,sizeof one);
 changes=99;CHECK(pen_app_poll_activity(&app,&one.w,&one.shifted.out,&changes)==-1);
 CHECK(changes==99&&!memcmp(&one,saved_one,sizeof one));
 union {pen_app_activity_status out;struct {uint64_t pad;pen_app_activity_watch w;} shifted;} two;
 two.shifted.w=watch;unsigned char saved_two[sizeof two];memcpy(saved_two,&two,sizeof two);
 CHECK(pen_app_poll_activity(&app,&two.shifted.w,&two.out,&changes)==-1);
 CHECK(changes==99&&!memcmp(&two,saved_two,sizeof two));

 union {pen_app_activity_status out;struct {uint64_t pad;pen_app a;} shifted;} three;
 three.shifted.a=app;unsigned char saved_three[sizeof three];memcpy(saved_three,&three,sizeof three);
 CHECK(pen_app_get_activity_status(&three.shifted.a,&three.out)==-1);
 CHECK(!memcmp(&three,saved_three,sizeof three));
 union {pen_app a;struct {uint64_t pad;pen_app_activity_status out;} shifted;} four;
 four.a=app;unsigned char saved_four[sizeof four];memcpy(saved_four,&four,sizeof four);
 CHECK(pen_app_get_activity_status(&four.a,&four.shifted.out)==-1);
 CHECK(!memcmp(&four,saved_four,sizeof four));
 puts("partial overlapping objects in both address directions rejected without mutation PASS");

 /* Independent adjacent fields must not be treated as overlap. */
 struct {pen_app a;pen_app_activity_watch w;pen_app_activity_status out;unsigned mask;} adjacent;
 adjacent.a=app;adjacent.w=(pen_app_activity_watch){0};adjacent.mask=99;
 CHECK(!pen_app_poll_activity(&adjacent.a,&adjacent.w,&adjacent.out,&adjacent.mask));
 CHECK(adjacent.mask==PEN_ACTIVITY_INITIAL);
 CHECK(!pen_app_poll_activity(&adjacent.a,&adjacent.w,&adjacent.out,&adjacent.mask)&&!adjacent.mask);
 struct {pen_store s;pen_app_activity_watch w;pen_app_activity_status out;unsigned mask;} adjacent_store;
 adjacent_store.s=store;adjacent_store.w=(pen_app_activity_watch){0};
 adjacent.a.recorder.store=&adjacent_store.s;
 CHECK(!pen_app_poll_activity(&adjacent.a,&adjacent_store.w,&adjacent_store.out,&adjacent_store.mask));
 CHECK(adjacent_store.mask==PEN_ACTIVITY_INITIAL);
 puts("independent adjacent app/store/watch/output/change objects accepted PASS");

 /* Fresh failed initialization may leave all fields except initialized
  * indeterminate. The sidecar must return before reading any of those fields. */
 pen_app failed;
 CHECK(pen_app_init(&failed,NULL,NULL,NULL)==-1&&failed.initialized==0);
 memset(&out,0xa5,sizeof out);pen_app_activity_status saved_out=out;changes=99;
 CHECK(pen_app_get_activity_status(&failed,&out)==-1&&!memcmp(&out,&saved_out,sizeof out));
 CHECK(pen_app_poll_activity(&failed,&watch,&out,&changes)==-1);
 CHECK(changes==99&&!memcmp(&out,&saved_out,sizeof out)&&!memcmp(&watch,&prior,sizeof watch));
 failed.initialized=2;
 CHECK(pen_app_poll_activity(&failed,&watch,&out,&changes)==-1&&changes==99);
 CHECK(!memcmp(&out,&saved_out,sizeof out)&&!memcmp(&watch,&prior,sizeof watch));
 puts("real fresh initialization failure / invalid lifecycle returns before other fields or output writes PASS");

 /* Other invalid inputs still clear only independent supplied outputs. */
 CHECK(pen_app_poll_activity(NULL,&watch,&out,&changes)==-1&&!changes&&!out.version);
 CHECK(!memcmp(&watch,&prior,sizeof watch));
 app.recorder.contact.lost=2;memset(&out,0xa5,sizeof out);changes=99;
 CHECK(pen_app_poll_activity(&app,&watch,&out,&changes)==-1&&!changes&&!out.version);
 CHECK(!memcmp(&watch,&prior,sizeof watch));app.recorder.contact.lost=1;
 pen_app_input input={.now_us=100,.pickup_irq_low=1,.camera_ready=1,.usb_sleep_allowed=1};
 pen_app_result result;CHECK(!pen_app_step(&app,&input,&result));
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&changes));
 CHECK(changes==PEN_ACTIVITY_STATE_CHANGED&&out.activity==PEN_ACTIVITY_READY);
 CHECK(!pen_app_poll_activity(&app,&watch,&out,&changes)&&!changes);
 puts("ordinary errors preserve watch; later real transition and steady query remain correct PASS");
 return 0;
}
