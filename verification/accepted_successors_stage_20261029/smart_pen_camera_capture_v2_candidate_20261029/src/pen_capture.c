#include "pen_capture.h"
#include <string.h>
#include <limits.h>
int pen_capture_clock_plan(uint32_t requested,pen_capture_clock *o) {
 if(!o)return PC_CLOCK;
 memset(o,0,sizeof(*o));o->requested_hz=requested;o->source_hz=160000000u;
 if(!requested)return PC_CLOCK;
 o->divider=o->source_hz/requested;
 if(o->divider<2||o->divider>255)return PC_CLOCK;
 o->actual_hz=o->source_hz/o->divider;o->remainder=o->source_hz%o->divider;
 return (o->remainder||o->actual_hz!=requested)?PC_CLOCK:PC_OK;
}
int pen_capture_profile_validate(const pen_capture_profile *p) {
 pen_capture_clock c;int pins[14];
 if(!p||!p->name||!p->name[0]||!p->review_reference||!p->review_reference[0]||!p->source_id||
 !p->electrical_reviewed||!p->scope_reviewed||!p->psram_reviewed||!p->power_sequence_reviewed||
 !p->prepare_safe||!p->power_on||!p->power_off||!p->control_gpios||!p->control_count||p->control_count>16)return PC_PROFILE;
 if(p->expected_pid!=PEN_CAPTURE_SENSOR_PID)return PC_SENSOR;
 if(p->requested_xclk_hz!=PEN_CAPTURE_XCLK_HZ)return PC_MODE;
 if(pen_capture_clock_plan(p->requested_xclk_hz,&c))return PC_CLOCK;
 if(!p->measured_pclk_hz||p->measured_pclk_hz>PEN_CAPTURE_PCLK_CAP_HZ)return PC_CLOCK;
 for(unsigned i=0;i<8;i++)pins[i]=p->d[i];
 pins[8]=p->xclk;pins[9]=p->pclk;pins[10]=p->vsync;pins[11]=p->href;pins[12]=p->sda;pins[13]=p->scl;
 for(unsigned i=0;i<14;i++) {
  if(pins[i]<0||pins[i]>48)return PC_PROFILE;
  for(unsigned j=0;j<i;j++)if(pins[i]==pins[j])return PC_PROFILE;
 }
 for(size_t i=0;i<p->control_count;i++) {
  if(p->control_gpios[i]<0||p->control_gpios[i]>48)return PC_PROFILE;
  for(unsigned j=0;j<14;j++)if(p->control_gpios[i]==pins[j])return PC_PROFILE;
  for(size_t j=0;j<i;j++)if(p->control_gpios[i]==p->control_gpios[j])return PC_PROFILE;
 }
 return PC_OK;
}
void pen_capture_construct(pen_capture *c,const pen_capture_backend *b,void *ctx) {
 if(!c)return;
 memset(c,0,sizeof(*c));c->ops=b;c->backend_ctx=ctx;c->state=PC_STOPPED;
}
static int close_owned(pen_capture *c) {
 int rc=0;
 if(c->held.owner) {c->ops->give(c->backend_ctx,c->held.owner);memset(&c->held,0,sizeof(c->held));}
 if(c->opened){rc=c->ops->close(c->backend_ctx);c->opened=0;if(rc)c->cleanup_failed=1;}
 return rc;
}
static int fail(pen_capture *c,int why) {
 if(close_owned(c))why=PC_DRIVER;
 c->state=PC_FAULT;c->last_error=why;return why;
}
int pen_capture_start_checked(pen_capture *c,const pen_capture_profile *p,int enabled) {
 int rc;uint16_t pid=0;pen_capture_clock clock={0};
 if(!c||!c->ops||!c->ops->open||!c->ops->close||!c->ops->take||!c->ops->give||!c->ops->now_us)return PC_STATE;
 if(!enabled)return PC_DISABLED;
 if(c->state!=PC_STOPPED||c->opened||c->cleanup_failed)return PC_STATE;
 if((rc=pen_capture_profile_validate(p)))return rc;
 c->profile=p;c->source_id=p->source_id;c->opened=1;
 if((rc=c->ops->open(c->backend_ctx,p,&pid,&clock)))return fail(c,rc);
 if(pid!=PEN_CAPTURE_SENSOR_PID)return fail(c,PC_SENSOR);
 c->clock=clock;
 if(clock.requested_hz!=PEN_CAPTURE_XCLK_HZ||clock.source_hz!=160000000u||clock.divider!=16||clock.actual_hz!=PEN_CAPTURE_XCLK_HZ||clock.remainder)return fail(c,PC_CLOCK);
 c->state=PC_RUNNING;c->timeouts=0;c->last_error=0;return PC_OK;
}
int pen_capture_get(pen_capture *c,uint32_t ms,pen_capture_view *out) {
 pen_capture_raw raw={0};int rc;uint64_t now;
 if(!out)return PC_FRAME;
 memset(out,0,sizeof(*out));
 if(!c||c->state!=PC_RUNNING)return PC_STATE;
 if(!ms||ms>PEN_CAPTURE_GET_MAX_MS)return PC_MODE;
 rc=c->ops->take(c->backend_ctx,ms,&raw);
 /* Even an erroneous backend must not leak an accidentally supplied owner. */
 if(rc) {
  if(raw.owner)c->ops->give(c->backend_ctx,raw.owner);
  if(rc==PC_TIMEOUT){if(++c->timeouts<3)return PC_TIMEOUT;return fail(c,PC_TIMEOUT_FATAL);}
  return fail(c,rc);
 }
 c->held=raw;
 if(!raw.owner||!raw.data||!raw.gray8||raw.width!=PEN_CAPTURE_WIDTH||raw.height!=PEN_CAPTURE_HEIGHT||raw.stride!=PEN_CAPTURE_WIDTH||raw.bytes!=PEN_CAPTURE_BYTES)return fail(c,PC_FRAME);
 now=c->ops->now_us(c->backend_ctx);
 if(!raw.timestamp_us||raw.timestamp_us<=c->last_timestamp_us||raw.timestamp_us>now||now-raw.timestamp_us>200000u)return fail(c,PC_STALE);
 if(c->next_frame_id==UINT64_MAX)return fail(c,PC_OWNERSHIP);
 c->last_timestamp_us=raw.timestamp_us;c->next_frame_id++;c->timeouts=0;c->state=PC_HELD;
 *out=(pen_capture_view){raw.data,raw.bytes,640,480,640,raw.timestamp_us,c->next_frame_id,c->source_id,raw.synthetic};
 return PC_OK;
}
int pen_capture_release(pen_capture *c,uint64_t id) {
 if(!c||c->state!=PC_HELD||!id||id!=c->next_frame_id)return PC_OWNERSHIP;
 c->ops->give(c->backend_ctx,c->held.owner);memset(&c->held,0,sizeof(c->held));c->state=PC_RUNNING;return PC_OK;
}
int pen_capture_stop(pen_capture *c) {
 if(!c||!c->ops)return PC_STATE;
 if(c->cleanup_failed)return PC_DRIVER;
 if(close_owned(c)){c->state=PC_FAULT;c->last_error=PC_DRIVER;return PC_DRIVER;}
 c->state=PC_STOPPED;c->timeouts=0;return PC_OK;
}
