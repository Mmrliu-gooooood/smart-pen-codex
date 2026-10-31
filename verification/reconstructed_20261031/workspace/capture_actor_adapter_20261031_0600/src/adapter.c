#include "adapter.h"
#include <string.h>
int pa_init(pen_adapter*a,pen_capture*c,pa_sink s,pa_fault_sink f,void*x,int e){
 if(!a)return PA_INPUT;
 if(a->enabled||a->busy||a->faulted||a->has_frame)return PA_STATE;
 memset(a,0,sizeof(*a));
 if(!PEN_ADAPTER_HOST_TEST||!e)return PA_DISABLED;
 if(!c||!s||!f)return PA_INPUT;
 a->capture=c;a->sink=s;a->fault_sink=f;a->ctx=x;a->enabled=1;return PA_OK;
}

static int fail(pen_adapter*a,int code){
 a->faulted=1;a->binding=0;a->count=0;a->has_frame=0;
 if(a->capture&&a->capture->ops&&pen_capture_stop(a->capture)!=PC_OK)code=PA_LEASE;
 a->busy=1;a->fault_sink(a->ctx,code);a->busy=0;return code;
}
static int ready(const pen_adapter*a){return a&&a->enabled&&!a->faulted&&!a->busy;}
static int enqueue(pen_adapter*a,pa_event e){
 if(!ready(a))return PA_STATE;
 if(!e.time)return fail(a,PA_INPUT);
 if(a->sealed_valid&&e.time<=a->sealed)return fail(a,PA_LATE);
 if(a->count==PA_CAPACITY)return fail(a,PA_FULL);
 size_t n=a->count;
 while(n&&(a->queue[n-1].time>e.time||(a->queue[n-1].time==e.time&&a->queue[n-1].kind>e.kind))){a->queue[n]=a->queue[n-1];n--;}
 a->queue[n]=e;a->count++;return PA_OK;
}
int pa_edge(pen_adapter*a,uint64_t t,uint8_t c,uint8_t i){
 if(!ready(a))return PA_STATE;
 if(c>1||i>1)return fail(a,PA_INPUT);
 return enqueue(a,(pa_event){.time=t,.kind=PA_EDGE,.contact=c,.irq=i});
}
int pa_idle(pen_adapter*a,uint64_t t){return enqueue(a,(pa_event){.time=t,.kind=PA_IDLE});}
int pa_drain(pen_adapter*a,uint64_t t){
 if(!ready(a))return PA_STATE;
 if(!t||(a->sealed_valid&&t<a->sealed))return fail(a,PA_LATE);
 a->busy=1;
 while(a->count&&a->queue[0].time<=t){
  pa_event e=a->queue[0];a->count--;memmove(a->queue,a->queue+1,a->count*sizeof(a->queue[0]));
  if(e.kind==PA_EDGE){a->contact=e.contact;a->irq=e.irq;}
  pen_app_input in={.now_us=e.time,.raw_contact=a->contact,.pickup_irq_low=a->irq,.camera_ready=(uint8_t)(a->capture->state==PC_RUNNING||a->capture->state==PC_HELD)};
  if(e.kind==PA_FRAME){
   if(pen_capture_app_roi(a->capture,&e.view,e.left,e.top,e.width,e.height,&a->active_frame,&a->active_origin)!=PC_OK){a->busy=0;return fail(a,PA_LEASE);}
   a->active_view=e.view;a->binding=1;in.frame=&a->active_frame;in.camera_ready=1;
  }
  if(a->sink(a->ctx,&in)){a->busy=0;return fail(a,PA_SINK);}
  a->binding=0;
  if(e.kind==PA_FRAME){
   a->has_frame=0;
   if(pen_capture_release(a->capture,e.view.frame_id)!=PC_OK){a->busy=0;return fail(a,PA_LEASE);}
  }
 }
 a->busy=0;a->sealed=t;a->sealed_valid=1;return PA_OK;
}

int pa_frame(pen_adapter*a,const pen_capture_view*v,unsigned l,unsigned t,unsigned w,unsigned h){
 if(!ready(a))return PA_STATE;
 if(!v||a->has_frame)return fail(a,PA_LEASE);
 pen_app_frame f;pen_capture_roi_origin o;
 if(!v->synthetic||pen_capture_app_roi(a->capture,v,l,t,w,h,&f,&o)!=PC_OK)return fail(a,PA_LEASE);
 int rc=enqueue(a,(pa_event){.time=v->timestamp_us,.kind=PA_FRAME,.view=*v,.left=l,.top=t,.width=w,.height=h});
 if(!rc)a->has_frame=1;
 return rc;
}
int pa_origin(const pen_adapter*a,const pen_app_frame*f,pen_capture_roi_origin*o){
 if(!o)return PA_INPUT;
 memset(o,0,sizeof(*o));
 if(!a||!f||!a->binding||!a->busy||a->faulted||f!=&a->active_frame||f->frame_id!=a->active_origin.parent_frame_id||f->source_id!=a->active_origin.source_id)return PA_LEASE;
 pen_app_frame check;
 if(pen_capture_app_frame(a->capture,&a->active_view,&check)!=PC_OK||check.timestamp_us!=f->timestamp_us)return PA_LEASE;
 *o=a->active_origin;return PA_OK;
}
int pa_stop(pen_adapter*a){
 if(!a||a->busy)return PA_STATE;
 a->enabled=0;a->binding=0;a->count=0;a->has_frame=0;
 if(a->capture&&a->capture->ops&&pen_capture_stop(a->capture)!=PC_OK)return fail(a,PA_LEASE);
 return PA_OK;
}
