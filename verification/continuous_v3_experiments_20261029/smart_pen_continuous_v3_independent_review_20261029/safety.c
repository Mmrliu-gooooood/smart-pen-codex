#include "roi_continuous.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
static struct { uint64_t a[8]; pen_continuous_workspace ws; uint64_t b[8]; } guarded;
static uint8_t frame[256*279];
static uint32_t random_state=0x29100351;
static uint32_t next(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return random_state;}
int main(void){
 pen_roi_config cfg={710,1000,10,2};
 for(unsigned i=0;i<320;i++){
  memset(&guarded,0x7c,sizeof guarded);
  unsigned w=96+next()%161,h=96+next()%161,stride=w+next()%24;
  for(unsigned y=0;y<h;y++)for(unsigned x=0;x<stride;x++){
   unsigned v=next(); frame[y*stride+x]=(i%5==0)?0:(i%5==1)?255:(i%5==2)?((x+y)%2?255:0):(i%5==3)?(x%13?0:255):(uint8_t)v;
  }
  pen_continuous_result out,before;memset(&out,0xa5,sizeof out);memcpy(&before,&out,sizeof out);
  int rc=pen_roi_decode_continuous(frame,(h-1)*stride+w,w,h,stride,&cfg,&guarded.ws,&out);
  assert(rc!=0);assert(memcmp(&out,&before,sizeof out)==0);
  for(unsigned j=0;j<8;j++)assert(guarded.a[j]==UINT64_C(0x7c7c7c7c7c7c7c7c)&&guarded.b[j]==UINT64_C(0x7c7c7c7c7c7c7c7c));
 }
 /* Actual default64-seed overflow with36 tiny separate components, not a cap1 build. */
 memset(frame,240,40000);
 for(unsigned y=0;y<6;y++)for(unsigned x=0;x<6;x++){
  unsigned pos=(80+y*3)*200+80+x*3;frame[pos]=30;frame[pos+1]=30;frame[pos+200]=30;
 }
 static struct {uint64_t a[8];pen_roi_refine_seed seeds[64];uint64_t b[8];} sg;
 memset(&sg,0x7c,sizeof sg);pen_roi_opt_result out,old;pen_roi_grid_transform t,told;pen_roi_refine_diagnostics d;
 memset(&out,0xa5,sizeof out);memcpy(&old,&out,sizeof out);memset(&t,0xa5,sizeof t);memcpy(&told,&t,sizeof t);
 int rc=pen_roi_decode_refined_transform(frame,40000,200,200,200,&cfg,&guarded.ws.core,sg.seeds,&out,&t,&d);
 assert(rc==PEN_ROI_AMBIGUOUS&&d.seeds==65&&d.cold_candidates<26901&&d.iterations==0&&d.refined_models==0);
 assert(!memcmp(&out,&old,sizeof out)&&!memcmp(&t,&told,sizeof t));
 for(unsigned j=0;j<8;j++)assert(sg.a[j]==UINT64_C(0x7c7c7c7c7c7c7c7c)&&sg.b[j]==UINT64_C(0x7c7c7c7c7c7c7c7c));
 puts("320/320 negative traversal cases + actual65th-seed overflow: guards/output preservation PASS");
}
