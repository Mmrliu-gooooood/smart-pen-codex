#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main candidate_tests_main
#include "test_capture.c"
#undef main
#pragma GCC diagnostic pop
static void extra(void) {
 pen_capture c; fake f; pen_capture_view v,old; pen_app_frame a; pen_capture_roi_origin o;
 started(&c,&f);
 f.take_rc=PC_TIMEOUT;CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(f.gives==1);
 CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(f.gives==2);
 f.take_rc=0;CHECK(!pen_capture_get(&c,200,&v));CHECK(c.timeouts==0);old=v;
 for(unsigned w=95;w<=257;w++) for(unsigned h=95;h<=257;h++) {
  int rc=pen_capture_app_roi(&c,&v,640-w,480-h,w,h,&a,&o);
  if(w>=96&&w<=256&&h>=96&&h<=256){CHECK(!rc);CHECK(a.gray+a.length==bytes+307200);CHECK(o.full_stride==640&&o.source_id==99&&o.parent_frame_id==v.frame_id);}
  else {CHECK(rc==PC_FRAME);CHECK(!a.gray&&!o.parent_frame_id);}
 }
 CHECK(pen_capture_app_roi(&c,&v,0,0,200,200,&a,NULL)==PC_FRAME);CHECK(!a.gray);
 CHECK(!pen_capture_release(&c,v.frame_id));
 f.raw.timestamp_us++;CHECK(!pen_capture_get(&c,1,&v));CHECK(v.frame_id!=old.frame_id);
 CHECK(pen_capture_release(&c,old.frame_id)==PC_OWNERSHIP);CHECK(c.state==PC_HELD);
 CHECK(pen_capture_app_frame(&c,&old,&a)==PC_OWNERSHIP);CHECK(!a.gray);
 CHECK(!pen_capture_stop(&c));CHECK(f.gives==4);CHECK(pen_capture_app_frame(&c,&v,&a)==PC_OWNERSHIP);
 CHECK(!pen_capture_start_checked(&c,&profile,1));f.raw.timestamp_us++;CHECK(!pen_capture_get(&c,1,&v));CHECK(v.frame_id==3);CHECK(!pen_capture_stop(&c));
 started(&c,&f);f.close_rc=PC_POWER;f.take_rc=PC_TIMEOUT;f.raw.owner=NULL;
 CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(pen_capture_get(&c,1,&v)==PC_TIMEOUT);CHECK(pen_capture_get(&c,1,&v)==PC_DRIVER);CHECK(c.cleanup_failed&&c.state==PC_FAULT);CHECK(pen_capture_stop(&c)==PC_DRIVER);CHECK(f.closes==1);
}
int main(void){clocks();profiles();normal();rois();failures();extra();printf("PASS extended portable: %u assertions; exhaustive ROI 95..257 two-axis edge bounds + lease/timeout cleanup\n",checks);}
