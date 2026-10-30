from pathlib import Path
import shutil,hashlib,json,os
os.environ['XDG_CONFIG_HOME']='/tmp/rebuild-kicad/config';os.environ['XDG_CACHE_HOME']='/tmp/rebuild-kicad/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';src=B/'native/mainboard_revD.kicad_pcb'
if hashlib.sha256(src.read_bytes()).hexdigest()!='8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5':raise RuntimeError('Wrong baseline')
if (D/'manifest.json').exists():raise RuntimeError('Frozen output must not be rebuilt in place')
shutil.copytree(B/'native',D/'native',dirs_exist_ok=True)
b=p.LoadBoard(str(src));rules=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='LIS2DW12_BODY_ALL6_NO_PLANES_OR_VIAS']
if len(rules)!=1:raise RuntimeError('Old rule missing/duplicate')
z=rules[0];ls=p.LSET();ls.AddLayer(p.F_Cu);z.SetLayerSet(ls);z.SetZoneName('LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA');z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowTracks(False)
# Explicit central-space rule, not a blanket ban on legitimate peripheral pad escape.
central_uuid='c59d76d7-4fe7-4475-8382-e1c75d7f8d6c'
c=p.ZONE(b);c.SetIsRuleArea(True);c.SetLayerSet(ls);c.SetZoneName('LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN');c.SetDoNotAllowTracks(True);c.SetDoNotAllowVias(True);c.SetDoNotAllowCopperPour(True);c.SetDoNotAllowPads(False);c.SetDoNotAllowFootprints(False)
c.Outline().NewOutline()
for x,y in [(3.425,81.4125),(4.575,81.4125),(4.575,82.5875),(3.425,82.5875)]:c.Outline().Append(p.FromMM(x),p.FromMM(y))
b.Add(c);p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'native/mainboard_revD.kicad_pcb'),b)
out=D/'native/mainboard_revD.kicad_pcb';text=out.read_text();token='(uuid \"'+c.m_Uuid.AsString()+'\")'
if text.count(token)!=1:raise RuntimeError('central rule UUID serialization not unique')
out.write_text(text.replace(token,'(uuid \"'+central_uuid+'\")'))
report={'status':'CONDITIONAL_LAYERED_RULE_STUDY_NOFAB','baseline_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'changed_existing_rule_uuid':z.m_Uuid.AsString(),'added_central_rule_uuid':central_uuid,'full_body_mm':[3,81,5,83],'central_screen_mm':[3.425,81.4125,4.575,82.5875],'track_or_pad_changes_intended':False,'same_side_peripheral_ground_links':'manual manufacturer-layout review remains open','inner_plane_policy':'project engineering inference from same-side restriction, not explicit six-layer manufacturer approval'}
(D/'delta.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
