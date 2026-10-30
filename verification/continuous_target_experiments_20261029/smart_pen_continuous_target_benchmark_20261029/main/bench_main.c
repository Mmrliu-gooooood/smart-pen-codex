/* Synthetic CPU-only benchmark. Never invokes camera/GPIO/radio/storage providers. */
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_idf_version.h"
#include "roi_continuous.h"
#if CONFIG_NEWLIB_NANO_FORMAT
#error "Benchmark requires full 64-bit integer and floating-point printf formatting"
#endif
int pen_roi_decode_opt_frozen(const uint8_t *,size_t,unsigned,unsigned,unsigned,const pen_roi_config *,pen_roi_workspace *,pen_roi_prior *,pen_roi_opt_result *);
#if CONFIG_PEN_DECODER_BENCH_RUN
#include "fixtures.h"
static void memory(const char *stage) {
 printf("{\"type\":\"memory\",\"stage\":\"%s\",\"placement\":\"internal\",\"internal_free_bytes\":%u,\"internal_min_free_bytes\":%u,\"internal_largest_bytes\":%u,\"stack_min_free_bytes\":%u}\n",stage,
 (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)uxTaskGetStackHighWaterMark(NULL));
}
static void matrix(const char *key,const double *m) {
 printf(",\"%s\":[%.17g,%.17g,%.17g,%.17g,%.17g,%.17g]",key,m[0],m[1],m[2],m[3],m[4],m[5]);
}
static void decoded(const pen_roi_opt_result *r) {
 printf(",\"x\":%u,\"y\":%u,\"dots\":%u,\"windows\":%u,\"candidates\":%" PRIu32 ",\"used_warm\":%u,\"directions\":[",r->decoded.x,r->decoded.y,r->decoded.dots,r->decoded.windows,r->candidates,r->used_warm_start);
 for(unsigned i=0;i<36;i++) printf("%s%u",i?",":"",r->decoded.directions[i]);
 putchar(']');
}
static void run(void) {
 memory("before_alloc");
 uint8_t *pixels=heap_caps_malloc(200*200,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
 pen_continuous_workspace *ws=heap_caps_malloc(sizeof(*ws),MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
 if(!pixels||!ws) {puts("{\"type\":\"fatal\",\"reason\":\"allocation_failed\"}");goto done;}
 memory("allocated");
 const pen_roi_config config={710,1000,10,2};
 for(size_t f=0;f<sizeof(fixtures)/sizeof(fixtures[0]);f++) {
  const bench_fixture *fixture=&fixtures[f];size_t n=0;
  if(fixture->packed_size%3) {puts("{\"type\":\"fatal\",\"reason\":\"fixture_encoding\"}");goto done;}
  for(size_t i=0;i<fixture->packed_size;i+=3) {
   size_t count=(size_t)fixture->packed[i]|((size_t)fixture->packed[i+1]<<8);
   if(!count||n+count>40000) {puts("{\"type\":\"fatal\",\"reason\":\"fixture_bounds\"}");goto done;}
   memset(pixels+n,fixture->packed[i+2],count);n+=count;
  }
  if(n!=40000) {puts("{\"type\":\"fatal\",\"reason\":\"fixture_length\"}");goto done;}
  for(unsigned repeat=0;repeat<CONFIG_PEN_DECODER_BENCH_REPEATS;repeat++) {
   for(unsigned decoder=0;decoder<2;decoder++) {
    /* No oracle/geometry prior enters either decode call. */
    pen_continuous_result result,before;memset(&result,0xa5,sizeof(result));memcpy(&before,&result,sizeof(result));
    int64_t start=esp_timer_get_time();int status;
    if(decoder) status=pen_roi_decode_continuous(pixels,n,200,200,200,&config,ws,&result);
    else status=pen_roi_decode_opt_frozen(pixels,n,200,200,200,&config,&ws->core,NULL,&result.roi);
    int64_t elapsed=esp_timer_get_time()-start;
    printf("{\"type\":\"decode\",\"fixture\":\"%s\",\"placement\":\"internal\",\"repeat\":%u,\"decoder\":\"%s\",\"mode\":\"cold\",\"status\":%d,\"decode_us\":%" PRId64 ",\"failure_output_preserved\":%s",fixture->name,repeat,decoder?"continuous_v2":"frozen_opt",status,elapsed,(!status||!memcmp(&before,&result,sizeof(result)))?"true":"false");
    if(!status) {
     decoded(&result.roi);
     if(decoder) {
      printf(",\"crop\":[%u,%u,%u,%u],\"crop_attempts\":%u,\"edge_components\":%u,\"edge_pixels\":%u",result.left,result.top,result.width,result.height,result.crop_attempts,result.edge_components,result.edge_pixels);
      matrix("paper_to_frame",result.paper_to_frame);matrix("frame_to_paper",result.frame_to_paper);
     }
    }
    puts("}");memory("after_decode");vTaskDelay(pdMS_TO_TICKS(10));
   }
  }
 }
 done: heap_caps_free(ws);heap_caps_free(pixels);memory("after_free");
}
#endif
void app_main(void) {
 vTaskDelay(pdMS_TO_TICKS(3000));
#if CONFIG_PEN_DECODER_BENCH_RUN
 printf("{\"type\":\"header\",\"schema\":2,\"synthetic_only\":true,\"manifest_sha256\":\"%s\",\"source_bundle_sha256\":\"%s\",\"timing_scope\":\"full_decode_call_including_wrapper_preprocessing\",\"cold_means\":\"no_prior_not_flushed_cpu_cache\",\"hardware_providers\":false}\n",BENCH_MANIFEST_SHA256,BENCH_SOURCE_SHA256);
 printf("{\"type\":\"runtime_config\",\"workspace_bytes\":%u,\"pixel_bytes\":40000,\"configured_cpu_mhz\":%u,\"configured_main_stack_bytes\":%u,\"repeats\":%u,\"idf_version\":\"%s\",\"configured_target\":\"esp32s3\",\"nano_format\":false}\n",(unsigned)sizeof(pen_continuous_workspace),(unsigned)CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ,(unsigned)CONFIG_ESP_MAIN_TASK_STACK_SIZE,(unsigned)CONFIG_PEN_DECODER_BENCH_REPEATS,IDF_VER);
 /* Fail before allocating/running samples if target libc cannot format both types. */
 char format_check[48];
 int format_length=snprintf(format_check,sizeof(format_check),"%" PRId64 "|%.2f",INT64_C(4294967297),1.25);
 if(format_length!=15 || strcmp(format_check,"4294967297|1.25")!=0) {
  puts("{\"type\":\"fatal\",\"reason\":\"libc_format_selftest\"}");return;
 }
 /* Explicit libc-format probe, not a measurement; parser requires exact values. */
 printf("{\"type\":\"format_probe\",\"int64\":%" PRId64 ",\"double\":%.17g}\n",INT64_C(4294967297),1.23456789012345);
 run();puts("{\"type\":\"skip\",\"placement\":\"psram\",\"reason\":\"pure_ram_profile\"}");puts("{\"type\":\"complete\"}");
#else
 puts("{\"type\":\"disabled\",\"reason\":\"explicit_opt_in_required\"}");
#endif
}
