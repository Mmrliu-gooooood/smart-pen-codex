#include <assert.h>
#include <stdio.h>
#include "../third_party/esp32-camera/driver/sccb-ng.c"
static int transport_rc,calls;
int i2c_master_transmit_receive(i2c_master_dev_handle_t h,const uint8_t*t,size_t n,uint8_t*r,size_t m,int timeout){
 assert(h==(void*)1&&n==2&&m==1&&t[0]==0x31&&t[1]==0x07&&timeout==1000);calls++;*r=0x31;return transport_rc;}
int main(void){uint8_t value=0xff;
 assert(SCCB_Read16_Checked(0x30,0x3107,&value)==-1&&value==0&&!calls);
 devices[0].address=0x30;devices[0].dev_handle=(void*)1;device_count=1;
 assert(SCCB_Read16_Checked(0x30,0x3107,NULL)==-1&&!calls);
 transport_rc=-1;value=0xff;assert(SCCB_Read16_Checked(0x30,0x3107,&value)==-1&&value==0&&calls==1);
 transport_rc=0;assert(!SCCB_Read16_Checked(0x30,0x3107,&value)&&value==0x31&&calls==2);
 puts("PASS actual sccb-ng checked-read source: no handle/null/error always rejected, success returns exact byte");}
