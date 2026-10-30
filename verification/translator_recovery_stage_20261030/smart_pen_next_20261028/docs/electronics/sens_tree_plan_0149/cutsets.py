from geometry import *
r=json.loads((D/'comparison.json').read_text());lookup={t.m_Uuid.AsString():t for t in old};lookup.update(pm);rows=[]
for c in r['candidates']:
 blocked=[]
 for z in c['checks']:
  if not z['conflicts']:continue
  obs=[]
  for v in z['conflicts']:
   if v[0]=='copper':
    q=lookup[v[3]];bb=shape(q,b.GetLayerID(v[4])).BBox();obs.append(dict(net=v[2],id=v[3],layer=v[4],copper_bbox_mm=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]))
   else:obs.append(dict(other=v))
  blocked.append(dict(index=z['index'],candidate_object=z['object'],blocking_objects=obs))
 rows.append(dict(topology=c['topology'],blocked_edges=blocked,interpretation='Exact collision cut list of this proposed tree, NOT a graph-theoretic global minimum cut or proof of board unroutability. No removal of blockers authorized.'))
(D/'cutsets.json').write_text(json.dumps(rows,indent=2)+'\n')
print('base unchanged',hashlib.sha256(S.read_bytes()).hexdigest())
