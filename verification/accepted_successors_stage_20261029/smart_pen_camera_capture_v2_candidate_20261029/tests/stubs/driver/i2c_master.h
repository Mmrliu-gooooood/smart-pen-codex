#ifndef TEST_I2C_MASTER_H
#define TEST_I2C_MASTER_H
#include <stddef.h>
#include <stdint.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_ARG -2
#define I2C_ADDR_BIT_LEN_7 7
#define I2C_CLK_SRC_DEFAULT 0
#define I2C_NUM_MAX 2
typedef void *i2c_master_dev_handle_t;
typedef void *i2c_master_bus_handle_t;
typedef struct {int dev_addr_length,device_address,scl_speed_hz;} i2c_device_config_t;
typedef struct {int clk_source,i2c_port,scl_io_num,sda_io_num,glitch_ignore_cnt;struct {unsigned enable_internal_pullup;}flags;} i2c_master_bus_config_t;
int i2c_master_get_bus_handle(int,i2c_master_bus_handle_t*);
int i2c_master_bus_add_device(i2c_master_bus_handle_t,const i2c_device_config_t*,i2c_master_dev_handle_t*);
int i2c_new_master_bus(const i2c_master_bus_config_t*,i2c_master_bus_handle_t*);
int i2c_master_bus_rm_device(i2c_master_dev_handle_t);
int i2c_del_master_bus(i2c_master_bus_handle_t);
int i2c_master_probe(i2c_master_bus_handle_t,uint16_t,int);
int i2c_master_transmit_receive(i2c_master_dev_handle_t,const uint8_t*,size_t,uint8_t*,size_t,int);
int i2c_master_transmit(i2c_master_dev_handle_t,const uint8_t*,size_t,int);
int i2c_master_receive(i2c_master_dev_handle_t,uint8_t*,size_t,int);
const char *esp_err_to_name(int);
#endif
