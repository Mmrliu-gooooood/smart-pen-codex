from pathlib import Path
import os,json,sys,re,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/imu-rollback-audit0405';D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
import pcbnew as p
source=R/'hardware/pressure_pullup_revision_0318/native/mainboard_revD.kicad_pcb';rollback=D/'native_negative/rollback/mainboard_revD.kicad_pcb';a=source.read_text();b=rollback.read_text()
def req(c,m):
 if not c:raise RuntimeError(m)
def r503(s):return next((i,j,v)for i,j,v in children(s)if v.startswith('(footprint ')and '(property "Reference" "R503"'in v)
def stripmpn(v):
 i,j,s=next((i,j,s)for i,j,s in children(v)if s.startswith('(property "MPN"'));return v[:i]+v[j:],s
def tok(s):return re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s)
ai,aj,av=r503(a);bi,bj,bv=r503(b);ar,am=stripmpn(av);br,bm=stripmpn(bv);req(tok(ar)==tok(br),'R503 nonMPN tokens');req(tok(am)==tok(bm),'MPN tokens');restored=b[:bi]+av+b[bj:];req(restored==a,'explicit R503 formatting restoration fullbyte')
out=D/'rollback_format_restored';out.mkdir(exist_ok=True);(out/source.name).write_text(restored)
normalized=D/'source_serialization_normalized';normalized.mkdir(exist_ok=True);board=p.LoadBoard(str(source));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(normalized/source.name),board);req((normalized/source.name).read_bytes()==rollback.read_bytes(),'normalized source equals raw rollback')
checks=[]
for f in [source,rollback,D/'native'/source.name]:
 bd=p.LoadBoard(str(f));fp=next(x for x in bd.GetFootprints()if x.GetReference()=='R503');req(fp.GetValue()=='47k 1%','value');req(fp.GetFieldByName('MPN').GetText()=='RC0603FR-0747KL','MPN');checks.append({'file':str(f.relative_to(R)),'value':fp.GetValue(),'MPN':fp.GetFieldByName('MPN').GetText(),'pose':[fp.GetPosition().x/1e6,fp.GetPosition().y/1e6,fp.GetOrientationDegrees()],'pads':[(x.GetNumber(),x.GetNetname())for x in fp.Pads()]})
req(all(x['pose']==checks[0]['pose']and x['pads']==checks[0]['pads']for x in checks),'R503 geometry nets unchanged')
print(json.dumps({'raw_freshfill_rollback_parent_byte_equal':a==b,'difference':'Only R503 MPN property ordering/pretty-print; no changed token content','normalized_source_matches_raw_rollback':True,'explicit_original_R503_field_block_format_restoration_byte_equal':True,'restored_sha256':hashlib.sha256(restored.encode()).hexdigest(),'independent_R503_checks':checks},indent=2))
