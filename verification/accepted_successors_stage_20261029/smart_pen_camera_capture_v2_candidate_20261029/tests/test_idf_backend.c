#include <assert.h>
#include <stdio.h>
#include <string.h>
#define PEN_CAMERA_GRAY_ONLY_BUILD 1
#include "../src/pen_capture_idf.c"
static unsigned checks;
#define CK(x) do { checks++;assert(x); }while(0)
static int prepare_n,on_n,off_n,init_n,deinit_n,give_n,off_rc,prepare_rc,on_rc,init_rc,deinit_rc,read_bad,mode_dma;
static size_t ext_block,int_block;
static sensor_t sens;static uint8_t pixels[307200];static camera_fb_t fb;static int fb_null;
static int prep(void*x){(void)x;prepare_n++;return prepare_rc;}
static int on(void*x){(void)x;on_n++;return on_rc;}
static int off(void*x){(void)x;off_n++;return off_rc;}
static int ctl[]={26};
static pen_capture_profile p={"MOCK_REVIEW_ONLY","no-hardware-test",99,0x31,10000000,40000000,1,1,1,1,{1,2,3,4,5,6,7,8},9,10,11,12,13,14,ctl,1,prep,on,off,NULL};
const pen_capture_profile *pen_capture_reviewed_profile(const char*n){return n&&!strcmp(n,p.name)?&p:NULL;}
fake_lcd_t LCD_CAM;
static int reg(sensor_t*s,int r,int m){(void)s;(void)m;if(r==read_bad)return -1;switch(r){case 0x3107:return 0;case 0x3108:return 0x31;case 0x3208:return 2;case 0x3209:return 128;case 0x320a:return 1;case 0x320b:return 224;}return -1;}
size_t heap_caps_get_largest_free_block(uint32_t caps){return (caps&MALLOC_CAP_SPIRAM)?ext_block:int_block;}
bool esp_camera_get_psram_mode(void){return mode_dma;}
esp_err_t esp_camera_init(const camera_config_t*c){init_n++;CK(c->fb_count==1&&c->fb_location==CAMERA_FB_IN_PSRAM&&c->pin_reset==-1&&c->pin_pwdn==-1&&c->pixel_format==PIXFORMAT_GRAYSCALE&&c->frame_size==FRAMESIZE_VGA&&c->xclk_freq_hz==10000000);return init_rc;}
esp_err_t esp_camera_deinit(void){deinit_n++;return deinit_rc;}
sensor_t *esp_camera_sensor_get(void){return &sens;}
camera_fb_t *esp_camera_fb_get_timeout_ms(uint32_t ms){CK(ms&&ms<=200);return fb_null?NULL:&fb;}
void esp_camera_fb_return(camera_fb_t*f){CK(f==&fb);give_n++;}
int64_t esp_timer_get_time(void){return 1000000;}
static void reset_mock(void){memset(&hw,0,sizeof(hw));memset(&instance,0,sizeof(instance));ready=start_armed=0;prepare_n=on_n=off_n=init_n=deinit_n=give_n=0;off_rc=prepare_rc=on_rc=init_rc=deinit_rc=mode_dma=0;read_bad=-1;ext_block=307216;int_block=32768;memset(&sens,0,sizeof(sens));sens.id.PID=0x31;sens.get_reg=reg;sens.pixformat=PIXFORMAT_GRAYSCALE;sens.status.framesize=FRAMESIZE_VGA;LCD_CAM=(fake_lcd_t){{16,3,0,0}};fb=(camera_fb_t){pixels,307200,640,480,PIXFORMAT_GRAYSCALE,{0,900000}};fb_null=0;}
int main(void){pen_capture_view v;
 reset_mock();CK(pen_capture_idf_start(p.name,0)==PC_DISABLED);CK(pen_capture_idf_start("SC035HGS",1)==PC_PROFILE);CK(!init_n&&!prepare_n);
 CK(pen_capture_start_checked(pen_capture_idf_instance(),&p,1)==PC_DISABLED);CK(!init_n&&!prepare_n);CK(!pen_capture_stop(&instance));
 reset_mock();ext_block--;CK(pen_capture_idf_start(p.name,1)==PC_MEMORY);CK(!prepare_n&&!init_n&&!off_n);
 reset_mock();int_block--;CK(pen_capture_idf_start(p.name,1)==PC_MEMORY);CK(!prepare_n&&!init_n&&!off_n);
 reset_mock();prepare_rc=-1;CK(pen_capture_idf_start(p.name,1)==PC_POWER);CK(prepare_n==1&&!on_n&&off_n==1&&!init_n);
 reset_mock();on_rc=-1;CK(pen_capture_idf_start(p.name,1)==PC_POWER);CK(prepare_n==1&&on_n==1&&off_n==1&&!init_n);
 reset_mock();mode_dma=1;CK(pen_capture_idf_start(p.name,1)==PC_MODE);CK(off_n==1&&!init_n);
 reset_mock();init_rc=-1;CK(pen_capture_idf_start(p.name,1)==PC_DRIVER);CK(hw.retired&&init_n==1&&off_n==1&&!deinit_n);CK(!pen_capture_stop(&instance));CK(pen_capture_idf_start(p.name,1)==PC_STATE);CK(init_n==1&&on_n==1);
 for(int i=0;i<6;i++){int regs[]={0x3107,0x3108,0x3208,0x3209,0x320a,0x320b};reset_mock();read_bad=regs[i];CK(pen_capture_idf_start(p.name,1)<0);CK(deinit_n==1&&off_n==1&&hw.retired);}
 reset_mock();LCD_CAM.cam_ctrl.cam_clkm_div_num=6;CK(pen_capture_idf_start(p.name,1)==PC_CLOCK);CK(deinit_n==1&&off_n==1);
 reset_mock();CK(!pen_capture_idf_start(p.name,1));CK(!pen_capture_get(&instance,1,&v));CK(!v.synthetic&&v.length==307200&&v.stride==640);CK(!pen_capture_stop(&instance));CK(give_n==1&&deinit_n==1&&off_n==1);CK(pen_capture_idf_start(p.name,1)==PC_STATE);CK(init_n==1&&on_n==1);
 reset_mock();CK(!pen_capture_idf_start(p.name,1));fb.timestamp.tv_usec=1000000;CK(pen_capture_get(&instance,1,&v)==PC_FRAME);CK(!v.gray&&give_n==1&&deinit_n==1&&off_n==1);
 reset_mock();CK(!pen_capture_idf_start(p.name,1));fb_null=1;CK(pen_capture_get(&instance,1,&v)==PC_TIMEOUT);CK(pen_capture_get(&instance,1,&v)==PC_TIMEOUT);CK(pen_capture_get(&instance,1,&v)==PC_TIMEOUT_FATAL);CK(deinit_n==1&&off_n==1&&hw.retired);
 reset_mock();CK(!pen_capture_idf_start(p.name,1));off_rc=-1;CK(pen_capture_stop(&instance)==PC_DRIVER);CK(instance.cleanup_failed);CK(pen_capture_stop(&instance)==PC_DRIVER);CK(off_n==1&&deinit_n==1);
 printf("PASS actual IDF-backend source (mock hardware ONLY): %u checks; power failures, memory, ID/window reads, stop/held, bad timeval, timeout, single-boot retirement\n",checks);
}
