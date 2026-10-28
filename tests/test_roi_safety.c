/* Native sanitizer runner: API memory safety, immutable failure outputs,
 * and one committed independently rendered positive fixture. */
#include "../firmware/vision/roi.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

static unsigned char image[192*192];
static pen_roi_config cfg={710,1000,0,0};
static void rejected(const unsigned char *p,size_t n,unsigned w,unsigned h,unsigned s,
                     const pen_roi_config *c) {
 pen_roi_result out,before;
 memset(&out,0xa5,sizeof out);memcpy(&before,&out,sizeof out);
 assert(pen_roi_decode(p,n,w,h,s,c,&out)!=PEN_ROI_OK);
 assert(memcmp(&out,&before,sizeof out)==0);
}
int main(int argc,char **argv) {
 pen_roi_result result;
 rejected(NULL,sizeof image,192,192,192,&cfg);
 rejected(image,sizeof image,192,192,192,NULL);
 assert(pen_roi_decode(image,sizeof image,192,192,192,&cfg,NULL)!=0);
 rejected(image,sizeof image,0,192,192,&cfg);
 rejected(image,sizeof image,192,0,192,&cfg);
 rejected(image,sizeof image,257,192,257,&cfg);
 rejected(image,sizeof image,192,257,192,&cfg);
 rejected(image,sizeof image,UINT_MAX,UINT_MAX,UINT_MAX,&cfg);
 rejected(image,sizeof image,192,192,191,&cfg);
 rejected(image,sizeof image-1,192,192,192,&cfg);
 rejected(image,0,192,192,192,&cfg);
 memset(image,255,sizeof image);rejected(image,sizeof image,192,192,192,&cfg);
 memset(image,0,sizeof image);rejected(image,sizeof image,192,192,192,&cfg);
 {unsigned state=12345;for(size_t i=0;i<sizeof image;i++){
   state=1664525u*state+1013904223u;image[i]=(unsigned char)(state>>24);
  } rejected(image,sizeof image,192,192,192,&cfg);}
 assert(argc==2);
 {FILE *f=fopen(argv[1],"rb");unsigned w,h,max;char magic[3];assert(f);
  assert(fscanf(f,"%2s %u %u %u",magic,&w,&h,&max)==4);
  assert(strcmp(magic,"P5")==0&&w==192&&h==192&&max==255);
  assert(fgetc(f)=='\n');assert(fread(image,1,sizeof image,f)==sizeof image);
  assert(fclose(f)==0);}
 assert(pen_roi_decode(image,sizeof image,192,192,192,&cfg,&result)==PEN_ROI_OK);
 assert(result.x==0&&result.y==0&&result.dots==36);
 puts("ROI native safety and positive fixture passed");return 0;
}
