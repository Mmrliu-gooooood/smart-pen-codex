#ifndef APP_STUB_LOG_H
#define APP_STUB_LOG_H
void actor_log(const char*,const char*,...);
#define ESP_LOGW actor_log
#endif
