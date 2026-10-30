from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-native1950-config'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'dvp_joint_native_candidate_1950/native/mainboard_revD.kicad_pcb';N=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(S));b=p.LoadBoard(str(N))
def req(x,msg):
 if not x:raise RuntimeError(msg)
def xy(v):return[v.x,v.y]
def fp(f):return{'ref':f.GetReference(),'value':f.GetValue(),'xy':xy(f.GetPosition()),'side':f.GetLayer(),'angle':f.GetOrientationDegrees(),'pads':sorted((q.GetNumber(),q.GetNetname(),q.GetLayerSet().FmtHex(),xy(q.GetPosition()),xy(q.GetSize()),q.GetOrientationDegrees(),q.GetShape())for q in f.Pads())}
x={f.GetReference():fp(f)for f in a.GetFootprints()};y={f.GetReference():fp(f)for f in b.GetFootprints()};changed=[r for r in x if x[r]!=y[r]];req(set(changed)=={'R206','J107'},'ONLY2')
for r in changed:
 req(x[r]['side']==y[r]['side']and x[r]['angle']==y[r]['angle'],'NOFLIP')
 dx,dy=[y[r]['xy'][i]-x[r]['xy'][i]for i in [0,1]]
 for old,new in zip(x[r]['pads'],y[r]['pads']):
  req(old[:3]==new[:3]and old[4:]==new[4:]and[old[3][0]+dx,old[3][1]+dy]==new[3],'PURE TRANSLATE')
def track(t):return(t.m_Uuid.AsString(),t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
req(sorted(map(track,a.GetTracks()))==sorted(map(track,b.GetTracks())),'COPPER CHANGED')
# Text outside exactly two moved footprint blocks remains byte identical. Native save may order stable UUIDs.
def stripped(path):
 lines=path.read_text().splitlines(keepends=True);blocks=[];i=0
 while i<len(lines):
  if lines[i].startswith('\t(footprint '):
   j=i+1
   while j<len(lines)and lines[j]!='\t)\n':j+=1
   block=''.join(lines[i:j+1]);
   if any(f'"Reference" "{r}"'in block for r in ['R206','J107']):blocks.append('<MOVED FOOTPRINT>\n')
   else:blocks.append(block)
   i=j+1
  else:blocks.append(lines[i]);i+=1
 return ''.join(blocks)
req(stripped(S)==stripped(N),'NONFOOTPRINT BYTES')
print(json.dumps({'status':'TWO_PURE_TRANSLATIONS_ONLY','changed_refs':changed,'all_76_copper_objects_uuid_and_geometry_identical':True,'all_remaining_native_text_identical':True,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(N.read_bytes()).hexdigest()},indent=2))
