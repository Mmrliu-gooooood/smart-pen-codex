from pathlib import Path
import sys,json,re,shutil,hashlib,pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());S=D/'parent';C=D/'candidate';I=D/'inverse'
if I.exists():raise RuntimeError('no inverse overwrite')
shutil.copytree(S,I);a=(S/'mainboard_revD.kicad_pcb').read_text();raw=(C/'mainboard_revD.kicad_pcb').read_text();added={x['uuid']for x in c['objects']};oldfp=next(v for _,_,v in blocks(a)if v.startswith('(footprint')and '(property "Reference" "J107"'in v);oldtracks=[v for _,_,v in blocks(a)if v.startswith(('(segment','(via'))and re.search(r'\(uuid "([^"]+)"\)',v).group(1)in c['removed']]
for x,z,v in reversed(blocks(raw)):
 if v.startswith(('(segment','(via'))and re.search(r'\(uuid "([^"]+)"\)',v).group(1)in added:raw=raw[:x]+raw[z:]
 elif v.startswith('(footprint')and '(property "Reference" "J107"'in v:raw=raw[:x]+oldfp+raw[z:]
pos=raw.rfind(')');raw=raw[:pos]+'\n'+'\n'.join(oldtracks)+'\n'+raw[pos:];P=I/'mainboard_revD.kicad_pcb';P.write_text(raw);b=p.LoadBoard(str(P));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b);actual=hashlib.sha256(P.read_bytes()).hexdigest();out={'inverse_sha256':actual,'parent_sha256':c['parent_sha256'],'exact_parent_reproduced':actual==c['parent_sha256'],'removed_new_objects':len(added),'restored_old_objects':len(oldtracks),'restored_J107_parent_footprint_and_project_dependencies':True};(D/'inverse.json').write_text(json.dumps(out,indent=2));print(out)
if not out['exact_parent_reproduced']:raise RuntimeError('inverse not exact')
