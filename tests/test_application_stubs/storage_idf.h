#ifndef ACTOR_STORAGE_STUB_H
#define ACTOR_STORAGE_STUB_H
#include "store.h"
#define ESP_OK 0
typedef struct {pen_store store;} pen_storage_idf;
int pen_storage_idf_open(pen_storage_idf*,int,const char*,uint32_t);
int pen_storage_idf_begin_boot(pen_storage_idf*,uint64_t*);
void pen_storage_idf_close(pen_storage_idf*);
#endif
