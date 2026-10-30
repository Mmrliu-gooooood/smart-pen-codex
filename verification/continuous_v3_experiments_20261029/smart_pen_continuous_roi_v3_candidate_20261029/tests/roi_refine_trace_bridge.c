/* Host-test link wrapper only: never compiled into target decoder. */
#include "../firmware/vision/roi_continuous.h"
#include <string.h>
static pen_roi_refine_diagnostics last;
size_t ws_size(void){return sizeof(pen_continuous_workspace);}
size_t result_size(void){return sizeof(pen_continuous_result);}
void reset_last_refine_stats(void){memset(&last,0,sizeof last);}
void get_last_refine_stats(pen_roi_refine_diagnostics *d){*d=last;}
int __real_pen_roi_decode_refined_transform(const uint8_t*,size_t,unsigned,unsigned,unsigned,
 const pen_roi_config*,pen_roi_workspace*,pen_roi_refine_seed*,pen_roi_opt_result*,pen_roi_grid_transform*,pen_roi_refine_diagnostics*);
int __wrap_pen_roi_decode_refined_transform(const uint8_t *g,size_t l,unsigned w,unsigned h,unsigned s,
 const pen_roi_config *c,pen_roi_workspace *ws,pen_roi_refine_seed *seeds,pen_roi_opt_result *o,
 pen_roi_grid_transform *t,pen_roi_refine_diagnostics *d){
 int rc=__real_pen_roi_decode_refined_transform(g,l,w,h,s,c,ws,seeds,o,t,d);
 if(d)last=*d;
 return rc;
}
