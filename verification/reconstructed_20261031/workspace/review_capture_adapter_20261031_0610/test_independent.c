/* Independent adversarial extension; original fixtures imported unchanged. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main authored_main
#include "../capture_actor_adapter_20261031_0600/tests/test_failures.c"
#undef main
#pragma GCC diagnostic pop
static unsigned rng=0x1337u;
static unsigned rnd(void){rng=rng*1664525u+1013904223u;return rng>>8;}
int main(void){
 for(unsigned trial=0;trial<10000;trial++){
  setup();
  struct ev {uint64_t t;unsigned kind;uint8_t c;} events[8];
  for(unsigned j=0;j<8;j++){
   events[j]=(struct ev){100u+rnd()%5u,rnd()%2u,(uint8_t)(rnd()%2u)};
   CHECK(events[j].kind?pa_idle(&adapter,events[j].t)==PA_OK:pa_edge(&adapter,events[j].t,events[j].c,0)==PA_OK);
  }
  for(unsigned j=1;j<8;j++){struct ev e=events[j];unsigned n=j;while(n&&(events[n-1].t>e.t||(events[n-1].t==e.t&&events[n-1].kind>e.kind))){events[n]=events[n-1];n--;}events[n]=e;}
  CHECK(pa_drain(&adapter,102)==PA_OK);
  unsigned cutoff=0;while(cutoff<8&&events[cutoff].t<=102)cutoff++;
  CHECK(calls==cutoff);CHECK(pa_drain(&adapter,102)==PA_OK);CHECK(calls==cutoff);
  CHECK(pa_drain(&adapter,104)==PA_OK);CHECK(calls==8);
  uint8_t level=0;for(unsigned j=0;j<8;j++){if(!events[j].kind)level=events[j].c;CHECK(seen[j]==events[j].t);CHECK(contact[j]==level);}
  CHECK(pa_stop(&adapter)==PA_OK);
 }
 /* Runtime gate cannot reinitialize a live adapter. */
 setup();CHECK(pa_init(&adapter,&capture,sink,fault,NULL,0)==PA_STATE);CHECK(adapter.enabled);CHECK(pa_stop(&adapter)==PA_OK);
 printf("PASS independent 10000 seeded eight-event tie/cutoff/permutation sequences (%u checks)\n",checks);
}
