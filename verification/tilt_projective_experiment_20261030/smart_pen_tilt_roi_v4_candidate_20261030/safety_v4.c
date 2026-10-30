#include "roi_projective.h"
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
static struct {uint64_t pre[8];pen_projective_workspace ws;uint64_t post[8];} work;
static struct {uint8_t pre[64],im[200*640],post[64];} pixels;
static struct {uint64_t pre[8];pen_projective_result out;uint64_t post[8];} result;
static uint8_t before[sizeof pixels.im],fixture[40000];
static pen_projective_diagnostics maxd;
static unsigned calls;
static void check_guards(void){
 for(unsigned i=0;i<8;i++){assert(work.pre[i]==UINT64_C(0x5a5a5a5a5a5a5a5a));assert(work.post[i]==UINT64_C(0x5a5a5a5a5a5a5a5a));assert(result.pre[i]==UINT64_C(0x5a5a5a5a5a5a5a5a));assert(result.post[i]==UINT64_C(0x5a5a5a5a5a5a5a5a));}
 for(unsigned i=0;i<64;i++)assert(pixels.pre[i]==0x5a&&pixels.post[i]==0x5a);
 assert(memcmp(before,pixels.im,sizeof before)==0);
}
static int invoke(const uint8_t*g,size_t len,unsigned w,unsigned h,unsigned stride,const pen_roi_config*cfg,int nullws,int nullout,int nulldiag){
 pen_projective_diagnostics d;memset(&d,0xa5,sizeof d);memset(&result.out,0xa5,sizeof result.out);pen_projective_result old=result.out;memcpy(before,pixels.im,sizeof before);
 int rc=pen_roi_decode_projective_v4(g,len,w,h,stride,cfg,nullws?NULL:&work.ws,nullout?NULL:&result.out,nulldiag?NULL:&d);calls++;
 check_guards();if(rc)assert(memcmp(&result.out,&old,sizeof old)==0);
 if(!nulldiag){
  assert(d.coarse<=32879&&d.seeds<=256&&d.iterations<=6400&&d.models<=256&&d.retained<=128&&d.overflow<=1);
  if(d.coarse>maxd.coarse)maxd.coarse=d.coarse;
  if(d.seeds>maxd.seeds)maxd.seeds=d.seeds;
  if(d.iterations>maxd.iterations)maxd.iterations=d.iterations;
  if(d.models>maxd.models)maxd.models=d.models;
 }
 return rc;
}
int main(int argc,char**argv){
 assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f);char line[80];for(int i=0;i<3;i++)assert(fgets(line,sizeof line,f));assert(fread(fixture,1,sizeof fixture,f)==sizeof fixture);fclose(f);
 memset(&work,0x5a,sizeof work);memset(&pixels,0x5a,sizeof pixels);memset(&result,0x5a,sizeof result);memcpy(pixels.im,fixture,sizeof fixture);
 pen_roi_config cfg={710,1000,10,2};
 assert(invoke(pixels.im,40000,200,200,200,&cfg,0,0,0)==0);pen_projective_result good=result.out;
 assert(invoke(pixels.im,40000,200,200,200,&cfg,0,0,1)==0);assert(memcmp(&good,&result.out,sizeof good)==0);
 assert(invoke(NULL,40000,200,200,200,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,200,NULL,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,200,&cfg,1,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,200,&cfg,0,1,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,39999,200,200,200,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,199,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,0,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,200,UINT_MAX,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,95,200,200,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,95,200,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,257,200,257,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 assert(invoke(pixels.im,40000,200,257,200,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 for(unsigned k=0;k<6;k++){pen_roi_config c=cfg;if(k==0)c.paper_width=5;if(k==1)c.paper_height=5;if(k==2)c.paper_width=4097;if(k==3)c.paper_height=4097;if(k==4)c.section_u=63;if(k==5)c.section_v=63;assert(invoke(pixels.im,40000,200,200,200,&c,0,0,0)==PEN_ROI_ARGUMENT);}
 memset(pixels.im,0xcc,sizeof pixels.im);for(unsigned y=0;y<200;y++)memcpy(pixels.im+y*640,fixture+y*200,200);
 assert(invoke(pixels.im,199*640+200,200,200,640,&cfg,0,0,0)==0);assert(memcmp(&good,&result.out,sizeof good)==0);
 assert(invoke(pixels.im,199*640+199,200,200,640,&cfg,0,0,0)==PEN_ROI_ARGUMENT);
 /* 128x128 raw frame preserving identical central80 pixels, not resizing. */
 memset(pixels.im,240,sizeof pixels.im);for(unsigned y=0;y<128;y++)memcpy(pixels.im+y*128,fixture+(y+36)*200+36,128);
 assert(invoke(pixels.im,128*128,128,128,128,&cfg,0,0,0)==0);assert(result.out.roi.decoded.x==good.roi.decoded.x&&result.out.roi.decoded.y==good.roi.decoded.y);
 for(int k=0;k<3;k++){assert(fabs(result.out.paper_to_frame[k]-(good.paper_to_frame[k]-36*good.paper_to_frame[6+k]))<1e-9);assert(fabs(result.out.paper_to_frame[3+k]-(good.paper_to_frame[3+k]-36*good.paper_to_frame[6+k]))<1e-9);}
 /* >128 separated 2x2 dark components exercises explicit centroid overflow. */
 memset(pixels.im,240,sizeof pixels.im);for(unsigned y=63;y<137;y+=5)for(unsigned x=63;x<137;x+=5){pixels.im[y*200+x]=30;pixels.im[y*200+x+1]=30;pixels.im[(y+1)*200+x]=30;pixels.im[(y+1)*200+x+1]=30;}
 assert(invoke(pixels.im,40000,200,200,200,&cfg,0,0,0)==PEN_ROI_DETECTION);
 pen_projective_diagnostics dd;assert(pen_roi_decode_projective_v4(pixels.im,40000,200,200,200,&cfg,&work.ws,&result.out,&dd)==PEN_ROI_DETECTION);assert(dd.overflow==1);
 for(uint32_t seed=1;seed<=32;seed++){uint32_t state=seed;for(unsigned i=0;i<40000;i++){state=state*1664525u+1013904223u;pixels.im[i]=(uint8_t)(state>>24);}assert(invoke(pixels.im,40000,200,200,200,&cfg,0,0,0)!=0);}
 double identity[9]={1,0,0,0,1,0,0,0,1},u=123,v=456;
 assert(pen_projective_map_v4(identity,2,3,&u,&v)==1&&u==2&&v==3);
 for(unsigned k=0;k<14;k++){double h[9];memcpy(h,identity,sizeof h);u=123;v=456;double x=2,y=3;if(k<9)h[k]=NAN;if(k==9)h[8]=0;if(k==10)x=INFINITY;if(k==11)y=NAN;if(k==12)h[0]=INFINITY;
  assert(pen_projective_map_v4(k==13?NULL:h,x,y,&u,&v)==0);assert(u==123&&v==456);}
 u=123;v=456;assert(!pen_projective_map_v4(identity,2,3,NULL,&v)&&v==456);assert(!pen_projective_map_v4(identity,2,3,&u,NULL)&&u==123);
 printf("PASS V4 ASan/UBSan safety: calls=%u random32 workspace=%zu max_coarse=%u max_seeds=%u max_iterations=%u max_models=%u\n",calls,sizeof work.ws,maxd.coarse,maxd.seeds,maxd.iterations,maxd.models);return 0;
}
