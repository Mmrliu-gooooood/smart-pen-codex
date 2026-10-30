/* Benchmark-only, serial/nonreentrant diagnostic capture. Production sources unchanged.
 * Link wrapping captures output only. Its copying overhead is inside wrapper timing. */
#include "trace.h"
#include <string.h>
static pen_roi_refine_diagnostics last;
static unsigned calls;
unsigned bench_trace_calls(void){return calls;}
void bench_trace_reset(void){memset(&last,0,sizeof last);calls=0;}
pen_roi_refine_diagnostics bench_trace_get(void){return last;}
int __real_pen_roi_decode_refined_transform(const uint8_t*,size_t,unsigned,unsigned,unsigned,
 const pen_roi_config*,pen_roi_workspace*,pen_roi_refine_seed*,pen_roi_opt_result*,pen_roi_grid_transform*,pen_roi_refine_diagnostics*);
int __wrap_pen_roi_decode_refined_transform(const uint8_t *g,size_t l,unsigned w,unsigned h,unsigned s,
 const pen_roi_config *c,pen_roi_workspace *ws,pen_roi_refine_seed *seeds,pen_roi_opt_result *o,
 pen_roi_grid_transform *t,pen_roi_refine_diagnostics *d){
 calls++;
 int rc=__real_pen_roi_decode_refined_transform(g,l,w,h,s,c,ws,seeds,o,t,d);
 if(d)last=*d;
 return rc;
}
