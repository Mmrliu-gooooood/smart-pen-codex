#include "roi_continuous.h"
#include <math.h>
#include <string.h>

_Static_assert(sizeof(pen_continuous_workspace)<=32768,"continuous workspace budget");
/* Reuses core traversal scratch, never its 128-point array for a dense crop.
 * Each dark pixel is queued at most once. Huge/connected ink fails boundedly. */
static int prepare(const uint8_t *g,unsigned stride,unsigned left,unsigned top,unsigned side,
 pen_continuous_workspace *ws,uint16_t *edge_components,uint16_t *edge_pixels){
 unsigned lo=255,hi=0;
 for(unsigned y=0;y<side;y++)for(unsigned x=0;x<side;x++){
  unsigned v=g[(size_t)(top+y)*stride+left+x];ws->crop[y*side+x]=(uint8_t)v;
  if(v<lo)lo=v;
  if(v>hi)hi=v;
 }
 if(hi-lo<60)return -1;
 unsigned threshold=(lo+hi)/2,n=0;uint8_t *seen=ws->core.seen;
 uint32_t *queue=ws->core.queue;
 memset(seen,0,((size_t)side*side+7)/8);*edge_components=0;*edge_pixels=0;
 for(unsigned y=0;y<side;y++)for(unsigned x=0;x<side;x++){
  unsigned pos=y*side+x;
  if((seen[pos>>3]&(1u<<(pos&7)))||ws->crop[pos]>=threshold)continue;
  unsigned head=0,tail=1,minx=x,maxx=x,miny=y,maxy=y;
  queue[0]=pos;seen[pos>>3]|=(uint8_t)(1u<<(pos&7));
  while(head<tail){
   unsigned q=queue[head++],cx=q%side,cy=q/side;
   if(cx<minx)minx=cx;
   if(cx>maxx)maxx=cx;
   if(cy<miny)miny=cy;
   if(cy>maxy)maxy=cy;
   for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
    int xx=(int)cx+dx,yy=(int)cy+dy;
    if(xx<0||yy<0||xx>=(int)side||yy>=(int)side)continue;
    unsigned z=(unsigned)yy*side+(unsigned)xx;
    if(!(seen[z>>3]&(1u<<(z&7)))&&ws->crop[z]<threshold){
     if(tail==256)return -1;
     seen[z>>3]|=(uint8_t)(1u<<(z&7));queue[tail++]=z;
    }
   }
  }
  unsigned bw=maxx-minx+1,bh=maxy-miny+1;
  if(minx==0||miny==0||maxx==side-1||maxy==side-1){
   /* Profile-C 5..7mm/200px point-size envelope, not an ink classifier.
    * Reject deep/long boundary ink; dot-sized fragments remain indistinguishable.
    * Never infer paper coordinates or a dot radius from ground truth. */
   if(tail>PEN_CONTINUOUS_EDGE_MAX_PIXELS||bw>PEN_CONTINUOUS_EDGE_MAX_EXTENT||
      bh>PEN_CONTINUOUS_EDGE_MAX_EXTENT||
      ((minx==0||maxx==side-1)&&bw>PEN_CONTINUOUS_EDGE_MAX_DEPTH)||
      ((miny==0||maxy==side-1)&&bh>PEN_CONTINUOUS_EDGE_MAX_DEPTH))return -1;
   for(unsigned i=0;i<tail;i++)ws->crop[queue[i]]=(uint8_t)hi;
   (*edge_components)++;*edge_pixels=(uint16_t)(*edge_pixels+tail);
  }else if(tail>=3){
   if(tail>100||bw>2*bh||bh>2*bw)return -1;
   n++;
  }
 }
 return (int)n;
}
int pen_roi_decode_continuous(const uint8_t *g,size_t length,unsigned w,unsigned h,unsigned stride,
 const pen_roi_config *cfg,pen_continuous_workspace *ws,pen_continuous_result *out){
 if(!g||!cfg||!ws||!out||w<96||h<96||w>256||h>256||stride<w||
    (size_t)(h-1)>(SIZE_MAX-w)/stride||length<(size_t)(h-1)*stride+w||
    cfg->paper_width<6||cfg->paper_height<6||cfg->paper_width>4096||cfg->paper_height>4096||
    cfg->section_u>=63||cfg->section_v>=63)return PEN_ROI_ARGUMENT;
 pen_continuous_result result;memset(&result,0,sizeof result);
 const unsigned sizes[2]={96,80};unsigned side=0,left=0,top=0;int selected=0;
 for(unsigned i=0;i<2;i++){
  side=sizes[i];left=(w-side)/2;top=(h-side)/2;result.crop_attempts++;
  int n=prepare(g,stride,left,top,side,ws,&result.edge_components,&result.edge_pixels);
  if(n<36)return PEN_ROI_DETECTION;
  if((unsigned)n<=PEN_CONTINUOUS_ROI_MAX_DOTS){selected=1;break;}
 }
 if(!selected)return PEN_ROI_DETECTION;
 pen_roi_grid_transform t;
 int rc=pen_roi_decode_opt_transform(ws->crop,(size_t)side*side,side,side,side,cfg,
  &ws->core,NULL,&result.roi,&t);
 if(rc)return rc;
 /* Core recomputes threshold on the filtered pixels. Never allow its result
  * to exceed the stricter wrapper policy, even if threshold extrema changed. */
 if(result.roi.decoded.dots>PEN_CONTINUOUS_ROI_MAX_DOTS)return PEN_ROI_DETECTION;
 double *a=result.paper_to_frame,*b=result.frame_to_paper;
 a[0]=t.x_dx;a[1]=t.y_dx;a[3]=t.x_dy;a[4]=t.y_dy;
 a[2]=t.origin_x+left-a[0]*result.roi.decoded.x-a[1]*result.roi.decoded.y;
 a[5]=t.origin_y+top-a[3]*result.roi.decoded.x-a[4]*result.roi.decoded.y;
 double det=a[0]*a[4]-a[1]*a[3];
 if(!isfinite(det)||fabs(det)<1)return PEN_ROI_NO_GRID;
 b[0]=a[4]/det;b[1]=-a[1]/det;b[3]=-a[3]/det;b[4]=a[0]/det;
 b[2]=-b[0]*a[2]-b[1]*a[5];b[5]=-b[3]*a[2]-b[4]*a[5];
 result.left=(uint16_t)left;result.top=(uint16_t)top;
 result.width=(uint16_t)side;result.height=(uint16_t)side;
 *out=result;return PEN_ROI_OK;
}
