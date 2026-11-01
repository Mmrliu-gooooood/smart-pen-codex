/* Host diagnostic linker wrapper. Original decoder sources unchanged.
 * Capture only dimensions/diagnostics passed through to genuine function. */
#include "roi_continuous.h"
#include <string.h>
size_t ws_size(void){return sizeof(pen_continuous_workspace);}
size_t result_size(void){return sizeof(pen_continuous_result);}
#ifdef TRACE
static unsigned calls,width,height,stride;
static pen_roi_refine_diagnostics last;
void reset_trace(void){calls=width=height=stride=0;memset(&last,0,sizeof last);}
void trace(unsigned *p){p[0]=calls;p[1]=width;p[2]=height;p[3]=stride;p[4]=last.cold_candidates;p[5]=last.seeds;p[6]=last.iterations;p[7]=last.refined_models;}
int __real_pen_roi_decode_refined_transform(const uint8_t*,size_t,unsigned,unsigned,unsigned,const pen_roi_config*,pen_roi_workspace*,pen_roi_refine_seed*,pen_roi_opt_result*,pen_roi_grid_transform*,pen_roi_refine_diagnostics*);
int __wrap_pen_roi_decode_refined_transform(const uint8_t*g,size_t n,unsigned w,unsigned h,unsigned s,const pen_roi_config*c,pen_roi_workspace*ws,pen_roi_refine_seed*seeds,pen_roi_opt_result*o,pen_roi_grid_transform*t,pen_roi_refine_diagnostics*d){
 calls++;width=w;height=h;stride=s;
 int rc=__real_pen_roi_decode_refined_transform(g,n,w,h,s,c,ws,seeds,o,t,d);
 if(d)last=*d;
 return rc;
}
#endif
