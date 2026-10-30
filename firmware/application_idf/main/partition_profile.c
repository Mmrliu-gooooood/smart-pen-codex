#include "partition_profile.h"
#include <string.h>
static const pen_partition_description expected[PEN_PROFILE8_PARTITIONS] = {
 {"nvs",0x9000,0x6000,1,2,0,0},
 {"otadata",0xf000,0x2000,1,0,0,0},
 {"phy_init",0x11000,0x1000,1,1,0,0},
 {"ota_0",0x20000,0x200000,0,0x10,0,0},
 {"ota_1",0x220000,0x200000,0,0x11,0,0},
 {"pen_records",0x420000,0x3e0000,1,0x40,0,0}
};
int pen_profile8_validate(uint32_t physical_bytes,uint32_t logical_bytes,
 const pen_partition_description *parts,size_t count) {
 if(physical_bytes!=PEN_PROFILE8_FLASH_BYTES || logical_bytes!=PEN_PROFILE8_FLASH_BYTES ||
    !parts || count!=PEN_PROFILE8_PARTITIONS) return -1;
 unsigned seen=0;
 for(size_t i=0;i<count;i++) {
  const pen_partition_description *p=parts+i;
  if(!p->label || p->encrypted || p->readonly || !p->size || p->address>physical_bytes ||
     p->size>physical_bytes-p->address || p->address%4096 || p->size%4096 ||
     (p->type==0 && p->address%65536)) return -1;
  unsigned found=PEN_PROFILE8_PARTITIONS;
  for(unsigned j=0;j<PEN_PROFILE8_PARTITIONS;j++) {
   if(!strcmp(p->label,expected[j].label)) {found=j;break;}
  }
  if(found==PEN_PROFILE8_PARTITIONS || (seen&(1u<<found))) return -1;
  const pen_partition_description *e=expected+found;
  if(p->address!=e->address || p->size!=e->size || p->type!=e->type || p->subtype!=e->subtype) return -1;
  seen|=1u<<found;
  for(size_t k=0;k<i;k++) {
   if(p->address<parts[k].address+parts[k].size && parts[k].address<p->address+p->size) return -1;
  }
 }
 return seen==((1u<<PEN_PROFILE8_PARTITIONS)-1u)?0:-1;
}
