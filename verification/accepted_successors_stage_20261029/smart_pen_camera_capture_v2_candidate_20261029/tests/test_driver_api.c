#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#define PEN_CAMERA_GRAY_ONLY_BUILD 1
#include "../third_party/esp32-camera/driver/esp_camera.c"
static unsigned checks;static int writes,fail_write,fail_read=-1,hal_init_n,hal_config_n,hal_deinit_n,sccb_deinit_n,starts,takes;static TickType_t last_ticks;
static uint8_t regs[65536];static camera_fb_t fb;
static int reads,fail_read_from,write_at_read[32],sccb_init_error,hal_init_error,hal_config_error;
#define CK(x) do {checks++;assert(x);}while(0)
const char *esp_err_to_name(int e){(void)e;return "mock";}
void vTaskDelay(int t){(void)t;}
int SCCB_Init(int sda,int scl){(void)sda;(void)scl;return sccb_init_error;}
int SCCB_Use_Port(int p){(void)p;return ESP_OK;}
int SCCB_Deinit(void){sccb_deinit_n++;return ESP_OK;}
int SCCB_Probe(uint8_t a){return a==0x30?ESP_OK:ESP_FAIL;}
int SCCB_Read16_Checked(uint8_t a,uint16_t r,uint8_t*out){CK(a==0x30);reads++;CK(reads<32);write_at_read[reads]=writes;*out=0;if(r==fail_read||(fail_read_from&&reads>=fail_read_from))return -1;*out=regs[r];return 0;}
int SCCB_Write16(uint8_t a,uint16_t r,uint8_t v){CK(a==0x30);writes++;if(writes==fail_write)return -1;regs[r]=v;return 0;}
int xclk_timer_conf(int a,int b){(void)a;(void)b;return 0;}
esp_err_t cam_init(const camera_config_t*c){CK(c!=NULL);hal_init_n++;return hal_init_error;}
esp_err_t cam_config(const camera_config_t*c,framesize_t fs,uint16_t pid){(void)c;CK(fs==FRAMESIZE_VGA&&pid==0x31);hal_config_n++;return hal_config_error;}
esp_err_t cam_deinit(void){hal_deinit_n++;return ESP_OK;}
void cam_start(void){starts++;}
camera_fb_t *cam_take(TickType_t t){last_ticks=t;takes++;return &fb;}
void cam_give(camera_fb_t*f){CK(f==&fb);}
static camera_config_t cfg={.pin_sccb_sda=13,.pin_sccb_scl=14,.pin_xclk=9,.pin_pwdn=-1,.pin_reset=-1,.frame_size=FRAMESIZE_VGA,.pixel_format=PIXFORMAT_GRAYSCALE};
static void reset_mock(void){CK(!s_state);writes=fail_write=hal_init_n=hal_config_n=hal_deinit_n=sccb_deinit_n=starts=takes=0;reads=fail_read_from=sccb_init_error=hal_init_error=hal_config_error=0;memset(write_at_read,0,sizeof(write_at_read));fail_read=-1;memset(regs,0,sizeof(regs));regs[0x3108]=0x31;cfg.pixel_format=PIXFORMAT_GRAYSCALE;}
int main(void){
 reset_mock();CK(!esp_camera_fb_get_timeout_ms(1)&&!takes);
 regs[0x3108]=0x35;CK(esp_camera_init(&cfg)==ESP_ERR_NOT_SUPPORTED);CK(!writes&&!s_state&&!hal_config_n&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);
 for(int n=0;n<2;n++){reset_mock();fail_read=n?0x3108:0x3107;CK(esp_camera_init(&cfg)==ESP_ERR_NOT_SUPPORTED);CK(!writes&&!s_state&&!hal_config_n&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);}
 reset_mock();CK(!esp_camera_init(&cfg));int total=writes,total_reads=reads;int baseline[32];memcpy(baseline,write_at_read,sizeof(baseline));CK(total>100&&total_reads==6&&starts==1&&s_state);CK(!esp_camera_deinit()&&!s_state);
 for(int n=1;n<=total;n++){reset_mock();fail_write=n;CK(esp_camera_init(&cfg)!=ESP_OK);CK(writes==n&&!s_state&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);}
 for(int n=1;n<=total_reads;n++){reset_mock();fail_read_from=n;CK(esp_camera_init(&cfg)!=ESP_OK);CK(writes==baseline[n]&&!s_state&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);}
 reset_mock();sccb_init_error=-9;CK(esp_camera_init(&cfg)==-9);CK(!s_state&&!writes&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);
 reset_mock();hal_init_error=-8;CK(esp_camera_init(&cfg)==-8);CK(!s_state&&!writes&&!starts&&!hal_deinit_n&&!sccb_deinit_n);
 reset_mock();hal_config_error=-7;CK(esp_camera_init(&cfg)==-7);CK(!s_state&&writes==1&&!starts&&hal_deinit_n==1&&sccb_deinit_n==1);
 reset_mock();cfg.pixel_format=PIXFORMAT_RGB565;CK(esp_camera_init(&cfg)==ESP_ERR_CAMERA_FAILED_TO_SET_OUT_FORMAT);CK(!s_state&&!starts&&hal_deinit_n==1);
 reset_mock();CK(!esp_camera_init(&cfg));CK(!esp_camera_fb_get_timeout_ms(0)&&!esp_camera_fb_get_timeout_ms(4001)&&!esp_camera_fb_get_timeout_ms(UINT32_MAX)&&!takes);
 CK(esp_camera_fb_get_timeout_ms(1)==&fb&&last_ticks==1);CK(fb.width==640&&fb.height==480&&fb.format==PIXFORMAT_GRAYSCALE);
 CK(esp_camera_fb_get_timeout_ms(200)==&fb&&last_ticks==200);CK(esp_camera_fb_get()==&fb&&last_ticks==4000);CK(!esp_camera_deinit()&&!s_state);
 printf("PASS actual esp_camera + SC031GS sources: %u checks; wrong-ID/ID-read failure zero init writes, all%d init write failures + all6 read failures clean/no later writes, init/config/pixformat failures, bounded timeout API (HAL mocked)\n",checks,total);
}
