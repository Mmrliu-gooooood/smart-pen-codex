#include "roi_projective.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static pen_projective_workspace ws;
static uint8_t image[40000];
int main(int argc,char**argv){
 assert(PEN_PROJECTIVE_MAX_SEEDS==1&&argc==2);FILE*f=fopen(argv[1],"rb");assert(f);char line[80];for(int i=0;i<3;i++)assert(fgets(line,sizeof line,f));assert(fread(image,1,sizeof image,f)==sizeof image);fclose(f);
 pen_projective_result out;memset(&out,0xa5,sizeof out);pen_projective_result before=out;pen_projective_diagnostics d;pen_roi_config c={710,1000,10,2};
 int rc=pen_roi_decode_projective_v4(image,sizeof image,200,200,200,&c,&ws,&out,&d);
 assert(rc==PEN_ROI_AMBIGUOUS&&d.overflow==1&&d.seeds==1&&d.models==0&&d.iterations==0&&memcmp(&out,&before,sizeof out)==0);
 printf("PASS injected seedcap1: status=%d overflow=%u seeds=%u coarse=%u models=%u unchanged_result=1\n",rc,d.overflow,d.seeds,d.coarse,d.models);return 0;
}
