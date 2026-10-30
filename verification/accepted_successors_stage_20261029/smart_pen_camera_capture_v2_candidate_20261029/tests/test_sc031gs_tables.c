/* Actual driver/table code, synthetic SCCB only. Tests all table contracts. */
#include <assert.h>
#include <stdio.h>
#include "../third_party/esp32-camera/sensors/sc031gs.c"
static unsigned checks;
static int writes,reads,fail_at;
#define CK(x) do {checks++;assert(x);}while(0)
int SCCB_Read16_Checked(uint8_t a,uint16_t r,uint8_t*out){(void)a;(void)r;reads++;*out=0;return 0;}
int SCCB_Write16(uint8_t a,uint16_t r,uint8_t v){(void)v;CK(a==0x30&&r!=REG_NULL&&r!=REG_DELAY);writes++;return writes==fail_at?-7:0;}
int xclk_timer_conf(int a,int b){(void)a;(void)b;return 0;}
static void table(const struct sc031gs_regval *t,size_t n) {
 writes=reads=fail_at=0;CK(!write_regs(0x30,t,n));int total=writes;CK(total>0&&!reads);
 for(int k=1;k<=total;k++){writes=0;fail_at=k;CK(write_regs(0x30,t,n)==-7);CK(writes==k);}
 writes=fail_at=0;CK(write_regs(0x30,t,n-1)==-1);CK(!writes); /* missing terminator, bounded */
}
int main(void){
 table(sc031gs_reset_regs,SC031GS_ARRAY_COUNT(sc031gs_reset_regs));
 table(sc031gs_200x200_init_regs,SC031GS_ARRAY_COUNT(sc031gs_200x200_init_regs));
 table(sc031gs_640x480_50fps_init_regs,SC031GS_ARRAY_COUNT(sc031gs_640x480_50fps_init_regs));
 const struct sc031gs_regval missing[]={{0x0103,1},{REG_DELAY,10}};
 const struct sc031gs_regval early[]={{REG_NULL,0},{0x0103,1},{REG_NULL,0}};
 const struct sc031gs_regval bad_tail[]={{0x0103,1},{REG_NULL,1}};
 const struct sc031gs_regval empty[]={{REG_NULL,0}};
 writes=0;CK(write_regs(0x30,NULL,0)==-1);CK(write_regs(0x30,missing,2)==-1);
 CK(write_regs(0x30,early,3)==-1);CK(write_regs(0x30,bad_tail,2)==-1);CK(write_regs(0x30,empty,1)==-1);CK(!writes);
 sensor_t s={0};s.slv_addr=0x30;CK(!esp32_camera_sc031gs_init(&s));writes=fail_at=0;CK(!s.reset(&s)&&writes==1);
 printf("PASS %u checks: actual reset + both mode tables bounded; malformed terminal contracts rejected before writes; every table write failure stops immediately (synthetic, no physical mode qualification)\n",checks);
}
