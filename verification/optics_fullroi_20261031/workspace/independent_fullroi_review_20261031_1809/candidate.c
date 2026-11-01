#include "candidate.h"
#include <string.h>
extern int pen_roi_active_decode_opt(const uint8_t *,size_t,unsigned,unsigned,unsigned,const pen_roi_config *,pen_roi_workspace *,pen_roi_prior *,pen_roi_opt_result *);
size_t candidate_workspace_size(void){return sizeof(candidate_workspace);}
size_t candidate_result_size(void){return sizeof(pen_roi_opt_result);}
size_t candidate_diagnostics_size(void){return sizeof(pen_roi_refine_diagnostics);}
static int disjoint(const void *const ptrs[],const size_t sizes[],size_t count){
 for(size_t i=0;i<count;i++){
  if(!ptrs[i]||!sizes[i])continue;
  uintptr_t a=(uintptr_t)ptrs[i];
  if(sizes[i]-1>UINTPTR_MAX-a)return 0;
  uintptr_t ae=a+sizes[i]-1;
  for(size_t j=0;j<i;j++){
   if(!ptrs[j]||!sizes[j])continue;
   uintptr_t b=(uintptr_t)ptrs[j],be=b+sizes[j]-1;
   if(a<=be&&b<=ae)return 0;
  }
 }
 return 1;
}
int candidate_decode(const uint8_t *g,size_t n,unsigned w,unsigned h,unsigned s,const pen_roi_config *cfg,candidate_workspace *ws,pen_roi_opt_result *out,pen_roi_refine_diagnostics *d){
 const void *ptrs[]={g,cfg,ws,out,d};
 const size_t sizes[]={n,sizeof *cfg,sizeof *ws,sizeof *out,sizeof *d};
 /* Aliasing/range-overflow fails before writes, including diagnostic reset. */
 if(!disjoint(ptrs,sizes,5))return PEN_ROI_ARGUMENT;
#if CANDIDATE_ENABLE_REFINEMENT
 return pen_roi_decode_refined_transform(g,n,w,h,s,cfg,ws?&ws->core:NULL,ws?ws->seeds:NULL,out,NULL,d);
#else
 if(d)memset(d,0,sizeof *d);
 return pen_roi_active_decode_opt(g,n,w,h,s,cfg,ws?&ws->core:NULL,NULL,out);
#endif
}
