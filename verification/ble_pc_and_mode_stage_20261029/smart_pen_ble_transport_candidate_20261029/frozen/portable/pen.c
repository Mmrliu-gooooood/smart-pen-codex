#include "pen.h"
#include <string.h>
static void put(uint8_t *p, uint64_t v, unsigned n) { for(unsigned i=0;i<n;i++) p[i]=(uint8_t)(v>>(8*i)); }
static uint64_t get(const uint8_t *p,unsigned n) { uint64_t v=0; for(unsigned i=0;i<n;i++)v|=(uint64_t)p[i]<<(8*i); return v; }
uint32_t pen_crc32(const uint8_t *p,size_t n) { uint32_t c=0xffffffffu; while(n--){c^=*p++; for(unsigned i=0;i<8;i++)c=(c>>1)^(0xedb88320u & (0u-(c&1u)));}return ~c; }
static int valid(const pen_sample *p) { return p->session!=0 && !(p->flags&~7u) && p->confidence<=1000 && (!(p->flags&PEN_VALID)||p->page!=0); }
int pen_encode(uint8_t o[PEN_PACKET_SIZE],const pen_sample *p) {
 if(!valid(p))return -1;
 memset(o,0,48);o[0]='S';o[1]='P';o[2]=1;o[3]=p->flags;
 put(o+4,p->device,4);put(o+8,p->session,8);put(o+16,p->seq,4);put(o+20,p->timestamp_us,8);put(o+28,p->page,4);
 put(o+32,(uint32_t)p->x_um,4);put(o+36,(uint32_t)p->y_um,4);put(o+40,p->confidence,2);put(o+44,pen_crc32(o,44),4);return 0;
}
/* Defined signed conversion also on hosts where uint32->int32 is implementation defined. */
static int32_t signed32(uint32_t v) { return v<=INT32_MAX?(int32_t)v:-(int32_t)(UINT32_MAX-v)-1; }
int pen_decode(pen_sample *p,const uint8_t o[PEN_PACKET_SIZE]) {
 if(o[0]!='S'||o[1]!='P'||o[2]!=1||get(o+42,2)||get(o+44,4)!=pen_crc32(o,44))return -1;
 pen_sample q={0};q.flags=o[3];q.device=(uint32_t)get(o+4,4);q.session=get(o+8,8);q.seq=(uint32_t)get(o+16,4);q.timestamp_us=get(o+20,8);q.page=(uint32_t)get(o+28,4);q.x_um=signed32((uint32_t)get(o+32,4));q.y_um=signed32((uint32_t)get(o+36,4));q.confidence=(uint16_t)get(o+40,2);
 if(!valid(&q))return -1;
 *p=q;return 0;
}
void pen_gate_apply(pen_gate *g,pen_sample *p,uint8_t raw,uint8_t calibrated,uint16_t threshold,uint32_t debounce) {
 raw=!!raw;
 if(!g->started || p->timestamp_us<g->last){memset(g,0,sizeof(*g));g->started=1;g->changed=p->timestamp_us;g->raw=raw;g->lost=1;}
 g->last=p->timestamp_us;
 if(raw!=g->raw){g->raw=raw;g->changed=p->timestamp_us;}
 /* Release is immediate; press is debounced. Never add a release tail. */
 if(!raw)g->stable=0;
 else if(p->timestamp_us-g->changed>=debounce)g->stable=1;
 p->flags=(uint8_t)((p->flags&~PEN_CONTACT)|(g->stable?PEN_CONTACT:0));
 if(!calibrated||p->confidence<threshold||!p->page||!(p->flags&PEN_VALID)) {p->flags&=(uint8_t)~PEN_VALID;g->lost=1;}
 else if(g->lost){p->flags|=PEN_GAP;g->lost=0;}
}
static const uint8_t commit[4]={'D','O','N','E'};
int pen_log_open(pen_log *l) {
 if(!l->read||!l->program||!l->sync||l->slots>SIZE_MAX/PEN_SLOT_SIZE)return -1;
 l->faulted=1;
 if(l->sync(l->ctx))return -1;
 l->next=0;
 for(size_t i=0;i<l->slots;i++) {uint8_t b[64];if(l->read(l->ctx,i*64,b,64))return -1;for(size_t j=0;j<64;j++)if(b[j]!=255){l->next=i+1;break;}}
 l->faulted=0;return 0;
}
int pen_log_append(pen_log *l,const pen_sample *p) {
 uint8_t b[48];if(l->faulted||pen_encode(b,p))return -1;
 if(l->next>=l->slots)return -2;
 size_t offset=l->next++*64;
 if(l->program(l->ctx,offset,b,48)||l->sync(l->ctx)){l->faulted=1;return -1;}
 if(l->program(l->ctx,offset+60,commit,4)||l->sync(l->ctx)){l->faulted=1;return -1;}
 return 0;
}
int pen_log_read(pen_log *l,size_t slot,pen_sample *p) {
 uint8_t b[64];if(slot>=l->slots)return -1;
 if(l->read(l->ctx,slot*64,b,64))return -1;
 if(memcmp(b+60,commit,4)||pen_decode(p,b))return 1;
 return 0;
}
