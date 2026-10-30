/* Small-ROI implementation informed by the original PC detector/grid fitter:
 * weighted connected components, periodic lattice phase and residual directions.
 * Source checkpoint and differences: docs/software/roi_vision.md.
 * Codec retains Christoph Heindl's MIT license in ../codec/LICENSE.microdots.
 */
#include "roi.h"
#include "../codec/anoto.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#define DOTS 128
#define PI 3.14159265358979323846
#define SIDE 40

typedef struct { double x,y; } point;
/* Fail closed on oversized/edge-touching/elongated components: no inpainting. */
static int detect(const uint8_t *g,unsigned w,unsigned h,unsigned stride,point *p) {
 unsigned lo=255,hi=0;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
  unsigned v=g[(size_t)y*stride+x];if(v<lo)lo=v;if(v>hi)hi=v;
 }
 if(hi-lo<60)return -1;
 unsigned threshold=(lo+hi)/2,n=0;
 uint8_t *seen=calloc((size_t)w*h,1);if(!seen)return -2;
 uint32_t queue[256];
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
  unsigned pos=y*w+x;
  if(seen[pos]||g[(size_t)y*stride+x]>=threshold)continue;
  unsigned head=0,tail=1,minx=x,maxx=x,miny=y,maxy=y;
  double sx=0,sy=0,weight=0;queue[0]=pos;seen[pos]=1;
  while(head<tail){
   unsigned q=queue[head++],cx=q%w,cy=q/w;
   unsigned mass=hi-g[(size_t)cy*stride+cx];sx+=cx*mass;sy+=cy*mass;weight+=mass;
   if(cx<minx)minx=cx;
   if(cx>maxx)maxx=cx;
   if(cy<miny)miny=cy;
   if(cy>maxy)maxy=cy;
   for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
    int xx=(int)cx+dx,yy=(int)cy+dy;
    if(xx<0||yy<0||xx>=(int)w||yy>=(int)h)continue;
    unsigned z=(unsigned)yy*w+(unsigned)xx;
    if(!seen[z]&&g[(size_t)(unsigned)yy*stride+(unsigned)xx]<threshold){
     if(tail==256){free(seen);return -1;}
     seen[z]=1;queue[tail++]=z;
    }
   }
  }
  if(tail<3)continue; /* isolated sensor speckles are not dots */
  unsigned bw=maxx-minx+1,bh=maxy-miny+1;
  if(minx==0||miny==0||maxx==w-1||maxy==h-1||bw>2*bh||bh>2*bw||tail>100||n==DOTS){free(seen);return -1;}
  p[n].x=sx/weight;p[n++].y=sy/weight;
 }
 free(seen);return n>=36?(int)n:-1;
}
/* Fit phase from the first circular moment: displaced dots do not require
 * their cell indices or image origin to be known. */
static double phase(const double *v,int n){
 double c=0,s=0;for(int i=0;i<n;i++){c+=cos(2*PI*v[i]);s+=sin(2*PI*v[i]);}
 return atan2(s,c)/(2*PI);
}
static double residual(double v){return v-round(v);}

