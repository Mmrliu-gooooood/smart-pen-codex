#ifndef PEN_RECORDER_H
#define PEN_RECORDER_H
#include "contact_power.h"
#include "store.h"
typedef struct {pen_cp contact;pen_store *store;int faulted;} pen_recorder;
typedef struct {unsigned recorded,actions,contact_faults;int storage_error,input_error;uint64_t raw_down_us;} pen_recorder_result;
int pen_recorder_init(pen_recorder*,pen_store*,const pen_cp_config*);
/* State machine events -> durable records in captured-time order. No GPIO/BLE
   calls. Storage failure latches until boot/reinitialization, strips SLEEP and
   stops recording; never acknowledges or transmits an undurable observation. */
int pen_recorder_step(pen_recorder*,const pen_cp_input*,const pen_sample*,pen_recorder_result*);
#endif
