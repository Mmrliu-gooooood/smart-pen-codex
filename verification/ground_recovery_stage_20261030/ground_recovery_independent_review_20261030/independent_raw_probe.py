from pathlib import Path
import os,re,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/ground-review-raw'
import pcbnew as p
R=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028');A=R/'hardware/camera_schmitt_native_0745/native/mainboard_revD.kicad_pcb';B=R/'hardware/ground_recovery_native_0818/native/mainboard_revD.kicad_pcb'
def blocks(s):
 depth=0;quote=False;esc=False;start=0
 for i,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield s[start:i+1]
   depth-=1
get=lambda f:{re.search(r'\(uuid "([^"]+)"\)',b).group(1):b for b in blocks(f.read_text())if b.startswith(('(segment','(via','(footprint'))}
a,b=get(A),get(B);changed=[u for u in a if b.get(u)!=a[u]];board=p.LoadBoard(str(B));fp=next(f for f in board.GetFootprints()if f.GetReference()=='J104');pad=next(q for q in fp.Pads()if q.GetNumber()=='3');via=next(t for t in board.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetPosition()==p.VECTOR2I(9350000,57250000));dist=math.hypot(pad.GetPosition().x-via.GetPosition().x,pad.GetPosition().y-via.GetPosition().y)/1e6
if changed:raise RuntimeError(changed)
print(json.dumps({'old_raw_copper_and_footprint_blocks_changed':changed,'new_blocks':len(set(b)-set(a)),'probe':{'footprint':fp.GetFPIDAsString(),'pad_shape':int(pad.GetShape()),'pad_size_mm':[pad.GetSize().x/1e6,pad.GetSize().y/1e6],'pad_xy_mm':[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6],'via_xy_mm':[9.35,57.25],'via_diameter_mm':via.GetWidth(p.F_Cu)/1e6,'via_drill_mm':via.GetDrillValue()/1e6,'center_distance_mm':dist,'copper_gap_mm':dist-pad.GetSize().x/2e6-via.GetWidth(p.F_Cu)/2e6,'has_B_paste':pad.IsOnLayer(p.B_Paste),'has_B_copper':pad.IsOnLayer(p.B_Cu)},'scope':'Geometry only; no mask expansion/tenting/fixture qualification'},indent=2))
