#include "pen_capture_idf.h"
#include "esp_camera.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "soc/lcd_cam_struct.h"
#include "sdkconfig.h"
#include <string.h>
#if !CONFIG_IDF_TARGET_ESP32S3
#error "Capture candidate is ESP32-S3 only"
#endif
#if !CONFIG_SC031GS_SUPPORT
#error "SC031GS support required"
#endif
#if CONFIG_OV2640_SUPPORT || CONFIG_OV7670_SUPPORT || CONFIG_OV7725_SUPPORT || CONFIG_NT99141_SUPPORT || CONFIG_OV3660_SUPPORT || CONFIG_OV3640_SUPPORT || CONFIG_OV5640_SUPPORT || CONFIG_GC2145_SUPPORT || CONFIG_GC032A_SUPPORT || CONFIG_GC0308_SUPPORT || CONFIG_BF3005_SUPPORT || CONFIG_BF20A6_SUPPORT || CONFIG_SC101IOT_SUPPORT || CONFIG_SC030IOT_SUPPORT || CONFIG_HM1055_SUPPORT || CONFIG_HM0360_SUPPORT || CONFIG_MEGA_CCM_SUPPORT
#error "Only SC031GS detection/init may be enabled"
#endif
#if CONFIG_CAMERA_PSRAM_DMA || CONFIG_CAMERA_CONVERTER_ENABLED
#error "Only CPU-copy Gray8 path is qualified for this software candidate"
#endif
static const char *TAG="pen_capture";
typedef struct { const pen_capture_profile *p; uint8_t powered,initialized,retired; } idf_backend;
static idf_backend hw;
static pen_capture instance;
static int ready;
static int start_armed;
static int hw_close(void *ctx) {
 idf_backend *h=ctx;int rc=0;
 if(h->initialized){if(esp_camera_deinit()!=ESP_OK)rc=PC_DRIVER;h->initialized=0;}
 /* esp_camera deinit does not guarantee XCLK pin disconnect/rails safe. The
  * reviewed hook MUST quiesce/reset all capture pins/clock and isolate rails,
  * not merely disable a regulator while leaving high IO back-power paths. */
 if(h->powered&&h->p){if(h->p->power_off(h->p->power_ctx))rc=PC_POWER;h->powered=0;}
 h->p=NULL;return rc;
}
static int hw_open(void *ctx,const pen_capture_profile *p,uint16_t *pid,pen_capture_clock *clock) {
 idf_backend *h=ctx;camera_config_t cfg={0};int rc;
 if(!start_armed)return PC_DISABLED;
 if(!p||p!=pen_capture_reviewed_profile(p->name))return PC_PROFILE;
 if(h->initialized||h->powered||h->retired)return PC_STATE;
 if((rc=pen_capture_profile_validate(p)))return rc;
 for(unsigned i=0;i<8;i++)if(!GPIO_IS_VALID_GPIO(p->d[i]))return PC_PROFILE;
 if(!GPIO_IS_VALID_GPIO(p->pclk)||!GPIO_IS_VALID_GPIO(p->href)||!GPIO_IS_VALID_GPIO(p->vsync)||!GPIO_IS_VALID_OUTPUT_GPIO(p->xclk)||!GPIO_IS_VALID_OUTPUT_GPIO(p->sda)||!GPIO_IS_VALID_OUTPUT_GPIO(p->scl))return PC_PROFILE;
 for(size_t i=0;i<p->control_count;i++)if(!GPIO_IS_VALID_OUTPUT_GPIO(p->control_gpios[i]))return PC_PROFILE;
 /* Fail before power if external frame storage/internal DMA block unavailable.
  * These necessary minima are not sufficient; IDF allocations remain checked. */
 if(heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT)<PEN_CAPTURE_BYTES+16u||heap_caps_get_largest_free_block(MALLOC_CAP_DMA|MALLOC_CAP_INTERNAL)<32768u)return PC_MEMORY;
 h->p=p;h->powered=1; /* safe-off needed even if prepare or on partially fails */
 if(p->prepare_safe(p->power_ctx)||p->power_on(p->power_ctx))return PC_POWER;
 cfg.pin_d0=p->d[0];cfg.pin_d1=p->d[1];cfg.pin_d2=p->d[2];cfg.pin_d3=p->d[3];
 cfg.pin_d4=p->d[4];cfg.pin_d5=p->d[5];cfg.pin_d6=p->d[6];cfg.pin_d7=p->d[7];
 cfg.pin_xclk=p->xclk;cfg.pin_pclk=p->pclk;cfg.pin_vsync=p->vsync;cfg.pin_href=p->href;
 cfg.pin_sccb_sda=p->sda;cfg.pin_sccb_scl=p->scl;cfg.pin_reset=-1;cfg.pin_pwdn=-1;
 cfg.xclk_freq_hz=PEN_CAPTURE_XCLK_HZ;cfg.pixel_format=PIXFORMAT_GRAYSCALE;cfg.frame_size=FRAMESIZE_VGA;
 cfg.fb_count=1;cfg.fb_location=CAMERA_FB_IN_PSRAM;cfg.grab_mode=CAMERA_GRAB_WHEN_EMPTY;
 if(esp_camera_get_psram_mode())return PC_MODE;
 h->retired=1; /* Single boot session: upstream cleanup is not a proven warm-reset contract. */
 if(esp_camera_init(&cfg)!=ESP_OK)return PC_DRIVER; /* upstream owns partial-init cleanup */
 h->initialized=1;
 sensor_t *s=esp_camera_sensor_get();
 if(!s||s->id.PID!=PEN_CAPTURE_SENSOR_PID)return PC_SENSOR;
 *pid=s->id.PID;
 int id_hi=s->get_reg(s,0x3107,0xff),id_lo=s->get_reg(s,0x3108,0xff);
 if(id_hi<0||id_lo<0||((id_hi<<8)|id_lo)!=PEN_CAPTURE_SENSOR_PID)return PC_SENSOR;
 int wh=s->get_reg(s,0x3208,0x03),wl=s->get_reg(s,0x3209,0xff);
 int hh=s->get_reg(s,0x320a,0x03),hl=s->get_reg(s,0x320b,0xff);
 if(wh<0||wl<0||hh<0||hl<0||((wh<<8)|wl)!=640||((hh<<8)|hl)!=480)return PC_MODE;
 if(s->pixformat!=PIXFORMAT_GRAYSCALE||s->status.framesize!=FRAMESIZE_VGA)return PC_MODE;
 if(pen_capture_clock_plan(PEN_CAPTURE_XCLK_HZ,clock))return PC_CLOCK;
 /* Read actual configured divider, not just requested xclk in sensor struct. */
 unsigned div=LCD_CAM.cam_ctrl.cam_clkm_div_num;
 if(LCD_CAM.cam_ctrl.cam_clk_sel!=3||LCD_CAM.cam_ctrl.cam_clkm_div_a||LCD_CAM.cam_ctrl.cam_clkm_div_b||div!=16)return PC_CLOCK;
 clock->divider=div;clock->actual_hz=160000000u/div;clock->remainder=160000000u%div;
 ESP_LOGI(TAG,"PID=%04x VGA Gray8 XCLK requested=%lu configured=%lu divider=%u; PCLK scope-record=%lu (not live measured)",*pid,(unsigned long)clock->requested_hz,(unsigned long)clock->actual_hz,div,(unsigned long)p->measured_pclk_hz);
 return PC_OK;
}
static int hw_take(void *ctx,uint32_t ms,pen_capture_raw *out) {
 idf_backend *h=ctx;
 if(!h->initialized)return PC_STATE;
 camera_fb_t *f=esp_camera_fb_get_timeout_ms(ms);
 if(!f)return PC_TIMEOUT;
 out->owner=f;out->data=f->buf;out->bytes=f->len;out->width=f->width;out->height=f->height;out->stride=f->width;
 out->gray8=f->format==PIXFORMAT_GRAYSCALE;out->synthetic=0;
 if(f->timestamp.tv_sec<0||f->timestamp.tv_usec<0||f->timestamp.tv_usec>=1000000)return PC_FRAME;
 /* HAL samples after ll_cam_start/manual VSYNC: freshness only, not exposure/pressure alignment. */
 out->timestamp_us=(uint64_t)f->timestamp.tv_sec*1000000u+(uint64_t)f->timestamp.tv_usec;
 return PC_OK;
}
static void hw_give(void *ctx,void *f){(void)ctx;esp_camera_fb_return(f);}
static uint64_t hw_now(void *ctx){(void)ctx;return (uint64_t)esp_timer_get_time();}
static const pen_capture_backend ops={hw_open,hw_close,hw_take,hw_give,hw_now};
pen_capture *pen_capture_idf_instance(void) {
 if(!ready){pen_capture_construct(&instance,&ops,&hw);ready=1;}
 return &instance;
}
int pen_capture_idf_start(const char *name,int enable) {
#if !CONFIG_PEN_CAMERA_CAPTURE_COMPILE_ENABLE
 (void)name;(void)enable;return PC_DISABLED;
#else
 if(!enable)return PC_DISABLED;
 const pen_capture_profile *p=pen_capture_reviewed_profile(name);
 if(!p)return PC_PROFILE;
 start_armed=1;
 int rc=pen_capture_start_checked(pen_capture_idf_instance(),p,1);
 start_armed=0;return rc;
#endif
}
