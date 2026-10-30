#include "update_policy.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static pen_update_safety safe={true,true,true,true,true};
static pen_update_policy policy={1,1,4096,"smartpen-p1","smartpen-p1",true,true,true,false};
static pen_update_manifest manifest={100,2,"smartpen-p1","smartpen-p1",{0}};
int main(void){
 char largest[32]="4294967295";uint32_t parsed=99;assert(!pen_update_version_parse(largest,&parsed)&&parsed==UINT32_MAX);
 const char invalid[6][32]={"","01","-1","1.0","4294967296","1x"};for(unsigned i=0;i<6;i++){assert(pen_update_version_parse(invalid[i],&parsed));}
 char unclosed[32];memset(unclosed,'1',32);assert(pen_update_version_parse(unclosed,&parsed));
 pen_update_transaction t={0};assert(!pen_update_start(&t,&policy,&manifest,&safe));
 assert(!pen_update_chunk(&t,0,40,&safe));assert(!pen_update_chunk(&t,40,60,&safe));assert(!pen_update_finish(&t,true,true,&safe));assert(t.state==PEN_UPDATE_READY);
 for(unsigned i=0;i<5;i++){pen_update_safety s=safe;bool *fields[]={&s.authorized,&s.contact_up,&s.power_qualified,&s.storage_durable,&s.recording_idle};*fields[i]=false;t=(pen_update_transaction){0};assert(pen_update_start(&t,&policy,&manifest,&s));assert(!pen_update_boot_healthy(31,&s));}
 for(unsigned i=0;i<4;i++){pen_update_policy p=policy;if(i==0)p.enabled=false;if(i==1)p.signatures_enforced=false;if(i==2)p.rollback_enabled=false;if(i==3)p.pending_verify=true;t=(pen_update_transaction){0};assert(pen_update_start(&t,&p,&manifest,&safe));}
 {pen_update_policy p=policy;pen_update_manifest m=manifest;p.hardware="other-board";strcpy(m.hardware,"other-board");t=(pen_update_transaction){0};assert(pen_update_start(&t,&p,&m,&safe));}
 for(unsigned i=0;i<5;i++){pen_update_manifest m=manifest;if(i==0)m.bytes=0;if(i==1)m.bytes=4097;if(i==2)m.version=1;if(i==3)m.project[0]='x';if(i==4)memset(m.hardware,'x',32);t=(pen_update_transaction){0};assert(pen_update_start(&t,&policy,&m,&safe));}
 for(unsigned i=0;i<4;i++){t=(pen_update_transaction){0};assert(!pen_update_start(&t,&policy,&manifest,&safe));if(i==0)assert(pen_update_chunk(&t,1,10,&safe));if(i==1)assert(pen_update_chunk(&t,0,101,&safe));if(i==2)assert(pen_update_chunk(&t,0,0,&safe));if(i==3){assert(!pen_update_chunk(&t,0,50,&safe));assert(pen_update_finish(&t,true,true,&safe));}assert(t.state==PEN_UPDATE_FAILED);assert(pen_update_chunk(&t,0,1,&safe));}
 for(unsigned i=0;i<2;i++){t=(pen_update_transaction){0};assert(!pen_update_start(&t,&policy,&manifest,&safe));assert(!pen_update_chunk(&t,0,100,&safe));assert(pen_update_finish(&t,i!=0,i!=1,&safe));}
 for(unsigned i=0;i<5;i++){assert(!pen_update_boot_healthy(31u&~(1u<<i),&safe));}assert(pen_update_boot_healthy(31,&safe));
 puts("update policy: gates, ranges, anti-downgrade, partial/corrupt image, ordering, boot diagnostics PASS");return 0;
}
