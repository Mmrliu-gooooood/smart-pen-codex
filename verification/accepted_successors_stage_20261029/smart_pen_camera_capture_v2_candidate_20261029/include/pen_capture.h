#ifndef PEN_CAPTURE_H
#define PEN_CAPTURE_H
#include <stddef.h>
#include <stdint.h>
#define PEN_CAPTURE_WIDTH 640u
#define PEN_CAPTURE_HEIGHT 480u
#define PEN_CAPTURE_BYTES (640u*480u)
#define PEN_CAPTURE_XCLK_HZ 10000000u
#define PEN_CAPTURE_SENSOR_PID 0x0031u
#define PEN_CAPTURE_PCLK_CAP_HZ 40000000u
#define PEN_CAPTURE_GET_MAX_MS 200u
enum pen_capture_error { PC_OK=0,PC_TIMEOUT=1,PC_DISABLED=-1,PC_PROFILE=-2,
 PC_MODE=-3,PC_CLOCK=-4,PC_STATE=-5,PC_DRIVER=-6,PC_FRAME=-7,PC_STALE=-8,
 PC_MEMORY=-9,PC_SENSOR=-10,PC_POWER=-11,PC_OWNERSHIP=-12,PC_TIMEOUT_FATAL=-13 };
enum pen_capture_state { PC_STOPPED,PC_RUNNING,PC_HELD,PC_FAULT };
typedef struct { uint32_t requested_hz,source_hz,divider,actual_hz,remainder; } pen_capture_clock;
typedef struct {
 const char *name,*review_reference; uint32_t source_id;
 uint16_t expected_pid; uint32_t requested_xclk_hz,measured_pclk_hz;
 uint8_t electrical_reviewed,scope_reviewed,psram_reviewed,power_sequence_reviewed;
 int d[8],xclk,pclk,vsync,href,sda,scl;
 /* Concrete reviewed power/reset/isolation sequence belongs to this exact board.
  * Must be idempotent and handle partial initialization. Camera library never
  * drives generic PWDN/RESET; those are -1 and exclusively owned by these hooks.
  * No hooks/profiles are supplied. Unknown board => reject before either hook. */
 const int *control_gpios; size_t control_count;
 int (*prepare_safe)(void*); int (*power_on)(void*); int (*power_off)(void*);
 void *power_ctx;
} pen_capture_profile;
typedef struct {
 const uint8_t *data; size_t bytes,width,height,stride;
 /* HAL software boot-time sample; not first-DMA/exposure time. */
 uint64_t timestamp_us; void *owner; uint8_t gray8,synthetic;
} pen_capture_raw;
typedef struct {
 int (*open)(void*,const pen_capture_profile*,uint16_t*,pen_capture_clock*);
 int (*close)(void*); int (*take)(void*,uint32_t,pen_capture_raw*);
 void (*give)(void*,void*); uint64_t (*now_us)(void*);
} pen_capture_backend;
typedef struct {
 const uint8_t *gray; size_t length; unsigned width,height,stride;
 uint64_t timestamp_us,frame_id; uint32_t source_id; uint8_t synthetic;
} pen_capture_view;
typedef struct {
 const pen_capture_backend *ops; void *backend_ctx; const pen_capture_profile *profile;
 pen_capture_raw held; pen_capture_clock clock; enum pen_capture_state state;
 uint64_t last_timestamp_us,next_frame_id; uint32_t source_id,timeouts;
 int last_error; uint8_t opened,cleanup_failed;
} pen_capture;
/* One owner task only, not ISR/thread-safe. Do not reconstruct while a frame is held.
 * All output views are borrowed, invalid immediately on release/stop/fault.
 * A timeout has no frame and must become a no-image/gap event, never old VALID. */
int pen_capture_clock_plan(uint32_t,pen_capture_clock*);
int pen_capture_profile_validate(const pen_capture_profile*);
void pen_capture_construct(pen_capture*,const pen_capture_backend*,void*);
/* Internal portable seam: production uses pen_capture_idf_start allowlist only.
 * runtime_enabled is an extra gate, not board approval; tests use synthetic backend. */
int pen_capture_start_checked(pen_capture*,const pen_capture_profile*,int runtime_enabled);
int pen_capture_get(pen_capture*,uint32_t timeout_ms,pen_capture_view*);
int pen_capture_release(pen_capture*,uint64_t frame_id);
int pen_capture_stop(pen_capture*);
#endif
