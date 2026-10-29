import pathlib,json,hashlib,collections,pcbnew as p
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];B=R/'hardware/power_integrated_layout_14x45';C=R/'hardware/power14_single_feed_revB';m=json.loads((C/'SINGLE_FEED_REVB_MANIFEST.json').read_text())
for name,sha in m['files'].items():
 if hashlib.sha256((C/name).read_bytes()).hexdigest()!=sha:raise RuntimeError('Candidate manifest mismatch '+name)
b=p.LoadBoard(str(B/'power_integrated_study.kicad_pcb'));c=p.LoadBoard(str(C/'power_integrated_study.kicad_pcb'))
def geom(t):
 base=[t.GetNetname().removeprefix('/core/').lstrip('/'),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y]
 return base+(['via',t.GetWidth(p.F_Cu),t.GetDrillValue(),t.TopLayer(),t.BottomLayer()] if isinstance(t,p.PCB_VIA) else ['track',t.GetWidth(),t.GetLayer()])
ba={t.m_Uuid.AsString():geom(t) for t in b.GetTracks()};ca={t.m_Uuid.AsString():geom(t) for t in c.GetTracks()}
removed=sorted(ba.keys()-ca.keys());added=sorted(ca.keys()-ba.keys());changed=[u for u in ba.keys()&ca.keys() if ba[u]!=ca[u]]
if changed or len(removed)!=26 or len(added)!=43:raise RuntimeError('Unexpected geometry changes')
def fps(board):
 return sorted((f.GetReference(),f.GetValue(),f.GetAttributes(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),(f.GetFPID().GetLibNickname(),f.GetFPID().GetLibItemName()),sorted((a.GetNumber(),a.GetNetname(),a.GetPosition().x,a.GetPosition().y,a.GetSize().x,a.GetSize().y,str(a.GetLayerSet().FmtBin())) for a in f.Pads())) for f in board.GetFootprints())
if fps(b)!=fps(c):raise RuntimeError('Footprint/pad/defaults changed')
for name in ['core.kicad_sch','thermal.kicad_sch','power_integrated_study.kicad_sch','power_integrated_study.kicad_pro']:
 if (B/name).read_bytes()!=(C/name).read_bytes():raise RuntimeError('Unexpected schematic/project change '+name)
def fills(board):
 out=[]
 for z in board.Zones():
  q=z.GetFilledPolysList(z.GetLayer());out.append({'net':z.GetNetname(),'layer':board.GetLayerName(z.GetLayer()),'islands':q.OutlineCount(),'area_mm2':q.Area()/1e12})
 return out
core=p.LoadBoard(str(R/'hardware/power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));core_geom={t.m_Uuid.AsString():geom(t) for t in core.GetTracks()};expected={u:g for u,g in core_geom.items() if u in ba}
for g in expected.values():
 if g[0]=='CE_PERMISSION_EXTERNAL':g[0]='CE_PERMISSION_INTERNAL' # documented unified-source rename already present in14x45 baseline
if any(ca.get(u)!=g for u,g in expected.items()):raise RuntimeError('Original retained core copper changed')
out={'retained_original_core_items':len(expected),'manifest_files_matched':len(m['files']),'same_source_and_project':True,'same_footprints_pads_defaults':True,'unchanged_common_track_via_geometries':len(ba.keys()&ca.keys()),'removed':{u:ba[u] for u in removed},'added':{u:ca[u] for u in added},'fills_before':fills(b),'fills_after':fills(c),'status':'Geometry delta verified; separate physical contact check required'}
(D/'delta_result.json').write_text(json.dumps(out,indent=2)+'\n');print('Manifest48/source/defaults match;26removed43added;allcommontrackvia unchanged')
