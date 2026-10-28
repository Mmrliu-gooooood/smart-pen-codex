#define main mock_enabled_exercises_main
#include "test_update_idf_mock.c"
#undef main
int main(void){reset();pen_update_idf u={0};assert(pen_update_idf_begin(&u,&manifest,&safe)==ESP_ERR_INVALID_STATE);assert(!begin_calls&&!select_calls);assert(pen_update_idf_boot_result(31,false,false,&safe)==ESP_ERR_INVALID_STATE);assert(!valid_calls&&!rollback_calls);puts("disabled/unsafe SDK configuration has zero hardware update calls PASS");return 0;}
