#include "bench_wire.h"
#include "pen.h"
#include <string.h>
static uint64_t get(const uint8_t*p,unsigned n){uint64_t v=0;for(unsigned i=0;i<n;i++)v|=(uint64_t)p[i]<<(i*8);return v;}
int bench_ack(const uint8_t*b,size_t n,bool approved,bool encrypted,bool authenticated,bool bonded,bool sent,uint64_t session,uint32_t seq){
 if(!approved||!encrypted||!authenticated||!bonded||n!=20)return -1;
 if(b[0]!='A'||b[1]!='K'||b[2]!=1||b[3]||get(b+16,4)!=pen_crc32(b,16)||get(b+4,8)!=session||get(b+12,4)>seq)return -1;
 if(get(b+12,4)<seq)return 0;
 return sent?1:-1;
}
int bench_fragment(const uint8_t p[48],uint32_t seq,unsigned i,uint8_t out[20]){
 if(i>2)return -1;
 out[0]=0xb1;out[1]=(uint8_t)i;out[2]=(uint8_t)seq;out[3]=(uint8_t)(seq>>8);memcpy(out+4,p+i*16,16);return 0;
}
