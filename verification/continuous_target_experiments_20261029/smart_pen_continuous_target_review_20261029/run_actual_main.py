"""Host mock of actual benchmark app_main. ALL clocks/heap/device values are fake.
Never use its output as device identity, speed, or RAM availability evidence."""
from pathlib import Path
import os,subprocess,json,sys
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_continuous_target_benchmark_20261029'))).resolve()
sys.path.insert(0,str(SRC/'tools'))
from summarize_serial import summarize
OUT=HERE/'run_output';OUT.mkdir(exist_ok=True)
stub=OUT/'stubs';(stub/'freertos').mkdir(parents=True,exist_ok=True)
(stub/'freertos/FreeRTOS.h').write_text('#define pdMS_TO_TICKS(x) (x)\n')
(stub/'freertos/task.h').write_text('#include <stddef.h>\nvoid vTaskDelay(unsigned);\nunsigned uxTaskGetStackHighWaterMark(void*);\n')
(stub/'esp_idf_version.h').write_text('#define IDF_VER "v5.4"\n')
(stub/'esp_timer.h').write_text('#include <stdint.h>\nint64_t esp_timer_get_time(void);\n')
(stub/'esp_heap_caps.h').write_text('''#include <stddef.h>
#include <stdint.h>
#define MALLOC_CAP_INTERNAL 1
#define MALLOC_CAP_8BIT 2
#define MALLOC_CAP_SPIRAM 4
void *heap_caps_malloc(size_t,uint32_t);void heap_caps_free(void*);
size_t heap_caps_get_free_size(uint32_t);size_t heap_caps_get_minimum_free_size(uint32_t);
size_t heap_caps_get_largest_free_block(uint32_t);size_t heap_caps_get_total_size(uint32_t);
''')
(OUT/'bridge.c').write_text('''#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
static int allocs,frees;static int64_t ticks;
void app_main(void);
#ifdef FAIL_FORMAT
int review_snprintf(char*s,size_t n,const char*f,...){(void)f;if(n)s[0]=0;return 0;}
#endif
void vTaskDelay(unsigned n){(void)n;}
unsigned uxTaskGetStackHighWaterMark(void*p){(void)p;return 1024;}
int64_t esp_timer_get_time(void){ticks+=123;return ticks;}
size_t heap_caps_get_free_size(uint32_t c){(void)c;return 100000;}
size_t heap_caps_get_minimum_free_size(uint32_t c){(void)c;return 90000;}
size_t heap_caps_get_largest_free_block(uint32_t c){(void)c;return 80000;}
size_t heap_caps_get_total_size(uint32_t c){(void)c;return 0;}
void*heap_caps_malloc(size_t n,uint32_t c){(void)c;allocs++;
#ifdef FAIL_ALLOC
return NULL;
#else
return malloc(n);
#endif
}
void heap_caps_free(void*p){if(p)frees++;free(p);}
int main(void){app_main();
#if defined(DISABLED)||defined(FAIL_FORMAT)
if(allocs||frees||ticks)return 1;
#elif defined(FAIL_ALLOC)
if(allocs!=2||frees||ticks)return 1;
#else
if(allocs!=2||frees!=2||ticks!=72*123)return 1;
#endif
return 0;}
''')
results=[]
for name,enabled,flags in [('enabled',1,[]),('disabled',0,['-DDISABLED=1']),('allocation_failure',1,['-DFAIL_ALLOC=1']),('format_failure',1,['-DFAIL_FORMAT=1','-Dsnprintf=review_snprintf']),('sanitized',1,['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 (stub/'sdkconfig.h').write_text(f'#define CONFIG_NEWLIB_NANO_FORMAT 0\n#define CONFIG_PEN_DECODER_BENCH_RUN {enabled}\n#define CONFIG_PEN_DECODER_BENCH_PSRAM 0\n#define CONFIG_PEN_DECODER_BENCH_REPEATS 3\n#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240\n#define CONFIG_ESP_MAIN_TASK_STACK_SIZE 16384\n')
 exe=OUT/name
 legacy=OUT/(name+'_legacy.o')
 subprocess.run(['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-Dpen_roi_decode_opt=pen_roi_decode_opt_frozen','-c',str(SRC/'legacy/vision/roi_opt.c'),'-o',str(legacy)]+flags,check=True)
 cmd=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-I'+str(stub),'-I'+str(SRC/'vision'),'-I'+str(SRC/'codec')]+flags+[str(SRC/p) for p in ('main/bench_main.c','vision/roi_continuous.c','vision/roi_opt.c','codec/anoto.c')]+[str(OUT/'bridge.c'),str(legacy),'-lm','-o',str(exe)]
 if name=='allocation_failure':cmd.insert(1,'-Wno-unused-parameter')
 subprocess.run(cmd,check=True)
 p=subprocess.run([str(exe)],text=True,capture_output=True,check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:abort_on_error=1'))
 rows=[json.loads(x) for x in p.stdout.splitlines()]
 if enabled and name not in ('allocation_failure','format_failure'):
  dec=[x for x in rows if x['type']=='decode'];assert len(dec)==36
  assert sum(x['status']==0 for x in dec)==9
  assert sum(x['status']!=0 for x in dec)==27
  assert all(x['decode_us']==123 for x in dec)
  assert not any(x.get('mode')=='warm' for x in rows)
  parsed=summarize(p.stdout.splitlines());assert not parsed['functional_failures'] and parsed['identity_verified'] is False and parsed['overall_pass'] is None
 elif not enabled:assert rows==[{'type':'disabled','reason':'explicit_opt_in_required'}]
 else:
  assert not any(x['type']=='decode' for x in rows)
  if name=='format_failure':assert rows[-1]=={'type':'fatal','reason':'libc_format_selftest'}
 # Store only machine summary, not mock JSON that could masquerade as measurements.
 results.append({'case':name,'passed':True,'artificial_clock':True,'device_measured':False})
# Negative build gate: a stale enabled nano setting must not compile this app.
config=(stub/'sdkconfig.h').read_text();(stub/'sdkconfig.h').write_text(config.replace('CONFIG_NEWLIB_NANO_FORMAT 0','CONFIG_NEWLIB_NANO_FORMAT 1'))
r=subprocess.run(['cc','-std=c11','-I'+str(stub),'-I'+str(SRC/'vision'),'-c',str(SRC/'main/bench_main.c'),'-o',str(OUT/'invalid_nano.o')],capture_output=True,text=True)
assert r.returncode!=0 and 'Benchmark requires full 64-bit' in r.stderr
(stub/'sdkconfig.h').write_text(config)
results.append({'case':'nano_enabled_compile_rejected','passed':True,'device_measured':False})
print(json.dumps(results,indent=2))
