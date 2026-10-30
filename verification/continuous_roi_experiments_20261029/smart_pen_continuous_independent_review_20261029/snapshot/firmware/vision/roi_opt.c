/* Small-ROI implementation informed by the original PC detector/grid fitter:
 * weighted connected components, periodic lattice phase and residual directions.
 * Source checkpoint and differences: docs/software/roi_vision.md.
 * Codec retains Christoph Heindl's MIT license in ../codec/LICENSE.microdots.
 */
#include "roi_opt.h"
#include "../codec/anoto.h"
#include <math.h>

#include <string.h>
#define DOTS 128
#define PI 3.14159265358979323846
#define SIDE 40

typedef pen_roi_opt_point point;
typedef struct { pen_roi_opt_result result; pen_roi_grid_transform transform; } fit;
/* Fail closed on oversized/edge-touching/elongated components: no inpainting. */
static int detect(const uint8_t *g,unsigned w,unsigned h,unsigned stride,point *p,pen_roi_workspace *ws) {
 unsigned lo=255,hi=0;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
  unsigned v=g[(size_t)y*stride+x];if(v<lo)lo=v;if(v>hi)hi=v;
 }
 if(hi-lo<60)return -1;
 unsigned threshold=(lo+hi)/2,n=0;
 uint8_t *seen=ws->seen;memset(seen,0,((size_t)w*h+7)/8);
 uint32_t *queue=ws->queue;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
  unsigned pos=y*w+x;
  if((seen[pos>>3]&(1u<<(pos&7)))||g[(size_t)y*stride+x]>=threshold)continue;
  unsigned head=0,tail=1,minx=x,maxx=x,miny=y,maxy=y;
  double sx=0,sy=0,weight=0;queue[0]=pos;seen[pos>>3]|=(uint8_t)(1u<<(pos&7));
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
    if(!(seen[z>>3]&(1u<<(z&7)))&&g[(size_t)(unsigned)yy*stride+(unsigned)xx]<threshold){
     if(tail==256){return -1;}
     seen[z>>3]|=(uint8_t)(1u<<(z&7));queue[tail++]=z;
    }
   }
  }
  if(tail<3)continue; /* isolated sensor speckles are not dots */
  unsigned bw=maxx-minx+1,bh=maxy-miny+1;
  if(minx==0||miny==0||maxx==w-1||maxy==h-1||bw>2*bh||bh>2*bw||tail>100||n==DOTS){return -1;}
  p[n].x=sx/weight;p[n++].y=sy/weight;
 }
 return n>=36?(int)n:-1;
}
/* Fit phase from the first circular moment: displaced dots do not require
 * their cell indices or image origin to be known. */
static double phase(const double *v,int n){
 double c=0,s=0;for(int i=0;i<n;i++){c+=cos(2*PI*v[i]);s+=sin(2*PI*v[i]);}
 return atan2(s,c)/(2*PI);
}
static double residual(double v){return v-round(v);}

/* One current-frame model hypothesis. All arrays live in caller workspace. */
static int candidate(pen_roi_workspace *ws,int n,const pen_roi_config *cfg,
 double pitch,double angle,double ratio,fit *fitted){
 pen_roi_opt_result *candidate=&fitted->result;
 double cs=cos(angle*PI/180),sn=sin(angle*PI/180);
 double *u=ws->u,*v=ws->v,*xx=ws->xx,*yy=ws->yy;
 for(int i=0;i<n;i++){
  u[i]=(ws->points[i].x*cs+ws->points[i].y*sn)/pitch;
  v[i]=(-ws->points[i].x*sn+ws->points[i].y*cs)/(pitch*ratio);
 }
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
   uint8_t *dirs=ws->dirs;
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
   if(!good||maxx-minx>=SIDE||maxy-miny>=SIDE)return 0;
   int *grid=ws->grid;for(int i=0;i<SIDE*SIDE;i++)grid[i]=-1;
   for(int i=0;i<n;i++){
    int z=((int)yy[i]-miny)*SIDE+(int)xx[i]-minx;
    if(grid[z]>=0){good=0;break;}grid[z]=dirs[i];
   }
   if(!good)return 0;
   int windows=0,origin_x=0,origin_y=0,firstcol=0,firstrow=0;uint16_t firstx=0,firsty=0;uint8_t firstd[36];
   for(int row=0;row<=maxy-miny-5;row++)for(int col=0;col<=maxx-minx-5;col++){
    uint8_t d[36];int complete=1;
    for(int r=0;r<6;r++)for(int c=0;c<6;c++){
     int q=grid[(row+r)*SIDE+col+c];if(q<0)complete=0;d[r*6+c]=(uint8_t)q;
    }
    uint16_t x,y;if(!complete||pen_anoto_decode(d,cfg->paper_width,cfg->paper_height,cfg->section_u,cfg->section_v,&x,&y))continue;
    /* All windows must share one coordinate translation. */
    if(windows&&((int)x-col!=origin_x||(int)y-row!=origin_y))return PEN_ROI_AMBIGUOUS;
    if(!windows){origin_x=(int)x-col;origin_y=(int)y-row;firstx=x;firsty=y;firstcol=col;firstrow=row;memcpy(firstd,d,36);}
    windows++;
   }
   if(!windows)return 0;
   candidate->decoded.x=firstx;candidate->decoded.y=firsty;
   candidate->decoded.dots=(uint16_t)n;candidate->decoded.windows=(uint16_t)windows;
   candidate->decoded.pitch_px=(float)pitch;candidate->decoded.angle_deg=(float)angle;
   candidate->decoded.residual_cells=(float)sqrt(error/n);
   memcpy(candidate->decoded.directions,firstd,36);candidate->y_scale=(float)ratio;
   fitted->transform.x_dx=pitch*cs;fitted->transform.x_dy=pitch*sn;
   fitted->transform.y_dx=-pitch*ratio*sn;fitted->transform.y_dy=pitch*ratio*cs;
   fitted->transform.origin_x=(ox+minx+firstcol)*fitted->transform.x_dx+(oy+miny+firstrow)*fitted->transform.y_dx;
   fitted->transform.origin_y=(ox+minx+firstcol)*fitted->transform.x_dy+(oy+miny+firstrow)*fitted->transform.y_dy;
   return 1;
}

