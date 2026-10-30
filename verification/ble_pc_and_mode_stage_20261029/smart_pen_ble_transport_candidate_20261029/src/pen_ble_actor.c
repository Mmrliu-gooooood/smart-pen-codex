#include "pen_ble_actor.h"
#include <string.h>
int pen_ble_core_authorize(pen_ble_core*c,const pen_ble_ticket*t,pen_ble_grant*g){
 if(!c||!t||!g)return -1;
 memset(g,0,sizeof *g);
 if(c->faulted)return -1;
 if(!pen_ble_core_ready(c)||!t->app||!t->nonce||!c->offered||t->epoch!=c->security.connection_epoch||t->session!=c->offered_session||t->seq!=c->offered_seq)return -3;
 pen_ble_ack a;int r=pen_ble_core_pop(c,&a);if(r)return r;
 if(a.receipt.connection_epoch!=t->epoch||a.session!=t->session||a.seq!=t->seq||
    !a.receipt.encrypted||!a.receipt.authenticated||!a.receipt.bonded||!a.receipt.approved_peer)return -3;
 /* Linearization point: later disconnect cannot revoke this authenticated,
  * exact ACK. It can only prevent authorization of another one. */
 g->ticket=*t;g->authorized=1;pen_ble_core_committed(c,&a);return 0;
}
int pen_ble_actor_init(pen_ble_actor*b,pen_app*a,const pen_ble_backend*t){
 if(!b||!a||!a->initialized||!t||!t->security||!t->send||!t->authorize)return -1;
 memset(b,0,sizeof *b);b->app=a;b->backend=*t;return 0;
}
static int same(const pen_ble_ticket*a,const pen_ble_ticket*b){return a->app==b->app&&a->nonce==b->nonce&&a->session==b->session&&a->epoch==b->epoch&&a->seq==b->seq;}
static int turn(pen_ble_actor*b){
 pen_app*a=b->app;
 if(a->sleep_prepared)return -3;
 if(a->sent_pending){
  if(b->nonce==UINT64_MAX)return -1;
  pen_ble_ticket t={.app=(uintptr_t)a,.nonce=++b->nonce,.session=a->sent_session,.epoch=a->sent_epoch,.seq=a->sent_seq};
  pen_ble_grant g={0};int r=b->backend.authorize(b->backend.ctx,&t,&g);
  if(r<0&&r!=-3)return -1;
  if(!r){
   /* Private grant stays on this stack. Consume before any durable callback;
    * an I/O failure never retries it and must stop this actor. */
   int valid=g.authorized==1&&same(&t,&g.ticket)&&a->initialized&&!a->sleep_prepared&&
    a->sent_pending&&a->sent_session==t.session&&a->sent_seq==t.seq&&a->sent_epoch==t.epoch;
   memset(&g,0,sizeof g);
   if(!valid)return -1;
   a->sent_pending=0;
   if(pen_store_ack(a->recorder.store,t.session,t.seq,1))return -1;
  }
 }
 pen_link_security security={0};
 int r=b->backend.security(b->backend.ctx,&security);if(r)return r<0?-1:1;
 r=pen_app_offer(a,&security,b->backend.send,b->backend.ctx);
 return r;
}
int pen_ble_actor_turn(pen_ble_actor*b){
 if(!b||!b->app||b->faulted||b->busy)return -1;
 b->busy=1;int r=turn(b);b->busy=0;
 if(r==-1){b->faulted=1;b->app->sent_pending=0;}
 return r;
}
