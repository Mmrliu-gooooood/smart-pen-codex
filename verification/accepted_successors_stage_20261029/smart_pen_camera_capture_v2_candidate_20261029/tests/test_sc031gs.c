#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include "sensor.h"
#include "sc031gs.h"
static uint8_t regs[65536];
static int writes,fail_write_at,fail_read_at=-1,reads;
int SCCB_Read16_Checked(uint8_t a,uint16_t r,uint8_t*out){assert(a==0x30);reads++;*out=0;if(r==fail_read_at)return -1;*out=regs[r];return 0;}
int SCCB_Write16(uint8_t a,uint16_t r,uint8_t v){assert(a==0x30);writes++;if(writes==fail_write_at)return -1;regs[r]=v;return 0;}
int xclk_timer_conf(int a,int b){(void)a;(void)b;return 0;}
int main(void){sensor_id_t id={0};sensor_t s={0};s.slv_addr=0x30;
 regs[0x3107]=0;regs[0x3108]=0x31;
 assert(esp32_camera_sc031gs_detect(0x30,&id)==0x31);assert(id.PID==0x31);assert(!writes);
 for(int fail=0;fail<2;fail++){fail_read_at=fail?0x3108:0x3107;assert(!esp32_camera_sc031gs_detect(0x30,&id));assert(!writes);}fail_read_at=-1;
 regs[0x3108]=0x35;assert(!esp32_camera_sc031gs_detect(0x30,&id));assert(!writes);regs[0x3108]=0x31;
 assert(!esp32_camera_sc031gs_detect(0x31,&id));assert(!writes);
 assert(!esp32_camera_sc031gs_init(&s));assert(!s.set_pixformat(&s,PIXFORMAT_GRAYSCALE));assert(s.set_pixformat(&s,PIXFORMAT_RGB565));
 assert(s.set_framesize(&s,(framesize_t)-1));assert(s.set_framesize(&s,FRAMESIZE_INVALID));assert(!writes);
 fail_write_at=1;assert(s.set_framesize(&s,FRAMESIZE_VGA));assert(writes==1);
 writes=0;fail_write_at=2;assert(s.set_framesize(&s,FRAMESIZE_VGA));assert(writes==2);
 writes=0;fail_write_at=0;assert(!s.set_framesize(&s,FRAMESIZE_VGA));assert(regs[0x3208]==2&&regs[0x3209]==128&&regs[0x320a]==1&&regs[0x320b]==224);
 int count=writes;writes=0;fail_read_at=0x3208;assert(s.set_framesize(&s,FRAMESIZE_VGA));assert(writes==count-4);fail_read_at=-1;
 fail_read_at=0x3107;assert(s.get_reg(&s,0x3107,0xff)<0);
 puts("PASS SC031GS actual patched source: checked ID, wrong sensor, I2C failures, enum bounds, mode-table failure propagation, VGA window readback");}
