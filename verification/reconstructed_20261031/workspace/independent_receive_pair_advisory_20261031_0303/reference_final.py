from pathlib import Path
import os,sys
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_polygon import native_fractured_once
uid=lambda t:t.m_Uuid.AsString()
a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'selected_candidate/mainboard_revD.kicad_pcb'));aa={uid(t):t for t in a.GetTracks()};bb={uid(t):t for t in b.GetTracks()}
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault((z.GetLayer(),z.GetNetname()),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b)
def shape(t):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,t.GetLayer(),0,50,p.ERROR_OUTSIDE);return q
