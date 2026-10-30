#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void tracked_free(void *);
#define free tracked_free
#define PEN_CAMERA_GRAY_ONLY_BUILD 1
#include "../third_party/esp32-camera/driver/cam_hal.c"
#undef free
static unsigned checks;
#define CK(x) do { checks++;assert(x); }while(0)
static void *live[32];static int live_n,alloc_n,fail_alloc,fail_task,fail_isr,task_creates,task_deletes,queue_deletes,ll_deinits,stops,resets,cache_calls;
static int timestamp_order;
static TickType_t now;static int receive_mode,receive_n;static camera_fb_t *queued_frame;
static void *alloc(size_t n){alloc_n++;if(alloc_n==fail_alloc)return NULL;void*p=calloc(1,n);CK(p&&live_n<32);live[live_n++]=p;return p;}
static void tracked_free(void*p){if(!p)return;int i;for(i=0;i<live_n;i++)if(live[i]==p)break;CK(i<live_n);live[i]=live[--live_n];free(p);}
void *heap_caps_malloc(size_t n,uint32_t c){(void)c;return alloc(n);}
void *heap_caps_calloc(size_t a,size_t b,uint32_t c){(void)c;return alloc(a*b);}
void *heap_caps_aligned_calloc(size_t a,size_t b,size_t c,uint32_t d){(void)a;(void)d;return alloc(b*c);}
void *heap_caps_aligned_alloc(size_t a,size_t b,uint32_t c){(void)a;(void)c;return alloc(b);}
size_t heap_caps_get_largest_free_block(uint32_t c){(void)c;return 1000000;}
QueueHandle_t xQueueCreate(size_t a,size_t b){CK(a&&b);return alloc(8);}
void vQueueDelete(QueueHandle_t q){queue_deletes++;tracked_free(q);}
BaseType_t xTaskCreatePinnedToCore(void(*fn)(void*),const char*n,unsigned sz,void*arg,unsigned prio,TaskHandle_t*out,int core){(void)fn;(void)n;(void)arg;(void)prio;CK(sz==4096&&core==0);task_creates++;if(fail_task)return pdFALSE;*out=alloc(8);return *out?pdPASS:pdFALSE;}
void vTaskDelete(TaskHandle_t t){task_deletes++;tracked_free(t);}
TickType_t xTaskGetTickCount(void){return now;}
void vTaskDelay(int t){CK(t>=0);now+=(TickType_t)t;}
BaseType_t xQueueReceive(QueueHandle_t q,void*out,TickType_t timeout){CK(q!=NULL&&timeout!=0);receive_n++;if(receive_mode==0){now+=timeout;return pdFALSE;}*(camera_fb_t**)out=receive_mode==1?NULL:queued_frame;return pdTRUE;}
BaseType_t xQueueSend(QueueHandle_t q,const void*v,TickType_t t){(void)q;(void)v;(void)t;return pdTRUE;}
BaseType_t xQueueSendFromISR(QueueHandle_t q,const void*v,BaseType_t*t){(void)q;(void)v;(void)t;return pdTRUE;}
void xQueueReset(QueueHandle_t q){(void)q;}
UBaseType_t uxQueueMessagesWaiting(QueueHandle_t q){(void)q;return 0;}
int64_t esp_timer_get_time(void){CK(timestamp_order==2);timestamp_order=3;return 1000000;}
int esp_cache_msync(void*a,size_t b,int c){(void)a;(void)b;(void)c;cache_calls++;return 0;}
size_t cache_hal_get_cache_line_size(int a,int b){(void)a;(void)b;return 32;}
esp_err_t ll_cam_set_pin(cam_obj_t*c,const camera_config_t*k){(void)c;(void)k;return ESP_OK;}
esp_err_t ll_cam_config(cam_obj_t*c,const camera_config_t*k){(void)c;(void)k;return ESP_OK;}
esp_err_t ll_cam_set_sample_mode(cam_obj_t*c,pixformat_t f,uint32_t x,uint16_t pid){CK(f==PIXFORMAT_GRAYSCALE&&x==10000000&&pid==0x31);c->in_bytes_per_pixel=1;c->fb_bytes_per_pixel=1;c->dma_bytes_per_item=1;return ESP_OK;}
bool ll_cam_dma_sizes(cam_obj_t*c){CK(c->fb_size==307200);c->dma_buffer_size=30720;c->dma_half_buffer_size=15360;c->dma_half_buffer_cnt=2;c->dma_node_buffer_size=3840;return true;}
uint8_t ll_cam_get_dma_align(cam_obj_t*c){(void)c;return 16;}
esp_err_t ll_cam_init_isr(cam_obj_t*c){(void)c;return fail_isr?ESP_FAIL:ESP_OK;}
esp_err_t ll_cam_deinit(cam_obj_t*c){CK(c!=NULL);ll_deinits++;return ESP_OK;}
void ll_cam_vsync_intr_enable(cam_obj_t*c,bool e){CK(c!=NULL);(void)e;}
bool ll_cam_stop(cam_obj_t*c){CK(c!=NULL);stops++;return true;}
bool ll_cam_start(cam_obj_t*c,int f){(void)c;(void)f;CK(timestamp_order==0);timestamp_order=1;return true;}
void ll_cam_do_vsync(cam_obj_t*c){(void)c;CK(timestamp_order==1);timestamp_order=2;}
void ll_cam_dma_reset(cam_obj_t*c){CK(c!=NULL);resets++;}
size_t ll_cam_memcpy(cam_obj_t*c,uint8_t*out,const uint8_t*in,size_t len){(void)c;memcpy(out,in,len);return len;}
static camera_config_t cfg={.pin_vsync=11,.xclk_freq_hz=10000000,.pixel_format=PIXFORMAT_GRAYSCALE,.frame_size=FRAMESIZE_VGA,.fb_count=1,.fb_location=CAMERA_FB_IN_PSRAM,.grab_mode=CAMERA_GRAB_WHEN_EMPTY};
static void reset_mock(void){CK(!cam_obj&&!live_n);alloc_n=fail_alloc=fail_task=fail_isr=task_creates=task_deletes=queue_deletes=ll_deinits=stops=resets=cache_calls=receive_n=receive_mode=0;now=0;timestamp_order=0;queued_frame=NULL;}
static void begin(void){CK(!cam_init(&cfg));CK(!cam_config(&cfg,FRAMESIZE_VGA,0x31));}
int main(void){
 /* Actual v2 HAL source (v1 task-create check retained), ll_cam modeled. */
 for(int f=1;f<=8;f++){reset_mock();fail_alloc=f;int rc=cam_init(&cfg);if(!rc)rc=cam_config(&cfg,FRAMESIZE_VGA,0x31);CK(rc!=ESP_OK);CK(!cam_obj&&!live_n);CK(cam_deinit()==ESP_FAIL);}
 reset_mock();fail_task=1;CK(!cam_init(&cfg));CK(cam_config(&cfg,FRAMESIZE_VGA,0x31)==ESP_FAIL);CK(!cam_obj&&!live_n&&task_creates==1&&!task_deletes&&queue_deletes==2&&ll_deinits==1&&stops==1);
 reset_mock();fail_isr=1;CK(!cam_init(&cfg));CK(cam_config(&cfg,FRAMESIZE_VGA,0x31)==ESP_FAIL);CK(!cam_obj&&!live_n&&!task_creates&&queue_deletes==2&&ll_deinits==1);
 reset_mock();begin();int pos=0;CK(cam_start_frame(&pos));CK(timestamp_order==3&&cam_obj->frames[0].fb.timestamp.tv_sec==1&&cam_obj->frames[0].fb.timestamp.tv_usec==0);CK(cam_obj->dma_node_cnt==8&&cam_obj->frame_copy_cnt==20&&cam_obj->fb_size==307200);CK(cam_take(200)==NULL);CK(now==200&&receive_n==1);
 now=UINT32_MAX-5;receive_n=0;CK(cam_take(10)==NULL);CK(now==4&&receive_n==1);
 now=0;receive_mode=1;receive_n=0;CK(cam_take(200)==NULL);CK(now==200&&resets==3&&receive_n==203);
 receive_mode=2;queued_frame=&cam_obj->frames[0].fb;cam_obj->frames[0].en=0;queued_frame->len=307200;CK(cam_take(1)==queued_frame);CK(!cache_calls&&!cam_obj->frames[0].en);cam_give(queued_frame);CK(cam_obj->frames[0].en==1);
 CK(!cam_deinit());CK(!cam_obj&&!live_n&&task_deletes==1&&queue_deletes==2&&ll_deinits==1);CK(cam_deinit()==ESP_FAIL);
 printf("PASS actual HAL source: %u checks, 8 allocation failures + task/ISR failure cleanup + timeout budget/tick wrap/3 GDMA reset cap + single-fb CPU-copy ownership + HAL software timestamp ordering; mocked ll_cam, not hardware proof\n",checks);
}
