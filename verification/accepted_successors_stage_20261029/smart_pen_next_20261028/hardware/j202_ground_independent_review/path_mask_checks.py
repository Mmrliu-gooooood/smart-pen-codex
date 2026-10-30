from pathlib import Path
import json,math
import pcbnew as p
from copper_geometry import shape
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));ts={t.m_Uuid.AsString():t for t in b.GetTracks()};j=next(f for f in b.GetFootprints()if f.GetReference()=='J202');pads={q.GetNumber():q for q in j.Pads()};links=json.loads((D/'ground_links.json').read_text());lengths={}
def need(v,s):
 if not v:raise RuntimeError(s)
for r in links:
 path=r['path'];need(len(r['tracks'])==len(path)-1,'path track count')
 for uid,aa,zz in zip(r['tracks'],path,path[1:]):
  t=ts[uid];need([t.GetStart().x,t.GetStart().y]==[round(v*1e6)for v in aa]and[t.GetEnd().x,t.GetEnd().y]==[round(v*1e6)for v in zz],'declared path not real')
 need([pads[r['pin']].GetPosition().x,pads[r['pin']].GetPosition().y]==[round(v*1e6)for v in path[0]],'real pad position')
 lengths[r['pin']]=sum(ts[u].GetLength()/1e6 for u in r['tracks'])
bar=next(ts[u]for r in links if r['pin']=='13'for u in r['tracks']if ts[u].GetStart().y==91200000 and ts[u].GetEnd().y==91200000);barshape=shape(bar,p.B_Cu)
def dist(q,z):
 lo=0;hi=2000000
 while lo<hi:
  mid=(lo+hi)//2
  if q.Collide(z,mid):hi=mid
  else:lo=mid+1
 return hi/1e6
mask={}
for n,pad in pads.items():
 if n.isdigit() and pad.IsOnLayer(p.B_Mask):
  q=shape(pad,p.B_Cu);e=pad.GetSolderMaskExpansion(p.B_Cu)
  if e:q.Inflate(e,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,250,True)
  mask[n]=q
web=min(dist(mask[str(n)],mask[str(n+1)])for n in range(1,24));gap=min(dist(barshape,mask[n])for n in mask if pads[n].GetNetname()!='GND')
need(abs(web-.2)<.000002 and abs(gap-.225)<.000002,'nominal actual mask geometry')
print(json.dumps({'declared_paths_match_all_actual_track_endpoints':True,'actual_track_length_by_pin_mm':lengths,'pin13_plus_pin10_shared_length_mm':lengths['13']+lengths['10'],'actual_min_adjacent_signal_mask_web_mm':web,'actual_pin13_bar_to_signal_mask_mm':gap,'limits':'Native polygons only; no board-house mask registration/underside tolerance approval'},indent=2))
