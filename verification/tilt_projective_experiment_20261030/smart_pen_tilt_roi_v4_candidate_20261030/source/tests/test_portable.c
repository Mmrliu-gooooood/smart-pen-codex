#include "pen.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t flash[256];static int fail;static int sync_calls,fail_on_sync;static int cut_after=-1,written;
static int rd(void*c,size_t o,uint8_t*b,size_t n){(void)c;memcpy(b,flash+o,n);return 0;}
static int wr(void*c,size_t o,const uint8_t*b,size_t n){(void)c;for(size_t i=0;i<n;i++){if(cut_after>=0&&written++>=cut_after)return -1;if(fail==1&&i==n/2)return -1;assert((flash[o+i]&b[i])==b[i]);flash[o+i]&=b[i];}return 0;}
static int sync_flash(void*c){(void)c;sync_calls++;return fail==2||(fail_on_sync&&sync_calls==fail_on_sync)?-1:0;}
int main(void){
 pen_sample p={.device=42,.session=123,.seq=0,.timestamp_us=100,.page=7,.x_um=-123,.y_um=456,.confidence=950,.flags=3},q;
 uint8_t b[48];assert(pen_crc32((const uint8_t*)"123456789",9)==0xcbf43926u);assert(!pen_encode(b,&p));assert(!pen_decode(&q,b));assert(q.x_um==-123&&q.session==123);
 for(size_t i=0;i<48;i++){b[i]^=1;assert(pen_decode(&q,b));b[i]^=1;}
 pen_gate g={0};pen_gate_apply(&g,&p,1,1,750,5000);assert(!(p.flags&PEN_CONTACT));p.timestamp_us+=5000;pen_gate_apply(&g,&p,1,1,750,5000);assert(p.flags&PEN_CONTACT);
 pen_gate_apply(&g,&p,0,1,750,5000);assert(!(p.flags&PEN_CONTACT));p.flags|=PEN_VALID;pen_gate_apply(&g,&p,1,0,750,5000);assert(!(p.flags&PEN_VALID));p.flags=PEN_VALID;p.timestamp_us+=5000;pen_gate_apply(&g,&p,1,1,750,5000);assert(p.flags&PEN_GAP);
 memset(flash,255,sizeof(flash));pen_log l={.read=rd,.program=wr,.sync=sync_flash,.slots=4};assert(!pen_log_open(&l));assert(!pen_log_append(&l,&p));assert(!pen_log_read(&l,0,&q));fail=1;assert(pen_log_append(&l,&p)==-1);fail=0;assert(pen_log_append(&l,&p)==-1);assert(!pen_log_open(&l)&&l.next==2);assert(pen_log_read(&l,1,&q)==1);assert(!pen_log_append(&l,&p));fail=2;assert(pen_log_append(&l,&p)==-1);fail=0;assert(!pen_log_open(&l)&&l.next==4);assert(pen_log_append(&l,&p)==-2);assert(pen_log_read(&l,3,&q)==1);
 memset(flash,255,sizeof(flash));assert(!pen_log_open(&l));sync_calls=0;fail_on_sync=2;assert(pen_log_append(&l,&p)==-1);assert(l.faulted);assert(pen_log_read(&l,0,&q)==0);assert(pen_log_append(&l,&p)==-1);fail_on_sync=0;assert(!pen_log_open(&l)&&l.next==1);assert(!pen_log_read(&l,0,&q));
 for(int cut=0;cut<52;cut++){memset(flash,255,sizeof(flash));cut_after=-1;assert(!pen_log_open(&l));written=0;cut_after=cut;assert(pen_log_append(&l,&p)==-1);cut_after=-1;assert(!pen_log_open(&l));assert(pen_log_read(&l,0,&q)==1);}
 puts("portable: CRC, all-byte corruption, contact, calibration, torn write, sync failure, reboot, full PASS");return 0;
}
