/* Private fitter unit seam plus public no-truncation/output contract. */
#include "../firmware/vision/roi_opt.c"
#include "../firmware/vision/roi_continuous.h"
#include <assert.h>
#include <stdio.h>
static pen_continuous_workspace workspace;
static uint8_t image[200*200];
static pen_roi_config config={710,1000,10,2};
int main(int argc,char **argv){
 pen_roi_workspace *w=&workspace.core;uint32_t iterations=0;
 for(int i=0;i<49;i++){
  int d=i%4;double dx=d==1?-1.0/6:d==2?1.0/6:0,dy=d==0?-1.0/6:d==3?1.0/6:0;
  w->points[i].x=25+10*(i%7+dx);w->points[i].y=30+10*(i/7+dy);
 }
 pen_roi_refine_seed seed={9.5,1,1};
 assert(refine_geometry(w,49,&seed,&iterations));assert(iterations==5);
 assert(fabs(seed.pitch-10)<1e-8&&fabs(seed.angle)<1e-8&&fabs(seed.ratio-1)<1e-8);
 for(unsigned kind=0;kind<3;kind++){
  seed.pitch=kind==0?NAN:kind==1?0:10;seed.angle=kind==2?INFINITY:0;seed.ratio=1;iterations=0;
  assert(!refine_geometry(w,49,&seed,&iterations));assert(iterations<=5);
 }
 for(int i=0;i<49;i++){w->points[i].x=i;w->points[i].y=20;}
 seed.pitch=10;seed.angle=0;seed.ratio=1;iterations=0;
 assert(!refine_geometry(w,49,&seed,&iterations));
 assert(argc==2);
 {FILE *f=fopen(argv[1],"rb");unsigned width,height,max;char magic[3];assert(f);
 assert(fscanf(f,"%2s %u %u %u",magic,&width,&height,&max)==4);
 assert(!strcmp(magic,"P5")&&width==200&&height==200&&max==255);assert(fgetc(f)=='\n');
 assert(fread(image,1,sizeof image,f)==sizeof image);assert(!fclose(f));}
 pen_continuous_result result,before;memset(&result,0xa5,sizeof result);memcpy(&before,&result,sizeof before);
 int rc=pen_roi_decode_continuous(image,sizeof image,200,200,200,&config,&workspace,&result);
 if(PEN_ROI_REFINE_MAX_SEEDS==1){assert(rc==PEN_ROI_AMBIGUOUS);assert(!memcmp(&result,&before,sizeof result));}
 else{assert(rc==PEN_ROI_OK);assert(result.refine_seeds>1&&result.refine_seeds<=64);}
 /* Same prepared96px buffer: overflow rejects before any first-success shortcut. */
 pen_roi_opt_result out,old;pen_roi_grid_transform t,told;pen_roi_refine_diagnostics d;
 memset(&out,0xa5,sizeof out);memcpy(&old,&out,sizeof old);memset(&t,0xa5,sizeof t);memcpy(&told,&t,sizeof told);
 rc=pen_roi_decode_refined_transform(workspace.crop,96*96,96,96,96,&config,w,workspace.seeds,&out,&t,&d);
 if(PEN_ROI_REFINE_MAX_SEEDS==1){
  assert(rc==PEN_ROI_AMBIGUOUS&&d.seeds==2&&d.iterations==0&&d.refined_models==0);
  assert(!memcmp(&out,&old,sizeof out)&&!memcmp(&t,&told,sizeof t));
 }else{assert(rc==0&&d.cold_candidates==26901&&d.seeds<=64&&d.iterations<=320);}
 memset(&out,0xa5,sizeof out);memcpy(&old,&out,sizeof old);memset(&t,0xa5,sizeof t);memcpy(&told,&t,sizeof told);
 config.section_u=63;
 assert(pen_roi_decode_refined_transform(image,sizeof image,200,200,200,&config,w,workspace.seeds,&out,&t,&d)==PEN_ROI_ARGUMENT);
 assert(!memcmp(&out,&old,sizeof out)&&!memcmp(&t,&told,sizeof t)&&!d.cold_candidates);
 puts("V3 all-point fitter degeneracy/nonfinite/seed-overflow safety PASS");return 0;
}
