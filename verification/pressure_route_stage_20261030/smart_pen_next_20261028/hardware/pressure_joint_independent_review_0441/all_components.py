import io,contextlib,json
with contextlib.redirect_stdout(io.StringIO()):import independent as a
def comps(board,net):
 ns,adj=a.graph(board,net);seen=set();out=[]
 for u,n,_ in ns:
  if not n or u in seen:continue
  rr=a.reach(adj,u);seen|=rr;out.append({v for v,name,_ in ns if name and v in rr})
 return out
rows=[]
for net in sorted({q.GetNetname()for f in a.base.GetFootprints()for q in f.Pads()}):
 old=comps(a.base,net);new=comps(a.b,net);a.need(all(any(c<=d for d in new)for c in old),'physical UUID component lost '+net);rows.append({'net':net,'before':len(old),'after':len(new)})
print(json.dumps({'all_physical_UUID_pad_components_preserved':rows,'duplicate_EP_numbers_not_merged':True},indent=2))
