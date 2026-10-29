from pathlib import Path
import shutil,subprocess,os
os.environ.update(XDG_CONFIG_HOME="/tmp/rebuild-kicad/config",XDG_CACHE_HOME="/tmp/rebuild-kicad/cache",XDG_DATA_HOME="/tmp/rebuild-kicad/data")
import pcbnew as p
H=Path(__file__).resolve().parents[2];A=H/'usb_tail_revA';B=H/'usb_tail_revB';B.mkdir(exist_ok=True)
for f in A.iterdir():
 if f.is_file() and f.suffix in ['.kicad_sch','.kicad_sym','.kicad_pro'] or f.name in ['fp-lib-table','sym-lib-table']:shutil.copyfile(f,B/f.name)
shutil.copytree(A/'SmartPen.pretty',B/'SmartPen.pretty',dirs_exist_ok=True)
name='USB4105_GroundHeelTrim80um_AssemblyUnqualified';fp=p.FootprintLoad('/usr/share/kicad/footprints/Connector_USB.pretty','USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal');fp.SetFPID(p.LIB_ID('SmartPen',name))
for pad in fp.Pads():
 if pad.GetNumber() in ['A1','B12','A12','B1']:
  pad.SetSize(p.VECTOR2I(p.FromMM(.6),p.FromMM(1.07)))
  pos=pad.GetPosition();pos.y-=p.FromMM(.04);pad.SetPosition(pos)
p.FootprintSave(str(B/'SmartPen.pretty'),fp)
old='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal';new='SmartPen:'+name
for f in B.glob('*.kicad_sch'):f.write_text(f.read_text().replace(old,new))
b=p.LoadBoard(str(A/'usb_tail_revA.kicad_pcb'));j=next(f for f in b.GetFootprints() if f.GetReference()=='J101');j.SetFPID(p.LIB_ID('SmartPen',name))
for pad in j.Pads():
 if pad.GetNumber() in ['A1','B12','A12','B1']:
  pad.SetSize(p.VECTOR2I(p.FromMM(.6),p.FromMM(1.07)))
  pos=pad.GetPosition();pos.y+=p.FromMM(.04);pad.SetPosition(pos)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(B/'usb_tail_revA.kicad_pcb'),b)
env=dict(os.environ,XDG_CONFIG_HOME='/tmp/rebuild-kicad/config',XDG_CACHE_HOME='/tmp/rebuild-kicad/cache',XDG_DATA_HOME='/tmp/rebuild-kicad/data')
for args in [['sch','export','netlist','--format','kicadxml','-o','usb_tail_revA.xml','usb_tail_revA.kicad_sch'],['sch','erc','-o','erc.rpt','usb_tail_revA.kicad_sch'],['pcb','drc','--schematic-parity','-o','drc.rpt','usb_tail_revA.kicad_pcb']]:subprocess.run(['kicad-cli']+args,cwd=B,env=env,check=True)
