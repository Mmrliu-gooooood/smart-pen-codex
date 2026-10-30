/* Native optimized-workspace API test: deterministic current pixels, not cache. */
#include "../firmware/vision/roi_opt.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
static pen_roi_workspace workspace;
static unsigned char image[192*192];
static unsigned char boundary_image[256*256];
static pen_roi_config config={710,1000,0,0};
static void rejected(const unsigned char *data,size_t length,unsigned w,unsigned h,unsigned stride,
                     pen_roi_workspace *ws,pen_roi_prior *prior){
 pen_roi_opt_result out,before;
 memset(&out,0xa5,sizeof out);memcpy(&before,&out,sizeof out);
 assert(pen_roi_decode_opt(data,length,w,h,stride,&config,ws,prior,&out)!=0);
 assert(memcmp(&out,&before,sizeof out)==0);
 assert(prior->valid==0);
}
int main(int argc,char **argv){
 pen_roi_prior prior={1,18,0,1};pen_roi_opt_result out;
 rejected(NULL,sizeof image,192,192,192,&workspace,&prior);
 rejected(image,sizeof image,192,192,192,NULL,&prior);
 rejected(image,sizeof image-1,192,192,192,&workspace,&prior);
 rejected(image,sizeof image,UINT_MAX,UINT_MAX,UINT_MAX,&workspace,&prior);
 memset(image,240,sizeof image);prior.valid=1;
 rejected(image,sizeof image,192,192,192,&workspace,&prior);
 /* Last bit of the packed visited map and non-byte-aligned dimensions. */
 memset(boundary_image,240,sizeof boundary_image);
 boundary_image[65535]=0;boundary_image[65534]=0;boundary_image[65279]=0;
 rejected(boundary_image,sizeof boundary_image,256,256,256,&workspace,&prior);
 for(unsigned side=17;side<=255;side+=17){
  memset(boundary_image,240,sizeof boundary_image);
  boundary_image[(side-1)*side+side-1]=0;
  rejected(boundary_image,sizeof boundary_image,side,side,side,&workspace,&prior);
 }
 assert(argc==2);
 {FILE *f=fopen(argv[1],"rb");unsigned w,h,max;char magic[3];assert(f);
  assert(fscanf(f,"%2s %u %u %u",magic,&w,&h,&max)==4);
  assert(strcmp(magic,"P5")==0&&w==192&&h==192&&max==255);
  assert(fgetc(f)=='\n');assert(fread(image,1,sizeof image,f)==sizeof image);
  assert(fclose(f)==0);}
 assert(pen_roi_decode_opt(image,sizeof image,192,192,192,&config,&workspace,&prior,&out)==0);
 assert(out.decoded.x==0&&out.decoded.y==0&&out.decoded.dots==36&&!out.used_warm_start);
 assert(prior.valid==1);
 assert(pen_roi_decode_opt(image,sizeof image,192,192,192,&config,&workspace,&prior,&out)==0);
 assert(out.used_warm_start&&out.candidates<=27);
 prior.valid=1;prior.pitch_px=NAN;
 assert(pen_roi_decode_opt(image,sizeof image,192,192,192,&config,&workspace,&prior,&out)==0);
 assert(!out.used_warm_start);
 prior.valid=1;prior.angle_deg=INFINITY;
 assert(pen_roi_decode_opt(image,sizeof image,192,192,192,&config,&workspace,&prior,&out)==0);
 assert(!out.used_warm_start);
 config.section_u=1;rejected(image,sizeof image,192,192,192,&workspace,&prior);
 config.section_u=0;prior.valid=1;
 memset(image,240,sizeof image);rejected(image,sizeof image,192,192,192,&workspace,&prior);
 puts("ROI optimized native safety/current pixels/warm start passed");
 return 0;
}
