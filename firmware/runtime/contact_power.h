#ifndef PEN_CONTACT_POWER_H
#define PEN_CONTACT_POWER_H
#include "pen.h"
#define PEN_CP_BUFFER 8u
#define PEN_CP_MAX_EVENTS (PEN_CP_BUFFER + 2u)
enum pen_cp_phase { PEN_CP_ASLEEP, PEN_CP_WAKING, PEN_CP_READY, PEN_CP_FAULT };
enum pen_cp_action { PEN_CP_WAKE_CAMERA=1, PEN_CP_CLEAR_PICKUP=2, PEN_CP_SLEEP_REQUEST=4 };
enum pen_cp_fault { PEN_CP_CLOCK=1, PEN_CP_CAMERA_TIMEOUT=2, PEN_CP_CONTACT_STUCK=4, PEN_CP_IRQ_STUCK=8 };
typedef struct {
 uint32_t press_us, camera_timeout_us, contact_stuck_us, irq_stuck_us, idle_us;
 uint16_t min_confidence;
} pen_cp_config;
typedef struct {
 uint64_t now_us;
 uint8_t raw_contact, pickup_irq_low, camera_ready, storage_pending;
 uint8_t usb_sleep_allowed, calibrated, has_observation, recover_fault;
} pen_cp_input;
typedef struct {
 pen_sample events[PEN_CP_MAX_EVENTS];
 unsigned count, actions, faults;
 uint64_t raw_down_us;
 uint8_t contact_confirmed;
} pen_cp_output;
typedef struct {
 pen_cp_config config;
 enum pen_cp_phase phase;
 uint64_t last_us, wake_us, activity_us, down_us, irq_us;
 pen_sample buffered[PEN_CP_BUFFER];
 unsigned buffered_count, faults;
 uint8_t started, raw, irq, confirmed, lost;
} pen_cp;
/* Pure state machine: no GPIO, camera power, sleeping, or storage writes.
   Initialize each boot. Timings are application configuration, not measured defaults. */
int pen_cp_init(pen_cp *state, const pen_cp_config *config);
/* template timestamp must equal now_us; valid observations must already be
   calibrated. Outputs retain captured timestamps. Caller assigns durable seq
   after ordering these events; template seq is not a sequence allocator. */
int pen_cp_step(pen_cp *state, const pen_cp_input *input,
                const pen_sample *observation_or_template, pen_cp_output *output);
#endif
