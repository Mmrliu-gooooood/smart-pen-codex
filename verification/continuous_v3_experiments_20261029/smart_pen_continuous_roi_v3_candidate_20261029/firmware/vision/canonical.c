#include "canonical.h"
#include <stdlib.h>
#include <string.h>
int pen_canonical_directions(const uint8_t *g,unsigned p,uint8_t out[36]) {
 if(p<8||p>64)return -1;
 uint8_t d[36];unsigned width=6*p;
 for(unsigned row=0;row<6;row++)for(unsigned col=0;col<6;col++){
  int sx=0,sy=0,n=0;
  for(unsigned y=0;y<p;y++)for(unsigned x=0;x<p;x++)if(g[(row*p+y)*width+col*p+x]<128){sx+=(int)x;sy+=(int)y;n++;}
  if(n<3||n>(int)(p*p/5))return -1;
  /* integer centroid in 1/1024 pixel, target center floor(p/2). */
  int dx=sx*1024/n-(int)(p/2)*1024,dy=sy*1024/n-(int)(p/2)*1024;
  int ax=abs(dx),ay=abs(dy),major=ax>ay?ax:ay,minor=ax>ay?ay:ax;
  if(major<(int)p*1024/10||major>(int)p*1024*35/100||minor>(int)p*1024*8/100)return -1;
  d[row*6+col]=ax>ay?(dx<0?1:2):(dy<0?0:3);
 }
 memcpy(out,d,36);return 0;
}
