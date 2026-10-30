#include "roi_opt.c"
size_t audit_ws_size(void){return sizeof(pen_roi_workspace);}
int audit_detect(const uint8_t*g,unsigned w,unsigned h,pen_roi_workspace*ws){return detect(g,w,h,w,ws->points,ws);}
