#include "bench_wire.h"
#include "pen.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void put(uint8_t*p,uint64_t v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(uint8_t)(v>>(8*i));}
int main(void){
 uint8_t a[20]={'A','K',1,0};put(a+4,123,8);put(a+12,4,4);put(a+16,pen_crc32(a,16),4);
 assert(bench_ack(a,20,1,1,1,1,1,123,4)==1);assert(bench_ack(a,20,1,1,1,1,1,123,5)==0);
 assert(bench_ack(a,20,1,1,1,1,1,123,3)==-1);assert(bench_ack(a,20,1,1,1,1,1,124,4)==-1);
 for(unsigned j=0;j<5;j++){bool sec[5]={1,1,1,1,1};sec[j]=0;assert(bench_ack(a,20,sec[0],sec[1],sec[2],sec[3],sec[4],123,4)==-1);}
 assert(bench_ack(a,19,1,1,1,1,1,123,4)==-1);
 for(unsigned i=0;i<20;i++){a[i]^=1;assert(bench_ack(a,20,1,1,1,1,1,123,4)==-1);a[i]^=1;}
 uint8_t p[48],f[20];for(unsigned i=0;i<48;i++)p[i]=(uint8_t)i;
 for(unsigned i=0;i<3;i++){assert(!bench_fragment(p,0x12345,i,f));assert(f[0]==0xb1&&f[1]==i&&f[2]==0x45&&f[3]==0x23);assert(!memcmp(f+4,p+i*16,16));}
 assert(bench_fragment(p,0,3,f)==-1);puts("bench wire: auth state, stale/future/session/CRC ACK, framing PASS");
}
