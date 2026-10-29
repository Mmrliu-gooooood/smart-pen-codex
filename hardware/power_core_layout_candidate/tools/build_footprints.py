#!/usr/bin/python3
"""Exact copper from official dimensional drawings; own courtyard/mask choices declared."""
from pathlib import Path
import pcbnew as p,json,hashlib
D=Path(__file__).resolve().parents[1];lib=D/'SmartPenPower.pretty';lib.mkdir(exist_ok=True);manifest={}
mm=lambda x:p.FromMM(x)
v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
def shape(fp,a,b,layer):
 q=p.PCB_SHAPE();q.SetShape(p.SHAPE_T_RECT);q.SetStart(v(*a));q.SetEnd(v(*b));q.SetWidth(mm(.05 if layer==p.F_CrtYd else .1));q.SetLayer(layer);fp.Add(q)
def make(name,body,pads,source):
 fp=p.FOOTPRINT(None);fp.SetFPID(p.LIB_ID('SmartPenPower',name));fp.SetAttributes(p.FP_SMD);fp.SetReference('REF**');fp.SetValue(name)
 fp.Reference().SetPosition(v(0,-body[1]/2-.8));fp.Reference().SetTextSize(v(.7,.7));fp.Reference().SetTextThickness(mm(.1));fp.Value().SetVisible(False)
 shape(fp,(-body[0]/2,-body[1]/2),(body[0]/2,body[1]/2),p.F_Fab)
 shape(fp,(-body[0]/2-.25,-body[1]/2-.25),(body[0]/2+.25,body[1]/2+.25),p.F_CrtYd)
 for num,x,y,w,h,paste in pads:
  a=p.PAD(fp);a.SetNumber(str(num));a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_RECT if name.startswith('Coilcraft') else p.PAD_SHAPE_ROUNDRECT);a.SetPosition(v(x,y));a.SetSize(v(w,h));a.SetRoundRectRadiusRatio(min(.05/min(w,h),.25));layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.F_Mask)
  if paste:layers.AddLayer(p.F_Paste)
  a.SetLayerSet(layers);a.SetLocalSolderMaskMargin(mm(.04));fp.Add(a)
 p.PCB_IO_MGR.PluginFind(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(lib),fp)
 f=lib/(name+'.kicad_mod');rb=p.FootprintLoad(str(lib),name);actual=[{'pin':a.GetNumber(),'x':p.ToMM(a.GetPosition().x),'y':p.ToMM(a.GetPosition().y),'w':p.ToMM(a.GetSize().x),'h':p.ToMM(a.GetSize().y),'paste':a.IsOnLayer(p.F_Paste)} for a in rb.Pads()]
 for a,b in zip(sorted(actual,key=lambda a:int(a['pin'])),sorted(pads,key=lambda a:a[0])):assert (a['pin'],a['x'],a['y'],a['w'],a['h'],a['paste'])==(str(b[0]),b[1],b[2],b[3],b[4],b[5]),(a,b)
 manifest[name]={'source':source,'actual_readback':actual,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'status':'Copper dimensions verified; mask .04/courtyard are engineering choices, stencil/assembly not released'}
# RGT0016B top-view pin1 upper-left, anti-clockwise; center electrical17.
r=[]
for i in range(4):r += [(i+1,-1.4,round(-.75+i*.5,3),.6,.25,True),(i+5,round(-.75+i*.5,3),1.4,.25,.6,True),(i+9,1.4,round(.75-i*.5,3),.6,.25,True),(i+13,round(.75-i*.5,3),-1.4,.25,.6,True)]
r.append((17,0,0,1.6,1.6,False))
make('TI_RGT0016B_Official_NOFAB',(3.1,3.1),r,'TI drawing4219033/A08/2016 RGT0016B, official CDCLVP1102 appendix; BQ24074 pinout explicitlyRGT0016B. EP paste omitted pending stencil. Actual order/package lot needs confirmation.')
r=[(i+1,-.9,round(-1+i*.5,3),.6,.25,True) for i in range(5)]
r += [(n,.55 if n==8 else .75,round(1-(n-6)*.5,3),1.3 if n==8 else .9,.25,True) for n in range(6,11)]
make('TI_DLA0010A_Official_NOFAB',(2.1,3.1),r,'TPS63802 DS DLA0010A drawing4223750/D03/2019: asymmetrical pad8, no exposed17/11 invented')
make('Coilcraft_XFL4015_Official_NOFAB',(4.3,4.3),[(1,-1.185,0,.98,3.4,True),(2,1.185,0,.98,3.4,True)],'Coilcraft XFL4015 document769-2 rev03/10/26: padwidth.98,length3.4,pitch2.37; markingstart terminal is1, route orientation remains EMI review')
for n in [2,4]:
 make(f'WireLands_{n}_P2.5_AssemblyUnqualified',(n*2.5,3),[(i+1,round((i-(n-1)/2)*2.5,3),0,1.5,2,False) for i in range(n)],'Own solder lands, not connector MPN; strain relief/wire gauge/ampacity not qualified')
(D/'footprint_checks.json').write_text(json.dumps(manifest,indent=2));(D/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "SmartPenPower")(type "KiCad")(uri "${KIPRJMOD}/SmartPenPower.pretty")(options "")(descr "NOFAB official-derived copper + unqualified wire lands")))')
print('PASS official copper readback plus explicit assembly gates',len(manifest))
