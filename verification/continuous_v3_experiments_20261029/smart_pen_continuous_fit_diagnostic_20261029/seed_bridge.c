#include "fit_bridge.c"
/* Exploratory capture envelope ONLY; final candidate() gates are unchanged. */
int geometry_seeds(pen_continuous_workspace *ws,int n,double *seeds,unsigned capacity){
 pen_roi_workspace *w=&ws->core;unsigned count=0;
 for(int a=-60;a<=60;a+=2)for(int p=16;p<=64;p++)for(int r=6;r<=14;r++){
  double pitch=p*.5,angle=a,ratio=r*.1,co=cos(angle*PI/180),si=sin(angle*PI/180);
  for(int i=0;i<n;i++){
   w->u[i]=(w->points[i].x*co+w->points[i].y*si)/pitch;
   w->v[i]=(-w->points[i].x*si+w->points[i].y*co)/(pitch*ratio);
  }
  double ox=phase(w->u,n),oy=phase(w->v,n);
  for(int k=0;k<3;k++){
   double sx=0,sy=0;int nx=0,ny=0;
   for(int i=0;i<n;i++){double dx=residual(w->u[i]-ox),dy=residual(w->v[i]-oy);if(fabs(dx)>fabs(dy)){sy+=dy;ny++;}else{sx+=dx;nx++;}}
   if(nx)ox+=sx/nx;if(ny)oy+=sy/ny;
  }
  double error=0;int good=1;
  for(int i=0;i<n;i++){
   double dx=fabs(residual(w->u[i]-ox)),dy=fabs(residual(w->v[i]-oy));
   double major=fmax(dx,dy),minor=fmin(dx,dy);
   if(major<.03||major>.42||minor>.20){good=0;break;}
   error+=minor*minor+(major-1./6)*(major-1./6);
  }
  if(!good||error/n>.0064)continue;
  if(count<capacity){seeds[count*3]=pitch;seeds[count*3+1]=angle;seeds[count*3+2]=ratio;}
  count++;
 }
 return (int)count;
}
