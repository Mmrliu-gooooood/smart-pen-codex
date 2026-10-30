/* Compiles against frozen REAL portable codec + BLE core, not a restated codec. */
#include "pen_ble_core.h"
#include <stdio.h>
#include <string.h>
static int emit(void *ctx,const uint8_t *p,size_t n,uint64_t epoch){
 (void)ctx;if(n!=20||epoch!=99)return -1;
 for(size_t i=0;i<n;i++)printf("%02x",p[i]);
 putchar('\n');return 0;
}
int main(int argc,char **argv){
 if(argc!=2||strlen(argv[1])!=40)return 10;
 uint8_t ack[20];for(unsigned i=0;i<20;i++){unsigned x;if(sscanf(argv[1]+i*2,"%2x",&x)!=1)return 11;ack[i]=(uint8_t)x;}
 pen_sample p={.device=42,.session=UINT64_MAX,.seq=65536,.timestamp_us=10,.page=9,.x_um=-1234,.y_um=5678,.confidence=1000,.flags=7};
 uint8_t raw[48];if(pen_encode(raw,&p))return 12;
 for(unsigned i=0;i<48;i++)printf("%02x",raw[i]);
 putchar('\n');
 pen_ble_core c;pen_ble_core_init(&c);
 pen_link_security s={.encrypted=1,.authenticated=1,.bonded=1,.approved_peer=1,.connection_epoch=99};
 pen_ble_core_link(&c,&s,16);pen_ble_core_subscribe(&c,1);
 if(pen_ble_core_receive(&c,ack,20,0)!=-3)return 13; /* before full offer */
 if(pen_ble_core_send(&c,raw,48,99,1,emit,NULL))return 14;
 if(pen_ble_core_receive(&c,ack,20,2))return 15;
 pen_ble_ack a;if(pen_ble_core_pop(&c,&a)||a.session!=p.session||a.seq!=p.seq)return 16;
 puts("C exact ACK accepted after full frozen offer");return 0;
}
