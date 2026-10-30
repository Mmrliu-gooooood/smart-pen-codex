#ifndef BENCH_TRACE_H
#define BENCH_TRACE_H
#include "roi_continuous.h"
void bench_trace_reset(void);
pen_roi_refine_diagnostics bench_trace_get(void);
unsigned bench_trace_calls(void);
#endif
