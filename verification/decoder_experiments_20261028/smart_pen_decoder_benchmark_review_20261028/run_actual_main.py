"""Host mock of actual benchmark app_main. ALL clocks/heap/device values are fake.
Never use its output as device identity, speed, or RAM availability evidence."""
from pathlib import Path
import os,subprocess,json,sys
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_decoder_target_benchmark_20261028'))).resolve()
sys.path.insert(0,str(SRC/'tools'))
from summarize_serial import summarize
OUT=HERE/'run_output';OUT.mkdir(exist_ok=True)
stub=OUT/'stubs';(stub/'freertos').mkdir(parents=True,exist_ok=True)
(stub/'freertos/FreeRTOS.h').write_text('#define pdMS_TO_TICKS(x) (x)\n')
(stub/'freertos/task.h').write_text('#include <stddef.h>\nvoid vTaskDelay(unsigned);\nunsigned uxTaskGetStackHighWaterMark(void*);\n')
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
#ifdef DISABLED
if(allocs||frees||ticks)return 1;
#elif defined(FAIL_ALLOC)
if(allocs!=2||frees||ticks)return 1;
#else
if(allocs!=2||frees!=2||ticks!=60*123)return 1;
#endif
return 0;}
''')
results=[]
for name,enabled,flags in [('enabled',1,[]),('disabled',0,['-DDISABLED=1']),('allocation_failure',1,['-DFAIL_ALLOC=1']),('sanitized',1,['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 (stub/'sdkconfig.h').write_text(f'#define CONFIG_PEN_DECODER_BENCH_RUN {enabled}\n#define CONFIG_PEN_DECODER_BENCH_PSRAM 0\n#define CONFIG_PEN_DECODER_BENCH_REPEATS 3\n#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240\n#define CONFIG_ESP_MAIN_TASK_STACK_SIZE 16384\n')
 exe=OUT/name
 cmd=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-I'+str(stub),'-I'+str(SRC/'vision'),'-I'+str(SRC/'codec')]+flags+[str(SRC/p) for p in ('main/bench_main.c','vision/roi_opt.c','codec/anoto.c')]+[str(OUT/'bridge.c'),'-lm','-o',str(exe)]
 if name=='allocation_failure':cmd.insert(1,'-Wno-unused-parameter')
 subprocess.run(cmd,check=True)
 p=subprocess.run([str(exe)],text=True,capture_output=True,check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:abort_on_error=1'))
 rows=[json.loads(x) for x in p.stdout.splitlines()]
 if enabled and name!='allocation_failure':
  dec=[x for x in rows if x['type']=='decode'];assert len(dec)==30
  assert sum(x['verdict']=='correct_coordinate' for x in dec)==18
  assert sum(x['verdict']=='expected_nofit' for x in dec)==12
  assert all(x['decode_us']==123 for x in dec)
  assert len([x for x in rows if x['type']=='warm_skip'])==12
  parsed=summarize(p.stdout.splitlines());assert not parsed['functional_failures'] and parsed['identity_verified'] is False and parsed['overall_pass'] is None
 elif not enabled:assert rows==[{'type':'disabled','reason':'explicit_opt_in_required'}]
 else:assert not any(x['type']=='decode' for x in rows)
 # Store only machine summary, not mock JSON that could masquerade as measurements.
 results.append({'case':name,'passed':True,'artificial_clock':True,'device_measured':False})
print(json.dumps(results,indent=2))
