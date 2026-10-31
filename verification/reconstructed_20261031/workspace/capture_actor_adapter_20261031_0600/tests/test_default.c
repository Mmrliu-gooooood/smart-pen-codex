#include "adapter.h"
#include "board_provider.h"
#include "pen_capture_idf.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do{if(!(x))exit(1);}while(0)
static int called;
static int sink(void*x,const pen_app_input*i){(void)x;(void)i;called++;return 0;}
static void fault(void*x,int e){(void)x;(void)e;called++;}
int main(void){pen_adapter a={0};pen_capture c={0};CHECK(!PEN_ADAPTER_HOST_TEST);CHECK(pa_init(&a,&c,sink,fault,NULL,1)==PA_DISABLED);CHECK(pa_edge(&a,1,1,0)==PA_STATE);CHECK(pa_drain(&a,2)==PA_STATE);CHECK(!called);CHECK(!pen_get_board_provider());CHECK(!pen_capture_reviewed_profile("SC031GS"));puts("PASS default compile gate OFF/provider NULL/profile empty");}
