#include "snapshot/firmware/vision/roi_continuous.c"
#include "snapshot/firmware/vision/roi_opt_instrumented.c"
size_t ws_size(void){return sizeof(pen_continuous_workspace);}
void trace_reset(void){memset(&trace,0,sizeof trace);}
void trace_get(diagnostic_trace *out){*out=trace;}
int extract_points(const uint8_t *g,pen_continuous_workspace *ws,double *points,unsigned *meta){
 unsigned sizes[2]={96,80};uint16_t ec=0,ep=0;
 for(unsigned i=0;i<2;i++){
  unsigned side=sizes[i],left=(200-side)/2;
  int n=prepare(g,200,left,left,side,ws,&ec,&ep);
  meta[0]=side;meta[1]=left;meta[2]=ec;meta[3]=ep;meta[4]=(unsigned)n;
  if(n<36)return -2;
  if(n<=100){
   int detected=detect(ws->crop,side,side,side,ws->core.points,&ws->core);
   if(detected<0)return -2;
   for(int j=0;j<detected;j++){points[2*j]=ws->core.points[j].x;points[2*j+1]=ws->core.points[j].y;}
   return detected;
  }
 }
 return -2;
}
