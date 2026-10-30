/* Separate experimental translation unit. Reuse frozen legacy implementation
 * verbatim for phase/candidate initialization, not a changed old ABI. Link this
 * TU OR roi_opt.c, never both. Existing V3 builds still compile roi_opt.c. */
#include "roi_opt.c"
#include "roi_projective.h"
_Static_assert(sizeof(pen_projective_workspace)<=40960,"V4 workspace bound");
_Static_assert(PEN_PROJECTIVE_MAX_SEEDS>0&&PEN_PROJECTIVE_MAX_SEEDS<=256,"V4 seed bound");
int pen_projective_map_v4(const double h[9],double x,double y,double *u,double *v){
 if(!h||!u||!v||!isfinite(x)||!isfinite(y))return 0;
 for(int i=0;i<9;i++)if(!isfinite(h[i]))return 0;
 double z=h[6]*x+h[7]*y+h[8];if(!isfinite(z)||fabs(z)<1e-9)return 0;
 double a=(h[0]*x+h[1]*y+h[2])/z,b=(h[3]*x+h[4]*y+h[5])/z;
 if(!isfinite(a)||!isfinite(b))return 0;
 *u=a;*v=b;return 1;
}
static int inverse(const double a[9],double b[9]){
 double c[9]={a[4]*a[8]-a[5]*a[7],a[2]*a[7]-a[1]*a[8],a[1]*a[5]-a[2]*a[4],a[5]*a[6]-a[3]*a[8],a[0]*a[8]-a[2]*a[6],a[2]*a[3]-a[0]*a[5],a[3]*a[7]-a[4]*a[6],a[1]*a[6]-a[0]*a[7],a[0]*a[4]-a[1]*a[3]};
 double d=a[0]*c[0]+a[1]*c[3]+a[2]*c[6];if(!isfinite(d)||fabs(d)<1e-9)return 0;
 for(int i=0;i<9;i++){b[i]=c[i]/d;if(!isfinite(b[i]))return 0;}return 1;
}
/* Fixed 8x8 normal solve with pivot/conditioning rejection, no dynamic memory. */
static int solve(double a[8][9],double h[9]){
 double scale=0;for(int i=0;i<8;i++)if(fabs(a[i][i])>scale)scale=fabs(a[i][i]);
 if(!isfinite(scale)||scale==0)return 0;
 for(int i=0;i<8;i++){
  int p=i;for(int j=i+1;j<8;j++)if(fabs(a[j][i])>fabs(a[p][i]))p=j;
  if(fabs(a[p][i])<1e-10*scale)return 0;
  for(int k=i;k<9;k++){double t=a[i][k];a[i][k]=a[p][k];a[p][k]=t;}
  double d=a[i][i];for(int k=i;k<9;k++)a[i][k]/=d;
  for(int j=0;j<8;j++)if(j!=i){double f=a[j][i];for(int k=i;k<9;k++)a[j][k]-=f*a[i][k];}
 }
 for(int i=0;i<8;i++){h[i]=a[i][8];if(!isfinite(h[i]))return 0;}h[8]=1;return 1;
}
static int geometry_valid(const double h[9]){
 double b[9];if(!inverse(h,b))return 0;
 double lo=1e9,hi=-1e9;
 for(int y=-40;y<=40;y+=80)for(int x=-40;x<=40;x+=80){double d=b[6]*x+b[7]*y+b[8];if(d<lo)lo=d;if(d>hi)hi=d;}
 if(lo<=0||hi/lo>4)return 0;
 double x,y,xx,xy,yx,yy;
 if(!pen_projective_map_v4(h,0,0,&x,&y)||!pen_projective_map_v4(h,1,0,&xx,&xy)||!pen_projective_map_v4(h,0,1,&yx,&yy))return 0;
 double ax=xx-x,ay=xy-y,bx=yx-x,by=yy-y,p=hypot(ax,ay),q=hypot(bx,by);
 return ax*by-ay*bx>0&&p>=8&&p<=32&&q>=3&&q<=45&&q/p>=.35&&q/p<=1.5&&fabs(atan2(ay,ax)*180/PI)<=62;
}
/* Small-ellipse adaptation is confined to this experimental path. Legacy
 * detector and wrapper are unchanged. Retain >=3 threshold pixels; subpixel
 * components are not fabricated. Long/large ink and capacity overflow reject. */
