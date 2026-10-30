/* Independent white-box bounded numerical rejection tests; frozen TU included verbatim. */
#include "roi_projective.c"
#include <assert.h>
#include <float.h>
#include <stdio.h>
static pen_projective_workspace ws;
int main(void){
 double good[9]={10,0,0,0,10,0,0,0,1},h[9],inv[9],u,v;unsigned checks=0;
 assert(geometry_valid(good));checks++;
 for(int i=0;i<9;i++)for(int k=0;k<3;k++){
  memcpy(h,good,sizeof h);h[i]=k==0?NAN:k==1?INFINITY:-INFINITY;
  u=123;v=456;assert(!pen_projective_map_v4(h,1,2,&u,&v)&&u==123&&v==456);assert(!geometry_valid(h));checks++;
 }
 memset(h,0,sizeof h);assert(!inverse(h,inv)&&!geometry_valid(h));checks++;
 memcpy(h,good,sizeof h);h[0]=-10;assert(!geometry_valid(h));checks++;
 memcpy(h,good,sizeof h);h[6]=1;assert(!geometry_valid(h));checks++; /* inverse denominator crosses horizon in crop */
 memcpy(h,good,sizeof h);h[8]=1e-12;u=123;v=456;assert(!pen_projective_map_v4(h,0,0,&u,&v)&&u==123&&v==456);checks++;
 memcpy(h,good,sizeof h);h[0]=DBL_MAX;u=123;v=456;assert(!pen_projective_map_v4(h,2,0,&u,&v)&&u==123&&v==456);checks++;
 double a[8][9]={{0}};assert(!solve(a,h));checks++;
 for(int i=0;i<8;i++)a[i][i]=1;a[7][7]=1e-12;assert(!solve(a,h));checks++;
 pen_roi_config cfg={710,1000,10,2};pen_projective_result out,old;memset(&out,0xa5,sizeof out);old=out;
 for(int k=0;k<4;k++){ws.all[0].x=k==0?NAN:k==1?INFINITY:k==2?DBL_MAX:1000000;ws.all[0].y=0;assert(!validate_projective(&ws,1,&cfg,good,&out));assert(memcmp(&out,&old,sizeof out)==0);checks++;}
 printf("PASS %u independent bounded numerical checks: NaN/Inf coefficients, degenerate solve, mirror, crop horizon, map overflow, huge grid conversion; no frozen source edits\n",checks);
}
