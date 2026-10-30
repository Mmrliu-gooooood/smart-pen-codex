from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p
D=Path(__file__).resolve().parent
def rules(b):
 return {z.m_Uuid.AsString():{'name':z.GetZoneName(),'layers':list(z.GetLayerSet().Seq()),'outline':str(z.Outline().Format()),'no_vias':z.GetDoNotAllowVias(),'no_copper':z.GetDoNotAllowCopperPour(),'no_tracks':z.GetDoNotAllowTracks(),'no_pads':z.GetDoNotAllowPads(),'no_footprints':z.GetDoNotAllowFootprints()} for z in b.Zones() if z.GetIsRuleArea()}
a=rules(p.LoadBoard(str(D.parent/'gate_input_local_routing/mainboard_revD.kicad_pcb')));b=rules(p.LoadBoard(str(D/'native_snapshot/mainboard_revD.kicad_pcb')))
if a!=b:raise RuntimeError('Rule-area geometry or flags changed')
print(json.dumps({'all_rule_areas_unchanged':True,'rules':b},indent=2))