int pen_roi_decode(const uint8_t *g,size_t length,unsigned w,unsigned h,unsigned stride,
 const pen_roi_config *cfg,pen_roi_result *out){
 if(!g||!cfg||!out||w<16||h<16||w>256||h>256||stride<w||
    (size_t)(h-1)>(SIZE_MAX-w)/stride||length<(size_t)(h-1)*stride+w||
    cfg->paper_width<6||cfg->paper_height<6||cfg->paper_width>4096||cfg->paper_height>4096||
    cfg->section_u>=63||cfg->section_v>=63)return PEN_ROI_ARGUMENT;
 point dots[DOTS];int n=detect(g,w,h,stride,dots);
 if(n<0)return n==-2?PEN_ROI_MEMORY:PEN_ROI_DETECTION;
 pen_roi_result best;memset(&best,0,sizeof best);double best_error=1e9;int found=0;
 /* Bounded acquisition search. This is host-reference code, NOT a measured
  * real-time ESP32 implementation. No unbounded RANSAC retry loop. */
 for(int angle=-20;angle<=20;angle++){
  double cs=cos(angle*PI/180),sn=sin(angle*PI/180),xx[DOTS],yy[DOTS];
  for(int pi=32;pi<=128;pi++){
   double pitch=pi*.25,u[DOTS],v[DOTS];
   for(int i=0;i<n;i++){u[i]=(dots[i].x*cs+dots[i].y*sn)/pitch;v[i]=(-dots[i].x*sn+dots[i].y*cs)/pitch;}
   double ox=phase(u,n),oy=phase(v,n);
   /* Remove phase bias from unequal counts of UP/LEFT/RIGHT/DOWN. Once the
    * dominant direction is known, the perpendicular residual should be 0. */
   for(int iter=0;iter<3;iter++){
    double sx=0,sy=0;int nx=0,ny=0;
    for(int i=0;i<n;i++){
     double dx=residual(u[i]-ox),dy=residual(v[i]-oy);
     if(fabs(dx)>fabs(dy)){sy+=dy;ny++;}else{sx+=dx;nx++;}
    }
    if(nx)ox+=sx/nx;
    if(ny)oy+=sy/ny;
   }
   int minx=1000,miny=1000,maxx=-1000,maxy=-1000,good=1;double error=0;
   uint8_t dirs[DOTS];
   for(int i=0;i<n;i++){
    xx[i]=round(u[i]-ox);yy[i]=round(v[i]-oy);
    double dx=u[i]-ox-xx[i],dy=v[i]-oy-yy[i];
    double ax=fabs(dx),ay=fabs(dy),major=fmax(ax,ay),minor=fmin(ax,ay);
    if(major<.10||major>.30||minor>.065){good=0;break;}
    error+=minor*minor+(major-1.0/6)*(major-1.0/6);
    dirs[i]=ax>ay?(dx<0?1:2):(dy<0?0:3);
    int ix=(int)xx[i],iy=(int)yy[i];
    if(ix<minx)minx=ix;
    if(ix>maxx)maxx=ix;
    if(iy<miny)miny=iy;
    if(iy>maxy)maxy=iy;
   }
   if(!good||maxx-minx>=SIDE||maxy-miny>=SIDE)continue;
   int grid[SIDE*SIDE];for(int i=0;i<SIDE*SIDE;i++)grid[i]=-1;
   for(int i=0;i<n;i++){
    int z=((int)yy[i]-miny)*SIDE+(int)xx[i]-minx;
    if(grid[z]>=0){good=0;break;}grid[z]=dirs[i];
   }
   if(!good)continue;
   int windows=0,origin_x=0,origin_y=0;uint16_t firstx=0,firsty=0;uint8_t firstd[36];
   for(int row=0;row<=maxy-miny-5;row++)for(int col=0;col<=maxx-minx-5;col++){
    uint8_t d[36];int complete=1;
    for(int r=0;r<6;r++)for(int c=0;c<6;c++){
     int q=grid[(row+r)*SIDE+col+c];if(q<0)complete=0;d[r*6+c]=(uint8_t)q;
    }
    uint16_t x,y;if(!complete||pen_anoto_decode(d,cfg->paper_width,cfg->paper_height,cfg->section_u,cfg->section_v,&x,&y))continue;
    /* All windows must share one coordinate translation. */
    if(windows&&((int)x-col!=origin_x||(int)y-row!=origin_y))return PEN_ROI_AMBIGUOUS;
    if(!windows){origin_x=(int)x-col;origin_y=(int)y-row;firstx=x;firsty=y;memcpy(firstd,d,36);}
    windows++;
   }
   if(!windows)continue;
   /* Distinct lattice candidates must agree on the selected paper origin. */
   if(found&&(best.x!=firstx||best.y!=firsty))return PEN_ROI_AMBIGUOUS;
   found=1;
   if(error<best_error){best_error=error;best.x=firstx;best.y=firsty;best.dots=(uint16_t)n;best.windows=(uint16_t)windows;best.pitch_px=(float)pitch;best.angle_deg=(float)angle;best.residual_cells=(float)sqrt(error/n);memcpy(best.directions,firstd,36);}
  }
 }
 if(!found)return PEN_ROI_NO_GRID;
 *out=best;return PEN_ROI_OK;
}
