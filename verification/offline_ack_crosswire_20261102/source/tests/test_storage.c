#include "store.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t flash[64*8];static int cut=-1,count,intent,erase_cut=-1;
static int read_mem(void*c,size_t o,uint8_t*b,size_t n){(void)c;if(o+n>sizeof flash)return -1;memcpy(b,flash+o,n);return 0;}
static int program(void*c,size_t o,const uint8_t*b,size_t n){(void)c;if(o+n>sizeof flash)return -1;for(size_t i=0;i<n;i++){if(cut>=0&&count++>=cut)return -1;assert((flash[o+i]&b[i])==b[i]);flash[o+i]&=b[i];}return 0;}
static int sync_mem(void*c){(void)c;return 0;}
static int get_intent(void*c,int*v){(void)c;*v=intent;return 0;}
static int set_intent(void*c,int v){(void)c;intent=v;return 0;}
static int erase(void*c){(void)c;for(size_t i=0;i<sizeof flash;i++){if(erase_cut>=0&&(int)i==erase_cut)return -1;flash[i]=255;}return 0;}
static pen_store fresh(void){pen_store s={.log={.read=read_mem,.program=program,.sync=sync_mem,.slots=8},.get_erase_intent=get_intent,.set_erase_intent=set_intent,.erase_all=erase};return s;}
static void reset(void){memset(flash,255,sizeof flash);cut=-1;erase_cut=-1;count=0;intent=0;}
int main(void){
 pen_sample p={.timestamp_us=100,.page=1,.x_um=123,.confidence=900,.flags=3},q;
 reset();pen_store s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));assert(!pen_store_append(&s,&p,&q));assert(q.seq==0&&q.session==10&&q.device==42);
 assert(!pen_store_offer(&s,&q));assert(pen_store_ack(&s,10,0,0)==-3);assert(pen_store_ack(&s,11,0,1)==-3);assert(pen_store_ack(&s,10,1,1)==-3);
 assert(!pen_store_ack(&s,10,0,1));assert(pen_store_offer(&s,&q)==1);assert(!pen_store_append(&s,&p,&q));assert(q.seq==1);
 s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_offer(&s,&q)&&q.seq==1);assert(!pen_store_ack(&s,10,1,1));assert(pen_store_begin(&s,10)==-1);assert(!pen_store_begin(&s,11));assert(!pen_store_append(&s,&p,&q)&&q.seq==0);
 assert(pen_store_reclaim(&s,1)==-3);pen_store_stop(&s);assert(pen_store_reclaim(&s,1)==-3);assert(!pen_store_offer(&s,&q)&&q.session==11);assert(!pen_store_ack(&s,11,0,1));assert(!pen_store_reclaim(&s,1));assert(s.log.next==0&&!intent);
 /* Every interrupted ACK byte must replay after reboot; same ACK is retry-safe. */
 for(int at=0;at<12;at++){reset();s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));assert(!pen_store_append(&s,&p,&q));assert(!pen_store_offer(&s,&q));cut=at;count=0;assert(pen_store_ack(&s,10,0,1)==-1);cut=-1;s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_offer(&s,&q)&&q.seq==0);assert(!pen_store_ack(&s,10,0,1));}
 /* Every interrupted data byte leaves no invented record or missing sequence. */
 for(int at=0;at<52;at++){reset();s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));cut=at;count=0;assert(pen_store_append(&s,&p,&q)==-1);cut=-1;s=fresh();assert(!pen_store_open(&s,42));assert(pen_store_offer(&s,&q)==1);assert(!pen_store_begin(&s,11));assert(!pen_store_append(&s,&p,&q)&&q.seq==0);}
 /* Durable erase intent allows every partial erase to finish before recording. */
 for(int at=0;at<(int)sizeof flash;at++){reset();s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));assert(!pen_store_append(&s,&p,&q));assert(!pen_store_offer(&s,&q));assert(!pen_store_ack(&s,10,0,1));pen_store_stop(&s);erase_cut=at;assert(pen_store_reclaim(&s,1)==-1&&intent);erase_cut=-1;s=fresh();assert(!pen_store_open(&s,42)&&!intent&&s.log.next==0);}
 /* CRC over data+its own CRC is a fixed residue: bind only first44 bytes. */
 reset();s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));assert(!pen_store_append(&s,&p,&q));assert(!pen_store_append(&s,&p,&q));
 assert(!pen_store_offer(&s,&q)&&q.seq==0);assert(!pen_store_ack(&s,10,0,1));
 assert(memcmp(flash+44,flash+64+44,4)!=0);memcpy(flash+64+48,flash+48,12);
 s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_offer(&s,&q)&&q.seq==1);
 reset();s=fresh();assert(!pen_store_open(&s,42));assert(!pen_store_begin(&s,10));for(int i=0;i<8;i++)assert(!pen_store_append(&s,&p,&q));assert(pen_store_append(&s,&p,&q)==-2);pen_store_stop(&s);assert(pen_store_reclaim(&s,1)==-3);
 flash[32]^=1;s=fresh();assert(pen_store_open(&s,42)==-1);assert(pen_store_begin(&s,11)==-1);
 puts("storage: restart/replay/authACK/full/corruption +52 data cuts +12 ACK cuts +512 erase cuts PASS");return 0;
}
