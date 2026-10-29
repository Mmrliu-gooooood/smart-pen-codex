from pathlib import Path
s=Path(__file__).with_name('grid_core.py').read_text().split('pads={}')[0].replace('TRACK_HALF=.127/2','TRACK_HALF=.15/2').replace("if net not in FINE:raise RuntimeError('unapproved signal net')","if net not in FINE and net!='GND':raise RuntimeError('unapproved net')").replace('p.FromMM(.127)','p.FromMM(.15)').replace('return .127 if other in FINE else .15','return .15')
exec(compile(s,__file__,'exec'))
net='GND';obs,vb=masks(net)
start=(2.85,45.0);goals=[]
for ix,iy in zip(*np.where(~vb & ~obs[1])):
 q=(ix*STEP,iy*STEP);distance=math.dist(q,start)
 if distance<2:goals.append((distance,q))
path=None
for distance,end in sorted(goals):
 no_vias=vb.copy();no_vias[:]=True
 path,why=search(start,end,obs,no_vias,1,1)
 if path is not None:break
if path is None:raise RuntimeError('no local legal ground via path')
before={t.m_Uuid.AsString() for t in b.GetTracks()};add(net,path,start,end,1,1);via=p.PCB_VIA(b);via.SetPosition(pt(end));via.SetWidth(p.F_Cu,p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(b.FindNet('GND'));b.Add(via);expected={t.m_Uuid.AsString():'GND' for t in b.GetTracks() if t.m_Uuid.AsString() not in before}
if not expected:raise RuntimeError('no new ground copper')
output=D/(outname+'.kicad_pcb');p.SaveBoard(str(output),b);b=p.LoadBoard(str(output));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(output),b)
for ext in ['.kicad_pro','.kicad_dru']:(D/(outname+ext)).write_bytes((D/(source+ext)).read_bytes())
(D/(outname+'_expected_new.json')).write_text(json.dumps(expected,indent=2))
print(why,expected)
