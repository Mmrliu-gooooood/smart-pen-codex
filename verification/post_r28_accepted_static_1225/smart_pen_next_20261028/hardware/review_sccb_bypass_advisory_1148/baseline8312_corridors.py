import geometry_native as g,json,sys,math
p=g.p;D=g.D;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from native_polygon import native_fractured_once
# Snapshot geometry + announced AON objects, memory only. No source/candidate save.
g.b=p.LoadBoard(str(D/'baseline8312.kicad_pcb'))
g.b.BuildConnectivity();start=(3.8875,66.875);targets=[(10,63.4),(12,67),(12,65.775)];rows=[]
for layer in[p.In1_Cu,p.In4_Cu]:
 plane=p.SHAPE_POLY_SET()
 for z in g.b.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()=='GND'and z.GetLayer()==layer:plane.BooleanAdd(native_fractured_once(z.GetFilledPolysList(layer)))
 for end in targets:
  same=[]
  for i in range(plane.OutlineCount()):
   unit=plane.UnitSet(i)
   if unit.Contains(g.V(start))and unit.Contains(g.V(end)):same.append(i)
  length=math.dist(start,end);n=math.ceil(length/.01);bad=[];run=None
  for j in range(n+1):
   f=j/n;xy=[start[k]+f*(end[k]-start[k])for k in range(2)];inside=plane.Contains(g.V(xy))
   if not inside and run is None:run=xy
   if inside and run is not None:bad.append([run,xy]);run=None
  if run is not None:bad.append([run,list(end)])
  corridors=[]
  for width in [.15,.3,.5]:
   t=g.track('GND',p.F_Cu,start,end,width);q=g.shape(t,p.F_Cu);q.BooleanSubtract(plane);corridors.append({'width_mm':width,'area_outside_GND_mm2':q.Area()/1e12})
  rows.append({'nominal_straight_corridors':corridors,'layer':g.b.GetLayerName(layer),'end_mm':end,'same_filled_GND_island_indices':same,'straight_centerline_span_mm':length,'sample_spacing_max_mm':.01,'straight_line_outside_plane_runs_mm':bad,'note':'Line samples expose holes/detours, not current-density or inductance calculation.'})
print(json.dumps(rows,indent=2));(D/'baseline8312_corridors.json').write_text(json.dumps(rows,indent=2)+'\n')
