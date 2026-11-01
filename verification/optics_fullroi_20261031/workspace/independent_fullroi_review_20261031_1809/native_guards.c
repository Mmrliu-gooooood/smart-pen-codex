#include "candidate.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c) do{if(!(c)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#c);return 1;}}while(0)
struct W { uint64_t pre[8]; candidate_workspace value; uint64_t post[8]; };
struct R { uint64_t pre[8]; pen_roi_opt_result value; uint64_t post[8]; };
struct I { uint64_t pre[8]; uint8_t pixels[40000]; uint64_t post[8]; };
static int guard(const uint64_t *p){for(unsigned i=0;i<8;i++)if(p[i]!=UINT64_C(0x7c7c7c7c7c7c7c7c))return 0;return 1;}
int main(int argc,char **argv){
 CHECK(argc==2);FILE *f=fopen(argv[1],"rb");CHECK(f);char line[80];CHECK(fgets(line,sizeof line,f));CHECK(strcmp(line,"P5\n")==0);CHECK(fgets(line,sizeof line,f));CHECK(strcmp(line,"200 200\n")==0);CHECK(fgets(line,sizeof line,f));CHECK(strcmp(line,"255\n")==0);
 struct W *w=malloc(sizeof *w);struct R r;struct I *im=malloc(sizeof *im);CHECK(w&&im);memset(w,0x7c,sizeof *w);memset(&r,0x7c,sizeof r);memset(im,0x7c,sizeof *im);CHECK(fread(im->pixels,1,40000,f)==40000);CHECK(fclose(f)==0);
 uint8_t saved[40000];memcpy(saved,im->pixels,sizeof saved);pen_roi_config cfg={710,1000,0,0};pen_roi_refine_diagnostics d;memset(&d,0xa5,sizeof d);
 int rc=candidate_decode(im->pixels,40000,200,200,200,&cfg,&w->value,&r.value,&d);
#if PEN_ROI_REFINE_MAX_SEEDS == 64
 CHECK(rc==0);CHECK(r.value.decoded.x==156&&r.value.decoded.y==51);
#else
 CHECK(rc!=0);
#endif
 CHECK(memcmp(saved,im->pixels,sizeof saved)==0);CHECK(guard(w->pre)&&guard(w->post)&&guard(r.pre)&&guard(r.post)&&guard(im->pre)&&guard(im->post));
 memset(&r.value,0xa5,sizeof r.value);pen_roi_opt_result before=r.value;
 CHECK(candidate_decode(im->pixels,40000,200,200,199,&cfg,&w->value,&r.value,&d)==PEN_ROI_ARGUMENT);CHECK(memcmp(&before,&r.value,sizeof before)==0);
 CHECK(candidate_decode(NULL,40000,200,200,200,&cfg,&w->value,&r.value,&d)==PEN_ROI_ARGUMENT);CHECK(memcmp(&before,&r.value,sizeof before)==0);
 CHECK(candidate_decode(im->pixels,SIZE_MAX,200,200,200,&cfg,&w->value,&r.value,&d)==PEN_ROI_ARGUMENT);
 CHECK(candidate_decode(im->pixels,40000,200,200,200,&cfg,&w->value,&r.value,(pen_roi_refine_diagnostics*)&r.value)==PEN_ROI_ARGUMENT);CHECK(memcmp(&before,&r.value,sizeof before)==0);
 CHECK(candidate_decode(im->pixels,40000,200,200,200,&cfg,&w->value,(pen_roi_opt_result*)&w->value,&d)==PEN_ROI_ARGUMENT);
 CHECK(candidate_decode(im->pixels,40000,200,200,200,&cfg,&w->value,&r.value,(pen_roi_refine_diagnostics*)im->pixels)==PEN_ROI_ARGUMENT);CHECK(memcmp(saved,im->pixels,sizeof saved)==0);
 memset(im->pixels,240,40000);for(unsigned y=0;y<6;y++)for(unsigned x=0;x<6;x++){unsigned xx=80+x*3,yy=80+y*3;im->pixels[yy*200+xx]=30;im->pixels[yy*200+xx+1]=30;im->pixels[(yy+1)*200+xx]=30;}
 cfg.section_u=10;cfg.section_v=2;memset(&r.value,0xa5,sizeof r.value);before=r.value;
 rc=candidate_decode(im->pixels,40000,200,200,200,&cfg,&w->value,&r.value,&d);
#if CANDIDATE_ENABLE_REFINEMENT
 CHECK(rc==PEN_ROI_AMBIGUOUS);CHECK(d.seeds==PEN_ROI_REFINE_MAX_SEEDS+1);CHECK(d.iterations==0&&d.refined_models==0);
#else
 CHECK(rc!=0);CHECK(d.seeds==0);
#endif
 CHECK(memcmp(&before,&r.value,sizeof before)==0);CHECK(guard(w->pre)&&guard(w->post)&&guard(r.pre)&&guard(r.post)&&guard(im->pre)&&guard(im->post));
 printf("PASS enabled=%d cap=%u workspace=%zu result=%zu overflow_status=%d seeds=%u guards/input/failure/alias/range checked\n",CANDIDATE_ENABLE_REFINEMENT,(unsigned)PEN_ROI_REFINE_MAX_SEEDS,sizeof(candidate_workspace),sizeof(pen_roi_opt_result),rc,(unsigned)d.seeds);free(w);free(im);return 0;
}
