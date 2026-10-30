#pragma once
#define GPIO_IS_VALID_GPIO(p) ((p)>=0 && (p)<=48 && ((p)<22 || (p)>25))
#define GPIO_IS_VALID_OUTPUT_GPIO(p) (GPIO_IS_VALID_GPIO(p) && (p)!=46)
#include <stdint.h>
typedef struct {uint64_t pin_bit_mask;int mode;} gpio_config_t;
#define GPIO_MODE_OUTPUT 1
static inline int gpio_config(const gpio_config_t*c){(void)c;return 0;}
static inline int gpio_set_level(int p,int v){(void)p;(void)v;return 0;}
