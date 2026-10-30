/* Algorithm adapted from Christoph Heindl's MIT py-microdots codec.py.
   Canonical anoto_6x6_a4_fixed only; see LICENSE.microdots. */
#include "anoto.h"
#include <stddef.h>
#include "sequences.h"
static const uint8_t *const sns[]={A1,A2,A3,A4_alt};
static const unsigned lens[]={236,233,31,241},bases[]={1,3,9,18},factors[]={3,3,2,3};
static int find(const uint8_t*s,unsigned n,const uint8_t*q,unsigned k){
 int found=-1;for(unsigned i=0;i<n;i++){unsigned j=0;while(j<k&&s[(i+j)%n]==q[j])j++;if(j==k){if(found>=0)return -1;found=(int)i;}}return found;
}
static int axis(const uint8_t*d,unsigned a,uint32_t *out,int *first){
 int loc[6];uint8_t q[6],coeff[4][5];
 for(unsigned i=0;i<6;i++){for(unsigned j=0;j<6;j++)q[j]=a?d[i*6+j]>>1:d[j*6+i]&1u;loc[i]=find(MNS,63,q,6);if(loc[i]<0)return -1;}
 for(unsigned i=0;i<5;i++){int delta=(loc[i+1]-loc[i]+63)%63;if(delta<5||delta>58)return -1;unsigned v=(unsigned)delta-5;for(unsigned j=0;j<4;j++)coeff[j][i]=(uint8_t)((v/bases[j])%factors[j]);}
 uint32_t value=0,step=1;
 for(unsigned j=0;j<4;j++){int r=find(sns[j],lens[j],coeff[j],5);if(r<0)return -1;unsigned k=0;while(value%lens[j]!=(unsigned)r){value+=step;if(++k>=lens[j])return -1;}step*=lens[j];}
 *out=value;*first=loc[0];return 0;
}
static unsigned integral(unsigned pos){unsigned v=0;for(unsigned i=0;i<pos;i++){unsigned delta=5;for(unsigned j=0;j<4;j++)delta+=bases[j]*sns[j][i%lens[j]];v=(v+delta)%63;}return v;}
int pen_anoto_decode(const uint8_t d[36],uint16_t w,uint16_t h,uint8_t u,uint8_t v,uint16_t*x,uint16_t*y){
 if(w<6||h<6||w>4096||h>4096||u>=63||v>=63)return -1;
 for(unsigned i=0;i<36;i++)if(d[i]>3)return -1;
 uint32_t px,py;int mx,my;
 if(axis(d,0,&px,&mx)||axis(d,1,&py,&my)||px>(uint32_t)w-6||py>(uint32_t)h-6)return -1;
 unsigned su=((unsigned)mx+126-(py%63)-integral(px))%63;
 unsigned sv=((unsigned)my+126-(px%63)-integral(py))%63;
 if(su!=u||sv!=v)return -1;
 *x=(uint16_t)px;*y=(uint16_t)py;return 0;
}