static int merge_candidate(fit *best,const fit *c,int *found){
 if(*found&&(best->result.decoded.x!=c->result.decoded.x||best->result.decoded.y!=c->result.decoded.y))return PEN_ROI_AMBIGUOUS;
 if(!*found||c->result.decoded.residual_cells<best->result.decoded.residual_cells)*best=*c;
 *found=1;return 0;
}
int pen_roi_decode_opt_transform(const uint8_t *g,size_t length,unsigned w,unsigned h,unsigned stride,
 const pen_roi_config *cfg,pen_roi_workspace *ws,pen_roi_prior *prior,pen_roi_opt_result *out,pen_roi_grid_transform *transform){
 pen_roi_prior hint={0,0,0,0};
 if(prior){hint=*prior;memset(prior,0,sizeof *prior);}
 if(!g||!cfg||!out||!ws||w<16||h<16||w>256||h>256||stride<w||
    (size_t)(h-1)>(SIZE_MAX-w)/stride||length<(size_t)(h-1)*stride+w||
    cfg->paper_width<6||cfg->paper_height<6||cfg->paper_width>4096||cfg->paper_height>4096||
    cfg->section_u>=63||cfg->section_v>=63)return PEN_ROI_ARGUMENT;
 int n=detect(g,w,h,stride,ws->points,ws);
 if(n<0)return PEN_ROI_DETECTION;
 fit best,c;memset(&best,0,sizeof best);memset(&c,0,sizeof c);
 int found=0;uint32_t tested=0;uint8_t warm=0;
 if(hint.valid==1&&isfinite(hint.pitch_px)&&isfinite(hint.angle_deg)&&isfinite(hint.y_scale)&&
    hint.pitch_px>=8&&hint.pitch_px<=32&&fabs(hint.angle_deg)<=60&&hint.y_scale>=.6f&&hint.y_scale<=1.4f){
  for(int a=-1;a<=1;a++)for(int p=-1;p<=1;p++)for(int r=-1;r<=1;r++){
   double pitch=hint.pitch_px+p*.25,angle=hint.angle_deg+a,ratio=hint.y_scale+r*.025;
   if(pitch<8||pitch>32||angle < -60||angle>60||ratio<.6||ratio>1.4)continue;
   tested++;int rc=candidate(ws,n,cfg,pitch,angle,ratio,&c);
   if(rc<0)return rc;
   if(rc&&merge_candidate(&best,&c,&found))return PEN_ROI_AMBIGUOUS;
  }
  if(found)warm=1;
 }
 if(!found){
  for(int a=-60;a<=60;a+=2)for(int p=16;p<=64;p++)for(int r=6;r<=14;r++){
   tested++;int rc=candidate(ws,n,cfg,p*.5,(double)a,r*.1,&c);
   if(rc<0)return rc;
   if(rc&&merge_candidate(&best,&c,&found))return PEN_ROI_AMBIGUOUS;
  }
 }
 if(!found)return PEN_ROI_NO_GRID;
 best.result.candidates=tested;best.result.used_warm_start=warm;*out=best.result;
 if(transform)*transform=best.transform;
 if(prior){prior->valid=1;prior->pitch_px=best.result.decoded.pitch_px;prior->angle_deg=best.result.decoded.angle_deg;prior->y_scale=best.result.y_scale;}
 return PEN_ROI_OK;
}

/* Backwards-compatible strict-edge API: no selection/filtering is introduced. */
int pen_roi_decode_opt(const uint8_t *g,size_t length,unsigned w,unsigned h,unsigned stride,
 const pen_roi_config *cfg,pen_roi_workspace *ws,pen_roi_prior *prior,pen_roi_opt_result *out){
 return pen_roi_decode_opt_transform(g,length,w,h,stride,cfg,ws,prior,out,NULL);
}
