#pragma once
#include <stddef.h>
#include <stdint.h>
#define MALLOC_CAP_SPIRAM 1
#define MALLOC_CAP_8BIT 2
#define MALLOC_CAP_DMA 4
#define MALLOC_CAP_INTERNAL 8
#define MALLOC_CAP_DEFAULT 16
size_t heap_caps_get_largest_free_block(uint32_t);
void *heap_caps_malloc(size_t,uint32_t);
void *heap_caps_calloc(size_t,size_t,uint32_t);
void *heap_caps_aligned_calloc(size_t,size_t,size_t,uint32_t);
void *heap_caps_aligned_alloc(size_t,size_t,uint32_t);
