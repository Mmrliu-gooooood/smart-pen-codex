#include "../firmware/vision/roi_continuous.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
static pen_continuous_workspace workspace;
static unsigned char pixels[256*269],saved[256*269];
static pen_roi_config config={710,1000,10,2};
static unsigned rng=0x10281029u;
static unsigned random32(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static int check(const unsigned char *g,size_t length,unsigned w,unsigned h,unsigned stride,
 pen_continuous_workspace *ws,int expect){
 pen_continuous_result result,before;memset(&result,0xa5,sizeof result);memcpy(&before,&result,sizeof before);
 int rc=pen_roi_decode_continuous(g,length,w,h,stride,&config,ws,&result);
 assert(rc==0||memcmp(&result,&before,sizeof result)==0);
 if(expect)assert(rc!=0);
 return rc;
}
int main(int argc,char **argv){
 assert(sizeof workspace<=32768);
 memset(pixels,240,sizeof pixels);
 check(NULL,sizeof pixels,200,200,200,&workspace,1);
 check(pixels,sizeof pixels,200,200,200,NULL,1);
 check(pixels,39999,200,200,200,&workspace,1);
 check(pixels,sizeof pixels,UINT_MAX,UINT_MAX,UINT_MAX,&workspace,1);
 check(pixels,sizeof pixels,200,200,0,&workspace,1);
 check(pixels,sizeof pixels,95,200,200,&workspace,1);
 check(pixels,sizeof pixels,200,95,200,&workspace,1);
 check(pixels,sizeof pixels,257,200,257,&workspace,1);
 check(pixels,sizeof pixels,200,200,200,&workspace,1);
 assert(argc==2);
 {FILE *f=fopen(argv[1],"rb");unsigned w,h,max;char magic[3];assert(f);
 assert(fscanf(f,"%2s %u %u %u",magic,&w,&h,&max)==4);
 assert(strcmp(magic,"P5")==0&&w==200&&h==200&&max==255);assert(fgetc(f)=='\n');
 assert(fread(pixels,1,40000,f)==40000);assert(fclose(f)==0);}
 memcpy(saved,pixels,sizeof pixels);assert(check(pixels,40000,200,200,200,&workspace,0)==0);
 assert(memcmp(saved,pixels,sizeof pixels)==0);
 /* No stale success after damage; large connected pixel sets never overflow. */
 memset(pixels,0,40000);check(pixels,40000,200,200,200,&workspace,1);
 for(unsigned n=0;n<400;n++){
  unsigned w=96+random32()%161,h=96+random32()%161,stride=w+random32()%14;
  for(unsigned y=0;y<h;y++)for(unsigned x=0;x<stride;x++)pixels[y*stride+x]=(unsigned char)random32();
  memcpy(saved,pixels,sizeof pixels);check(pixels,sizeof pixels,w,h,stride,&workspace,1);
  assert(memcmp(saved,pixels,sizeof pixels)==0);
 }
 /* New optional transform shares the core output-untouched failure contract. */
 pen_roi_opt_result out,before;pen_roi_grid_transform t,t_before;
 memset(&out,0xa5,sizeof out);memcpy(&before,&out,sizeof out);
 memset(&t,0xa5,sizeof t);memcpy(&t_before,&t,sizeof t);
 pen_roi_prior prior={1,12,0,1};
 assert(pen_roi_decode_opt_transform(NULL,0,200,200,200,&config,&workspace.core,&prior,&out,&t)!=0);
 assert(!prior.valid&&memcmp(&out,&before,sizeof out)==0&&memcmp(&t,&t_before,sizeof t)==0);
 puts("continuous ROI native bounded traversal/buffer/output contract PASS");return 0;
}
