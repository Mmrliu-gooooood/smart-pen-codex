from pathlib import Path
import os,json,hashlib,re,collections,sys
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
from copper_geometry import build,components,shape,L
D=Path(__file__).resolve().parent;B=D.parents[1]/'j202_low_speed_reference_candidate'
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
candidate=Path(sys.argv[1])if len(sys.argv)>1 else D/'native/mainboard_revD.kicad_pcb'
a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(candidate))
def blocks(file,kind):
 t=file.read_text();out={}
 for s in re.findall(r'\n\t\('+kind+r'[^\n]*\n.*?\n\t\)',t,re.S):
  u=re.search(r'\(uuid "([^"\n]+)"\)',s)
  if u:out[u[1]]=s
 return out
req(blocks(B/'native/mainboard_revD.kicad_pcb','footprint')==blocks(candidate,'footprint'),'FOOTPRINT_CHANGE')
za,zb=[blocks(q,'zone') for q in [B/'native/mainboard_revD.kicad_pcb',candidate]]
strip=lambda q:re.sub(r'\n\t\t\(filled_polygon\n.*?\n\t\t\)','',q,flags=re.S)
req(za.keys()==zb.keys(),'ZONE_SET')
for u in za:req(strip(za[u])==strip(zb[u]),'ZONE_CONFIG '+u)
sourcecount=0
for f in (B/'native').rglob('*'):
 if f.is_file()and f.suffix in ['.kicad_sch','.kicad_pro','.kicad_dru']:
  req(sha(f)==sha(D/'native'/f.relative_to(B/'native')),'SOURCE_CHANGED '+str(f));sourcecount+=1
def tg(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={t.m_Uuid.AsString():tg(t)for t in a.GetTracks()};bt={t.m_Uuid.AsString():tg(t)for t in b.GetTracks()};removed={u:at[u]for u in at.keys()-bt.keys()};added={u:bt[u]for u in bt.keys()-at.keys()};modified={u:{'before':at[u],'after':bt[u]}for u in at.keys()&bt.keys()if at[u]!=bt[u]}
req(all(v[1]in ['USB_EN1','SENS_TRIG_IN']for v in list(removed.values())+list(added.values())),'UNRELATED_NET_CHANGE')
req(all(v['before'][1]==v['after'][1]=='USB_EN1'for v in modified.values()),'UNRELATED_MODIFICATION')
(D/'exact_copper_delta.json').write_text(json.dumps({'removed':removed,'added':added,'modified':modified},indent=2))
print('Copper delta',len(removed),len(added),len(modified),flush=True)
na,nb=build(a),build(b);ca={n:components(v)for n,v in na.items()};cb={n:components(v)for n,v in nb.items()};req(ca==cb,'OLD_PAD_GRAPH_CHANGED')
islands={}
for n,anchor in [('3V3_AON','C104.1'),('GND','C104.2')]:
 tagged=[(name,pad or '/'in name,ss)for name,pad,ss in nb[n]];cc=components(tagged);core=next(c for c in cc if anchor in c);zs=[name for name,pad,ss in nb[n]if '/'in name];req(all(z in core for z in zs),'ISLAND_NOT_CORE '+n);islands[n]=len(zs)
# All exact new copper polygons checked against all other-net finite copper incl planes.
shorts=[]
for u in added:
 t=next(t for t in b.GetTracks()if t.m_Uuid.AsString()==u);ss={l:shape(t,l)for l in L if t.IsOnLayer(l)}
 for n,nodes in nb.items():
  if n==t.GetNetname():continue
  for ident,pad,tt in nodes:
   for l in ss.keys()&tt.keys():
    if not ss[l].BBox().Intersects(tt[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],tt[l])
    if q.Area()>1:shorts.append([u,n,ident,b.GetLayerName(l),q.Area()/1e12])
req(not shorts,'NEW_FOREIGN_COPPER_INTERSECTION')
body=p.SHAPE_POLY_SET();body.NewOutline()
for x,y in[(.05,90),(13.95,90),(13.95,94),(.05,94)]:body.Append(round(x*1e6),round(y*1e6))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in added:
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,p.B_Cu),body);req(q.Area()<=1,'NEW_VIA_UNQUALIFIED_CONNECTOR_UNDERSIDE')
# Reserved full lanes, no hypothetical via or endpoint claims.
for l in [p.F_Cu,p.In3_Cu,p.B_Cu]:
 for x in [12.6,12.9,13.2,13.5]:
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(round(x*1e6),32000000));t.SetEnd(p.VECTOR2I(round(x*1e6),89000000));t.SetWidth(449998);t.SetLayer(l);g=shape(t,l)
  for n,nodes in nb.items():
   for ident,pad,ss in nodes:
    if l not in ss:continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(g,ss[l]);req(q.Area()<=1,'CORRIDOR_BLOCK '+n+' '+ident+' '+str(x))
# Retain original full violation multiset; counts alone insufficient.
x,y=[json.loads(f.read_text())for f in [D/'baseline_fresh_drc.json',D/'trimmed_drc.json']]
def canon(o):
 z=dict(o);z['items']=sorted(z.get('items',[]),key=lambda a:json.dumps(a,sort_keys=True));return json.dumps(z,sort_keys=True)
req(collections.Counter(map(canon,x['violations']))==collections.Counter(map(canon,y['violations'])),'FULL_DRC_MULTISET_CHANGED')
counts={k:len(y[k])for k in ['violations','unconnected_items','schematic_parity']};req(list(counts.values())==[17,21,0],'FULL_DRC_COUNTS')
out={'status':'SCOPED_LOW_SPEED_REROUTE_ONLY_NOFAB','pcb_sha256':sha(candidate),'base_sha256':sha(B/'native/mainboard_revD.kicad_pcb'),'source_project_files_unchanged':sourcecount,'footprints_unchanged':len(b.GetFootprints()),'all_pad_components_equal':True,'plane_islands_in_core':islands,'new_foreign_intersections':shorts,'reserved_lanes_clear':12,'full_counts':counts,'historical_baseline_counts':[17,21,0],'fresh_baseline_counts':[17,21,0],'historical_difference_note':'An initial command omitted --all-track-errors and gave an incomplete 16 findings. Corrected full-mode baseline and candidate both have 17 findings; no old short repaired.','full_violation_multiset_equal':True,'delta_counts':{'removed':len(removed),'added':len(added),'modified':len(modified)},'pad_components':cb}
(D/'verify_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='pad_components'},indent=2))
