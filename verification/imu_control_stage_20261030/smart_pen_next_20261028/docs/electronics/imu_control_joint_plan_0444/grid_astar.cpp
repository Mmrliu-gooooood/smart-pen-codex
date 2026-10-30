#include <cstdio>
#include <vector>
#include <queue>
#include <cmath>
#include <cstdint>
#include <limits>
#include <algorithm>
struct Q{double f,g;int i; bool operator<(Q const&o)const{return f>o.f;}};
bool midpoint_ok(double x,double y){
 const double ax[6]={12,14,14,0,0,12},ay[6]={6,6,95,-6.5,95,-6.5};
 const double bx[6]={14,14,0,12,0,12},by[6]={6,95,95,-6.5,-6.5,6};
 bool in=false;double best=1e100;
 for(int i=0;i<6;i++){double dx=bx[i]-ax[i],dy=by[i]-ay[i],t=std::clamp(((x-ax[i])*dx+(y-ay[i])*dy)/(dx*dx+dy*dy),0.0,1.0);best=std::min(best,pow(x-ax[i]-t*dx,2)+pow(y-ay[i]-t*dy,2));if((ay[i]>y)!=(by[i]>y))if(x<(bx[i]-ax[i])*(y-ay[i])/(by[i]-ay[i])+ax[i])in=!in;}
 return in&&best>=pow(.325-1e-9,2);
}
int main(int argc,char**argv){if(argc!=3)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 3;int hd[5];if(fread(hd,4,5,f)!=5)return 4;int K=hd[0],X=hd[1],Y=hd[2],NS=hd[3],NG=hd[4],P=X*Y,N=K*P;double params[3];fread(params,8,3,f);std::vector<uint8_t>obs(N),vb(P),soft(N),sv(P),goal(N);std::vector<float>h(P);std::vector<int>starts(NS),goals(NG);fread(obs.data(),1,N,f);fread(vb.data(),1,P,f);fread(soft.data(),1,N,f);fread(sv.data(),1,P,f);fread(h.data(),4,P,f);fread(starts.data(),4,NS,f);fread(goals.data(),4,NG,f);fclose(f);for(int i:goals)goal[i]=1;std::vector<double>d(N,std::numeric_limits<double>::infinity());std::vector<int>pr(N,-1);std::priority_queue<Q>q;for(int i:starts){d[i]=0;q.push({h[i%P]*params[2],0,i});}int dx[8]={-1,1,0,0,-1,-1,1,1},dy[8]={0,0,-1,1,-1,1,-1,1};long pops=0;int end=-1;while(!q.empty()){Q a=q.top();q.pop();if(a.g>d[a.i]+1e-9)continue;if(++pops>20000000)break;if(goal[a.i]){end=a.i;break;}int k=a.i/P,j=a.i%P,x=j/Y,y=j%Y;auto relax=[&](int ni,double cost){double ng=a.g+cost;if(ng+1e-9<d[ni]){d[ni]=ng;pr[ni]=a.i;q.push({ng+h[ni%P]*params[2],ng,ni});}};for(int z=0;z<8;z++){int xx=x+dx[z],yy=y+dy[z];if(xx<0||xx>=X||yy<0||yy>=Y)continue;int ni=k*P+xx*Y+yy;if(obs[ni])continue;if(!midpoint_ok((x+xx)*.0125,(y+yy)*.0125))continue;if(dx[z]&&dy[z]&&(obs[k*P+(x+dx[z])*Y+y]||obs[k*P+x*Y+y+dy[z]]))continue;relax(ni,(z<4?1:sqrt(2.0))+(double(soft[ni])*params[0]));}if(!vb[j])for(int kk=0;kk<K;kk++)if(kk!=k&&!obs[kk*P+j])relax(kk*P+j,35+(double(sv[j])*params[1]));}FILE*out=fopen(argv[2],"wb");fprintf(out,"%d %ld\n",end>=0,pops);if(end>=0){std::vector<int>path;for(int i=end;i>=0;i=pr[i])path.push_back(i);std::reverse(path.begin(),path.end());fprintf(out,"%.12f %zu\n",d[end],path.size());for(int i:path)fprintf(out,"%d %d %d\n",i/P,(i%P)/Y,i%Y);}fclose(out);return end>=0?0:5;}
