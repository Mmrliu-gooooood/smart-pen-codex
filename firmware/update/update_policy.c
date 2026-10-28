#include "update_policy.h"
#include <string.h>
bool pen_update_safe(const pen_update_safety *s){return s&&s->authorized&&s->contact_up&&s->power_qualified&&s->storage_durable&&s->recording_idle;}
static bool text_equal(const char a[32],const char *b){return b&&memchr(a,0,32)&&strlen(b)<32&&!strcmp(a,b);}
int pen_update_start(pen_update_transaction *t,const pen_update_policy *p,const pen_update_manifest *m,const pen_update_safety *s){
 if(!t||!p||!m||t->state!=PEN_UPDATE_IDLE)return -1;
 if(!p->enabled||!p->signatures_enforced||!p->rollback_enabled||p->pending_verify||!pen_update_safe(s)||
 !m->bytes||m->bytes>p->partition_bytes||m->version<=p->minimum_version||m->version<=p->running_version||
 !text_equal(m->project,p->project)||!text_equal(m->hardware,p->hardware)||strcmp(m->project,m->hardware))return -1;
 t->state=PEN_UPDATE_WRITING;t->expected_bytes=m->bytes;t->received=0;t->version=m->version;return 0;
}
int pen_update_chunk(pen_update_transaction *t,uint32_t offset,size_t bytes,const pen_update_safety *s){
 if(!t||t->state!=PEN_UPDATE_WRITING)return -1;
 if(!pen_update_safe(s)||offset!=t->received||!bytes||t->received>t->expected_bytes||bytes>t->expected_bytes-t->received){t->state=PEN_UPDATE_FAILED;return -1;}
 t->received+=(uint32_t)bytes;return 0;
}
int pen_update_finish(pen_update_transaction *t,bool digest,bool signed_descriptor,const pen_update_safety *s){
 if(!t||t->state!=PEN_UPDATE_WRITING)return -1;
 if(!pen_update_safe(s)||t->received!=t->expected_bytes||!digest||!signed_descriptor){t->state=PEN_UPDATE_FAILED;return -1;}
 t->state=PEN_UPDATE_READY;return 0;
}
bool pen_update_boot_healthy(uint32_t passed,const pen_update_safety *s){return pen_update_safe(s)&&(passed&PEN_UPDATE_REQUIRED_TESTS)==PEN_UPDATE_REQUIRED_TESTS;}

int pen_update_version_parse(const char text[32],uint32_t *version){
 if(!text||!version||!text[0])return -1;
 uint32_t v=0;
 for(unsigned i=0;i<32;i++){
  unsigned char c=(unsigned char)text[i];
  if(!c){if(i>1&&text[0]=='0')return -1;*version=v;return 0;}
  if(c<'0'||c>'9'||v>(UINT32_MAX-(uint32_t)(c-'0'))/10u)return -1;
  v=v*10u+(uint32_t)(c-'0');
 }
 return -1;
}
