import reference_final as r,json
p=r.p;ts=[t for u,t in r.bb.items()if u not in r.aa and t.GetClass()!='PCB_VIA'];out=[]
for i,t in enumerate(ts):
 for q in ts[:i]:
  if (t.GetNetname(),t.GetLayer(),t.GetWidth())!=(q.GetNetname(),q.GetLayer(),q.GetWidth()):continue
  a,z=t.GetStart(),t.GetEnd();c,d=q.GetStart(),q.GetEnd()
  shared=next((x for x in[a,z]if x==c or x==d),None)
  if shared is None:continue
  x=z if a==shared else a;y=d if c==shared else c;dx=x.x-shared.x;dy=x.y-shared.y;ex=y.x-shared.x;ey=y.y-shared.y
  if dx*ey-dy*ex==0 and dx*ex+dy*ey<0:out.append([t.m_Uuid.AsString(),q.m_Uuid.AsString()])
(r.D/'collinear_screen.json').write_text(json.dumps({'exact_collinear_adjacent_pairs':out,'count':len(out),'scope':'Exact integer endpoint/collinearity screen on new tracks only. No aesthetic non-collinear smoothing or reference-changing simplification.'},indent=2));print(out)
