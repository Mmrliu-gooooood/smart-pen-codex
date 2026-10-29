from pathlib import Path
import pcbnew as p,json,hashlib,sys,shutil
D=Path(__file__).resolve().parent
src=D/'mainboard_revD.kicad_pcb'
b=p.LoadBoard(str(src));b.BuildConnectivity(); con=b.GetConnectivity()
f=next(f for f in b.GetFootprints() if f.GetReference()=='R220');pad=next(a for a in f.Pads() if a.GetNumber()=='1');q=[pad];seen=set();remove=[]
while q:
 a=q.pop();uid=a.m_Uuid.AsString()
 if uid in seen:continue
 seen.add(uid);q.extend(con.GetConnectedTracks(a));q.extend(con.GetConnectedPads(a))
 if a.GetClass()=='PAD':
  if a.m_Uuid!=pad.m_Uuid:raise RuntimeError('not isolated bias branch')
 else:remove.append(a)
removed=[a.m_Uuid.AsString() for a in remove]
for a in remove:b.Delete(a)
x,y,dx,dy=map(float,sys.argv[1:5]);name=sys.argv[5]
if len(sys.argv)<7 or sys.argv[6]!='F':f.Flip(f.GetPosition(),False)
for angle in [0,90,180,270]:
 f.SetOrientationDegrees(angle);pads={a.GetNumber():a for a in f.Pads()};v=pads['2'].GetPosition()-pads['1'].GetPosition()
 if abs(p.ToMM(v.x)-dx)<.001 and abs(p.ToMM(v.y)-dy)<.001:break
else:raise RuntimeError('orientation not found')
f.Move(p.VECTOR2I(p.FromMM(x)-pads['1'].GetPosition().x,p.FromMM(y)-pads['1'].GetPosition().y))
output=D/(name+'.kicad_pcb');p.SaveBoard(str(output),b);b=p.LoadBoard(str(output));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(output),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(D/('mainboard_revD'+ext),D/(name+ext))
(D/(name+'_delta.json')).write_text(json.dumps({'removed_isolated_CAM_HREF':removed,'R220_pad1':[x,y],'R220_pad2':[x+dx,y+dy],'orientation':angle},indent=2))