static int extract(const uint8_t*g,unsigned stride,unsigned left,unsigned top,pen_projective_workspace*w,pen_projective_diagnostics*d){
 unsigned lo=255,hi=0;for(unsigned y=0;y<80;y++)for(unsigned x=0;x<80;x++){unsigned v=g[(size_t)(top+y)*stride+left+x];w->crop[y*80+x]=(uint8_t)v;if(v<lo)lo=v;if(v>hi)hi=v;}
 if(hi-lo<60)return -1;
 unsigned threshold=(lo+hi)/2,n=0;memset(w->core.seen,0,800);
 for(unsigned pos=0;pos<6400;pos++){
  if((w->core.seen[pos>>3]&(1u<<(pos&7)))||w->crop[pos]>=threshold)continue;
  unsigned head=0,tail=1,minx=pos%80,maxx=minx,miny=pos/80,maxy=miny;double sx=0,sy=0,mass=0;
  w->core.queue[0]=pos;w->core.seen[pos>>3]|=(uint8_t)(1u<<(pos&7));d->components++;
  while(head<tail){unsigned q=w->core.queue[head++],x=q%80,y=q/80;unsigned v=hi-w->crop[q];sx+=x*v;sy+=y*v;mass+=v;if(x<minx)minx=x;
  if(x>maxx)maxx=x;
  if(y<miny)miny=y;
  if(y>maxy)maxy=y;
   for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int xx=(int)x+dx,yy=(int)y+dy;if(xx<0||yy<0||xx>=80||yy>=80)continue;unsigned z=(unsigned)yy*80+(unsigned)xx;
    if(!(w->core.seen[z>>3]&(1u<<(z&7)))&&w->crop[z]<threshold){if(tail==256){d->overflow=1;return -1;}w->core.queue[tail++]=z;w->core.seen[z>>3]|=(uint8_t)(1u<<(z&7));}}
  }
  unsigned bw=maxx-minx+1,bh=maxy-miny+1;
  if(minx==0||miny==0||maxx==79||maxy==79){if(tail>24||bw>6||bh>6||((minx==0||maxx==79)&&bw>4)||((miny==0||maxy==79)&&bh>4))return -1;continue;}
  if(tail<3)continue;
  if(tail>24||bw>6||bh>6||bw>4*bh||bh>4*bw)return -1;
  if(n==128){d->overflow=1;return -1;}w->all[n].x=sx/mass-39.5;w->all[n++].y=sy/mass-39.5;
 }
 d->retained=n;
 /* Stable bounded insertion sort by central distance: acquisition starts with
  * nearest36, progressive all-point fit never drops retained outliers. */
 for(unsigned i=1;i<n;i++){point p=w->all[i];unsigned j=i;double r=p.x*p.x+p.y*p.y;while(j&&w->all[j-1].x*w->all[j-1].x+w->all[j-1].y*w->all[j-1].y>r){w->all[j]=w->all[j-1];j--;}w->all[j]=p;}
 return n>=36?(int)n:-1;
}
static int refine_projective(pen_projective_workspace*w,int n,const pen_roi_refine_seed*s,double h[9],pen_projective_diagnostics*d){
 double cs=cos(s->angle*PI/180),sn=sin(s->angle*PI/180),ox,oy;coordinates(&w->core,36,s->pitch,cs,sn,s->ratio,&ox,&oy);
 double init[9]={s->pitch*cs,-s->pitch*s->ratio*sn,0,s->pitch*sn,s->pitch*s->ratio*cs,0,0,0,1};init[2]=init[0]*ox+init[1]*oy;init[5]=init[3]*ox+init[4]*oy;memcpy(h,init,sizeof init);
 const int counts[5]={36,48,64,96,128};
 for(int stage=0;stage<5;stage++)for(int iter=0;iter<5;iter++){
  d->iterations++;double inv[9],a[8][9]={{0}};if(!inverse(h,inv))return 0;int use=n<counts[stage]?n:counts[stage];
  for(int i=0;i<use;i++){
   double u,v;if(!pen_projective_map_v4(inv,w->all[i].x,w->all[i].y,&u,&v))return 0;double x=round(u),y=round(v),dx=u-x,dy=v-y;
   if(fabs(dx)>fabs(dy))x+=dx<0?-1.0/6:1.0/6;else y+=dy<0?-1.0/6:1.0/6;
   double px=w->all[i].x,py=w->all[i].y,rows[2][9]={{x,y,1,0,0,0,-px*x,-px*y,px},{0,0,0,x,y,1,-py*x,-py*y,py}};
   for(int k=0;k<2;k++)for(int r=0;r<8;r++)for(int c=0;c<9;c++)a[r][c]+=rows[k][r]*rows[k][c];
  }
  if(!solve(a,h)||!geometry_valid(h))return 0;
 }
 return 1;
}
static int validate_projective(pen_projective_workspace*w,int n,const pen_roi_config*cfg,const double h[9],pen_projective_result*out){
 double inv[9];if(!geometry_valid(h)||!inverse(h,inv))return 0;
 int minx=1000,miny=1000,maxx=-1000,maxy=-1000;double error=0;
 for(int i=0;i<n;i++){
  double u,v;if(!pen_projective_map_v4(inv,w->all[i].x,w->all[i].y,&u,&v))return 0;
  if(fabs(u)>SIDE*2||fabs(v)>SIDE*2)return 0; /* bound integer conversion */
  int x=(int)round(u),y=(int)round(v);double dx=u-x,dy=v-y,ax=fabs(dx),ay=fabs(dy),major=fmax(ax,ay),minor=fmin(ax,ay);
  if(major<.10||major>.30||minor>.065)return 0;
  error+=minor*minor+(major-1.0/6)*(major-1.0/6);w->core.xx[i]=x;w->core.yy[i]=y;w->core.dirs[i]=ax>ay?(dx<0?1:2):(dy<0?0:3);
  if(x<minx)minx=x;
  if(x>maxx)maxx=x;
  if(y<miny)miny=y;
  if(y>maxy)maxy=y;
 }
 if(maxx-minx>=SIDE||maxy-miny>=SIDE)return 0;
 for(int i=0;i<SIDE*SIDE;i++)w->core.grid[i]=-1;
 for(int i=0;i<n;i++){int z=((int)w->core.yy[i]-miny)*SIDE+(int)w->core.xx[i]-minx;if(w->core.grid[z]>=0)return 0;w->core.grid[z]=w->core.dirs[i];}
 int windows=0,tx=0,ty=0;pen_projective_result r;memset(&r,0,sizeof r);
 for(int row=0;row<=maxy-miny-5;row++)for(int col=0;col<=maxx-minx-5;col++){
  uint8_t dirs[36];int complete=1;for(int y=0;y<6;y++)for(int x=0;x<6;x++){int v=w->core.grid[(row+y)*SIDE+col+x];if(v<0)complete=0;dirs[y*6+x]=(uint8_t)v;}
  uint16_t x,y;if(!complete||pen_anoto_decode(dirs,cfg->paper_width,cfg->paper_height,cfg->section_u,cfg->section_v,&x,&y))continue;
  int nx=(int)x-col-minx,ny=(int)y-row-miny;if(windows&&(tx!=nx||ty!=ny))return PEN_ROI_AMBIGUOUS;
  if(!windows){tx=nx;ty=ny;r.roi.decoded.x=x;r.roi.decoded.y=y;memcpy(r.roi.decoded.directions,dirs,36);}windows++;
 }
 if(!windows)return 0;
 r.abi_version=PEN_PROJECTIVE_ABI;r.roi.decoded.dots=(uint16_t)n;r.roi.decoded.windows=(uint16_t)windows;r.roi.decoded.residual_cells=(float)sqrt(error/n);
 r.roi.decoded.pitch_px=(float)hypot(h[0],h[3]);r.roi.decoded.angle_deg=(float)(atan2(h[3],h[0])*180/PI);r.roi.y_scale=(float)(hypot(h[1],h[4])/hypot(h[0],h[3]));
 /* Compose paper translation: lattice=paper-(tx,ty). Crop/frame translation
  * is added by caller, preserving projective denominator terms. */
 memcpy(r.paper_to_frame,h,9*sizeof(double));for(int row=0;row<3;row++)r.paper_to_frame[row*3+2]-=h[row*3]*tx+h[row*3+1]*ty;
 *out=r;return 1;
}
int pen_roi_decode_projective_v4(const uint8_t*g,size_t len,unsigned width,unsigned height,unsigned stride,const pen_roi_config*cfg,pen_projective_workspace*w,pen_projective_result*out,pen_projective_diagnostics*diagnostics){
 pen_projective_diagnostics d={0};if(diagnostics)*diagnostics=d;
 if(!g||!cfg||!w||!out||width<96||height<96||width>256||height>256||stride<width||(size_t)(height-1)>(SIZE_MAX-width)/stride||len<(size_t)(height-1)*stride+width||cfg->paper_width<6||cfg->paper_height<6||cfg->paper_width>4096||cfg->paper_height>4096||cfg->section_u>=63||cfg->section_v>=63)return PEN_ROI_ARGUMENT;
 unsigned left=(width-80)/2,top=(height-80)/2;int n=extract(g,stride,left,top,w,&d),rc=PEN_ROI_DETECTION;
 if(n<0)goto done;
 for(int i=0;i<36;i++)w->core.points[i]=w->all[i];
 for(int a=-60;a<=60;a+=2)for(int p=16;p<=64;p++)for(int r=4;r<=14;r++){
  int seed=0;fit dummy;d.coarse++;(void)candidate(&w->core,36,cfg,p*.5,a,r*.1,&dummy,&seed);
  if(seed){if(d.seeds==PEN_PROJECTIVE_MAX_SEEDS){d.overflow=1;rc=PEN_ROI_AMBIGUOUS;goto done;}w->seeds[d.seeds++]=(pen_roi_refine_seed){p*.5,a,r*.1};}
 }
 rc=PEN_ROI_NO_GRID;int found=0;pen_projective_result best;
 for(unsigned i=0;i<d.seeds;i++){
  double h[9];if(!refine_projective(w,n,&w->seeds[i],h,&d))continue;d.models++;pen_projective_result r;int status=validate_projective(w,n,cfg,h,&r);
  if(status<0){rc=status;goto done;}if(!status)continue;
  if(found&&(best.roi.decoded.x!=r.roi.decoded.x||best.roi.decoded.y!=r.roi.decoded.y)){rc=PEN_ROI_AMBIGUOUS;goto done;}
  if(!found||r.roi.decoded.residual_cells<best.roi.decoded.residual_cells)best=r;
  found=1;
 }
 if(found){
  best.left=(uint16_t)left;best.top=(uint16_t)top;best.width=80;best.height=80;best.roi.candidates=d.coarse+d.models;
  for(int i=0;i<3;i++){best.paper_to_frame[i]+=(left+39.5)*best.paper_to_frame[6+i];best.paper_to_frame[3+i]+=(top+39.5)*best.paper_to_frame[6+i];}
  if(!inverse(best.paper_to_frame,best.frame_to_paper)){rc=PEN_ROI_NO_GRID;goto done;}*out=best;rc=0;
 }
 done:if(diagnostics)*diagnostics=d;return rc;
}
