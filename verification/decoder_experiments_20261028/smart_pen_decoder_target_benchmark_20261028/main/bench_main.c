/* No board, camera, GPIO, radio, NVS, flash-write or update provider. */
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "roi_opt.h"
#if CONFIG_PEN_DECODER_BENCH_RUN
#include "fixtures.h"
static void memory(const char *stage,const char *placement) {
 printf("{\"type\":\"memory\",\"stage\":\"%s\",\"placement\":\"%s\",\"internal_free_bytes\":%u,\"internal_min_free_bytes\":%u,\"internal_largest_bytes\":%u,\"psram_free_bytes\":%u,\"stack_min_free_bytes\":%u}\n",stage,placement,
 (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
 (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT),
 (unsigned)uxTaskGetStackHighWaterMark(NULL));
}
static void run(const char *placement,uint32_t caps) {
 memory("before_alloc",placement);
 uint8_t *pixels=heap_caps_malloc(200*200,caps);
 pen_roi_workspace *ws=heap_caps_malloc(sizeof(*ws),caps);
 if(!pixels||!ws) {printf("{\"type\":\"skip\",\"placement\":\"%s\",\"reason\":\"allocation_failed\"}\n",placement);heap_caps_free(pixels);heap_caps_free(ws);return;}
 memory("allocated",placement);
 for(size_t f=0;f<sizeof(fixtures)/sizeof(fixtures[0]);f++) {
  const bench_fixture *fixture=&fixtures[f]; size_t n=0;
  for(size_t r=0;r<fixture->nruns;r++) {size_t count=fixture->runs[r].count;
   if(n+count>200*200) {puts("{\"type\":\"fatal\",\"reason\":\"fixture_bounds\"}");goto done;}
   memset(pixels+n,fixture->runs[r].value,count);n+=count;
  }
  if(n!=fixture->w*fixture->h) {puts("{\"type\":\"fatal\",\"reason\":\"fixture_length\"}");goto done;}
  const pen_roi_config config={710,1000,10,2}; /* Bounds and section only, not answer coordinates. */
  for(unsigned repeat=0;repeat<CONFIG_PEN_DECODER_BENCH_REPEATS;repeat++) {
   pen_roi_prior prior={0};
   for(unsigned phase=0;phase<2;phase++) {
    /* Warm is attempted only after successful pixel-derived cold acquisition. */
    if(phase && !prior.valid) {printf("{\"type\":\"warm_skip\",\"fixture\":\"%s\",\"placement\":\"%s\",\"repeat\":%u,\"reason\":\"cold_rejected\"}\n",fixture->name,placement,repeat);break;}
    pen_roi_opt_result result,before;memset(&result,0xa5,sizeof(result));memcpy(&before,&result,sizeof(result));
    int64_t start=esp_timer_get_time();
    int status=pen_roi_decode_opt(pixels,n,fixture->w,fixture->h,fixture->w,&config,ws,&prior,&result);
    int64_t elapsed=esp_timer_get_time()-start;
    const char *verdict=status==0 ? ((fixture->status==0 && result.decoded.x==fixture->x && result.decoded.y==fixture->y)?"correct_coordinate":"unexpected_success") : (fixture->status==status?"expected_nofit":"unexpected_reject");
    printf("{\"type\":\"decode\",\"fixture\":\"%s\",\"placement\":\"%s\",\"repeat\":%u,\"mode\":\"%s\",\"status\":%d,\"verdict\":\"%s\",\"decode_us\":%" PRId64 ",\"failure_output_preserved\":%s,\"failure_prior_cleared\":%s",fixture->name,placement,repeat,phase?"warm":"cold",status,verdict,elapsed,(!status||!memcmp(&before,&result,sizeof(result)))?"true":"false",(!status||!prior.valid)?"true":"false");
    if(!status) printf(",\"x\":%u,\"y\":%u,\"dots\":%u,\"windows\":%u,\"candidates\":%" PRIu32 ",\"used_warm\":%u",result.decoded.x,result.decoded.y,result.decoded.dots,result.decoded.windows,result.candidates,result.used_warm_start);
    puts("}"); memory("after_decode",placement);vTaskDelay(pdMS_TO_TICKS(10));
   }
  }
 }
 done: heap_caps_free(ws);heap_caps_free(pixels);memory("after_free",placement);
}
#endif
void app_main(void) {
 /* Delay lets a manually attached serial logger catch the benchmark header. */
 vTaskDelay(pdMS_TO_TICKS(3000));
#if CONFIG_PEN_DECODER_BENCH_RUN
 puts("{\"type\":\"header\",\"schema\":1,\"decoder\":\"frozen_roi_opt\",\"synthetic_only\":true,\"timing_scope\":\"decode_call_only\",\"cold_means\":\"empty_geometry_prior_not_flushed_cache\",\"warm_means\":\"same_pixels_pixel_derived_prior\",\"hardware_providers\":false}");
 printf("{\"type\":\"runtime_config\",\"workspace_bytes\":%u,\"configured_cpu_mhz\":%u,\"configured_main_stack_bytes\":%u,\"repeats\":%u}\n",(unsigned)sizeof(pen_roi_workspace),(unsigned)CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ,(unsigned)CONFIG_ESP_MAIN_TASK_STACK_SIZE,(unsigned)CONFIG_PEN_DECODER_BENCH_REPEATS);
 run("internal",MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
#if CONFIG_PEN_DECODER_BENCH_PSRAM
 if(heap_caps_get_total_size(MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT)>0) run("psram",MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 else puts("{\"type\":\"skip\",\"placement\":\"psram\",\"reason\":\"not_initialized_or_absent\"}");
#else
 puts("{\"type\":\"skip\",\"placement\":\"psram\",\"reason\":\"not_opted_in\"}");
#endif
 puts("{\"type\":\"complete\"}");
#else
 puts("{\"type\":\"disabled\",\"reason\":\"explicit_opt_in_required\"}");
#endif
}
