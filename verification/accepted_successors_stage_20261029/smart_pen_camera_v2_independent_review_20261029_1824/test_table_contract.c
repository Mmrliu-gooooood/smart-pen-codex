/* Independent bounded-table unit test. Synthetic bus, no device access. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "candidate/third_party/esp32-camera/sensors/sc031gs.c"
static unsigned checks, writes, fail_at;
static uint16_t trace_addr[512];
static uint8_t trace_val[512];
#define CHECK(x) do { ++checks; if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} } while(0)
int SCCB_Read16_Checked(uint8_t a,uint16_t r,uint8_t *o){(void)a;(void)r;*o=0;return 0;}
int SCCB_Write16(uint8_t a,uint16_t r,uint8_t v){CHECK(a==0x30);CHECK(writes<512);trace_addr[writes]=r;trace_val[writes]=v;++writes;return writes==fail_at?19:0;}
int xclk_timer_conf(int a,int b){(void)a;(void)b;return 0;}
static void verify(const struct sc031gs_regval *table,size_t n){
 for(size_t k=0;k<n;k++){
  struct sc031gs_regval *p=malloc((k?k:1)*sizeof(*p));CHECK(p);memcpy(p,table,k*sizeof(*p));writes=fail_at=0;CHECK(write_regs(0x30,p,k)==-1);CHECK(!writes);free(p);
 }
 struct sc031gs_regval *p=malloc(n*sizeof(*p));CHECK(p);
 for(size_t k=0;k+1<n;k++) {memcpy(p,table,n*sizeof(*p));p[k].addr=REG_NULL;writes=fail_at=0;CHECK(write_regs(0x30,p,n)==-1);CHECK(!writes);}
 for(unsigned v=1;v<256;v++){memcpy(p,table,n*sizeof(*p));p[n-1].val=(uint8_t)v;writes=fail_at=0;CHECK(write_regs(0x30,p,n)==-1);CHECK(!writes);}
 writes=fail_at=0;CHECK(write_regs(0x30,table,n)==0);unsigned total=writes,j=0;
 for(size_t i=0;i+1<n;i++)if(table[i].addr!=REG_DELAY){CHECK(trace_addr[j]==table[i].addr);CHECK(trace_val[j]==table[i].val);j++;}
 CHECK(j==total);
 for(unsigned k=1;k<=total;k++){writes=0;fail_at=k;CHECK(write_regs(0x30,table,n)==19);CHECK(writes==k);}
 free(p);
}
int main(void){verify(sc031gs_reset_regs,SC031GS_ARRAY_COUNT(sc031gs_reset_regs));verify(sc031gs_200x200_init_regs,SC031GS_ARRAY_COUNT(sc031gs_200x200_init_regs));verify(sc031gs_640x480_50fps_init_regs,SC031GS_ARRAY_COUNT(sc031gs_640x480_50fps_init_regs));printf("PASS %u independent checks: exact-size prefixes, every early terminator, all nonzero terminal values, exact write order, positive-error early stop. Synthetic only.\n",checks);}
