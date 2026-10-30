#include "bridge.c"
int validate_estimated_model(pen_continuous_workspace *ws,int n,const pen_roi_config *cfg,
 double pitch,double angle,double ratio,pen_roi_opt_result *out,pen_roi_grid_transform *transform){
 fit f;memset(&f,0,sizeof f);
 int rc=candidate(&ws->core,n,cfg,pitch,angle,ratio,&f);
 if(rc==1){*out=f.result;*transform=f.transform;}
 return rc;
}
