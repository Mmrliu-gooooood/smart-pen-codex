#include "pen_capture_app.h"
#include <string.h>
int pen_capture_app_frame(const pen_capture *c,const pen_capture_view *v,pen_app_frame *out) {
 if(!out)return PC_FRAME;
 memset(out,0,sizeof(*out));
 if(!c||!v||c->state!=PC_HELD||v->frame_id!=c->next_frame_id||v->gray!=c->held.data||v->timestamp_us!=c->held.timestamp_us||v->length!=PEN_CAPTURE_BYTES||v->source_id!=c->source_id||v->synthetic!=c->held.synthetic)return PC_OWNERSHIP;
 *out=(pen_app_frame){c->held.data,c->held.bytes,640,480,640,c->held.timestamp_us,c->next_frame_id,c->source_id,c->held.synthetic?PEN_FRAME_SYNTHETIC:PEN_FRAME_SENSOR};
 return PC_OK;
}
void pen_capture_app_disqualify(pen_app_config *c) {
 if(c){c->camera_qualified=0;c->map_tip=NULL;c->map_ctx=NULL;c->calibration_revision=0;}
}

int pen_capture_app_roi(const pen_capture *c,const pen_capture_view *v,unsigned left,
 unsigned top,unsigned width,unsigned height,pen_app_frame *out,pen_capture_roi_origin *origin) {
 pen_app_frame full;size_t offset,need;
 if(out)memset(out,0,sizeof(*out));
 if(origin)memset(origin,0,sizeof(*origin));
 if(!out||!origin)return PC_FRAME;
 int rc=pen_capture_app_frame(c,v,&full);
 if(rc)return rc;
 if(width<96||height<96||width>256||height>256||left>full.width||top>full.height||width>full.width-left||height>full.height-top)return PC_FRAME;
 offset=(size_t)top*full.stride+left;
 need=(size_t)(height-1u)*full.stride+width;
 if(offset>full.length||need>full.length-offset)return PC_FRAME;
 *out=full;out->gray=full.gray+offset;out->width=width;out->height=height;out->length=need;
 *origin=(pen_capture_roi_origin){full.width,full.height,full.stride,left,top,full.frame_id,full.source_id};
 return PC_OK;
}
