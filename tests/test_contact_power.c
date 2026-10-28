#include "contact_power.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static pen_cp_config config={.press_us=5000,.camera_timeout_us=20000,.contact_stuck_us=100000,.irq_stuck_us=30000,.idle_us=10000,.min_confidence=750};
static pen_sample sample={.device=42,.session=7,.seq=0,.page=1,.x_um=123,.y_um=456,.confidence=900,.flags=PEN_VALID};
static pen_cp_input input;
static pen_cp state;
static pen_cp_output output;
static void reset(void){assert(!pen_cp_init(&state,&config));memset(&input,0,sizeof(input));input.usb_sleep_allowed=1;input.calibrated=1;input.has_observation=1;}
static void step(uint64_t time){input.now_us=time;sample.timestamp_us=time;assert(!pen_cp_step(&state,&input,&sample,&output));assert(output.count<=PEN_CP_MAX_EVENTS);}
static void debounce_and_release(void){
 reset();input.raw_contact=1;input.camera_ready=1;step(100);assert(output.count==0);assert(output.actions&PEN_CP_WAKE_CAMERA);assert(output.raw_down_us==100);
 step(2000);assert(output.count==0);step(5100);assert(output.count==3);assert(output.contact_confirmed);assert(output.events[0].timestamp_us==100);assert(output.events[1].timestamp_us==2000);assert(output.events[0].flags==(PEN_CONTACT|PEN_VALID|PEN_GAP));
 step(6000);assert(output.count==1&&output.events[0].flags==(PEN_CONTACT|PEN_VALID));input.raw_contact=0;step(6001);assert(output.count==1&&output.events[0].flags==0);assert(!output.contact_confirmed&&output.events[0].page==0);
}
static void short_tap_and_overflow(void){
 reset();input.raw_contact=1;input.camera_ready=1;step(0);input.raw_contact=0;step(1);assert(output.count==1&&output.events[0].flags==PEN_GAP);
 reset();input.raw_contact=1;input.camera_ready=1;for(unsigned n=0;n<9;n++)step(n*100);assert(output.count==1);assert(output.events[0].flags==(PEN_CONTACT|PEN_GAP));step(5000);assert(output.count==2);assert(output.events[0].timestamp_us==800);assert(output.events[0].flags&PEN_GAP);
}
static void camera_and_calibration(void){
 reset();input.raw_contact=1;step(0);step(5000);assert(output.count==2);for(unsigned n=0;n<output.count;n++)assert(!(output.events[n].flags&PEN_VALID));input.camera_ready=1;step(6000);assert(output.events[0].flags&PEN_GAP);input.calibrated=0;step(7000);assert(!(output.events[0].flags&PEN_VALID));input.calibrated=1;step(8000);assert(output.events[0].flags&PEN_GAP);
 input.has_observation=0;input.camera_ready=0;step(9000);assert(output.count==1&&!(output.events[0].flags&PEN_VALID));step(29000);assert(output.faults&PEN_CP_CAMERA_TIMEOUT);assert(state.phase==PEN_CP_FAULT);
 input.recover_fault=1;step(30000);assert(state.phase==PEN_CP_FAULT);input.raw_contact=0;input.storage_pending=1;step(31000);assert(state.phase==PEN_CP_FAULT);input.storage_pending=0;step(32000);assert(state.phase==PEN_CP_ASLEEP);
}
static void pickup_sleep_guards(void){
 reset();input.pickup_irq_low=1;step(0);assert(output.actions==(PEN_CP_WAKE_CAMERA|PEN_CP_CLEAR_PICKUP));input.camera_ready=1;step(100);assert(!(output.actions&PEN_CP_CLEAR_PICKUP));input.pickup_irq_low=0;input.storage_pending=1;step(15000);assert(!(output.actions&PEN_CP_SLEEP_REQUEST));input.storage_pending=0;input.usb_sleep_allowed=0;step(16000);assert(!(output.actions&PEN_CP_SLEEP_REQUEST));input.usb_sleep_allowed=1;step(17000);assert(output.actions&PEN_CP_SLEEP_REQUEST);
 reset();input.pickup_irq_low=1;input.camera_ready=1;step(0);step(30000);assert(output.faults&PEN_CP_IRQ_STUCK);input.recover_fault=1;step(31000);assert(state.phase==PEN_CP_FAULT);input.pickup_irq_low=0;step(32000);assert(state.phase==PEN_CP_ASLEEP);
}
static void stuck_and_clock(void){
 reset();input.raw_contact=1;input.camera_ready=1;step(0);step(5000);step(100000);assert(output.faults&PEN_CP_CONTACT_STUCK);assert(output.count==1&&output.events[0].flags==PEN_GAP);assert(!(output.actions&PEN_CP_SLEEP_REQUEST));
 reset();step(10);step(9);assert(output.faults&PEN_CP_CLOCK);input.recover_fault=1;step(100);assert(state.phase==PEN_CP_FAULT);
}
static void no_observation_and_invalid_config(void){
 reset();input.raw_contact=1;input.camera_ready=1;input.has_observation=0;step(0);step(5000);assert(output.count==1&&!(output.events[0].flags&PEN_VALID));assert(output.events[0].timestamp_us==0);step(6000);assert(output.count==0);
 pen_cp_config bad=config;bad.press_us=bad.contact_stuck_us;assert(pen_cp_init(&state,&bad)==-1);bad=config;bad.min_confidence=1001;assert(pen_cp_init(&state,&bad)==-1);
 reset();input.now_us=1;sample.timestamp_us=2;assert(pen_cp_step(&state,&input,&sample,&output)==-1);assert(!state.started);
}
int main(void){debounce_and_release();short_tap_and_overflow();camera_and_calibration();pickup_sleep_guards();stuck_and_clock();no_observation_and_invalid_config();puts("contact_power: buffered edges, gaps, readiness, release, sleep guards, stuck faults, clock recovery PASS");return 0;}
