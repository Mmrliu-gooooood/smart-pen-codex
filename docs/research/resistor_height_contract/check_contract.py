from pathlib import Path
import json,hashlib,copy,pcbnew
D=Path(__file__).resolve().parent; ROOT=D.parents[2]
def check(d):
 p=ROOT/d['board_path']
 if hashlib.sha256(p.read_bytes()).hexdigest()!=d['board_sha256']: raise ValueError('source hash')
 b=pcbnew.LoadBoard(str(p)); fs={f.GetReference():f for f in b.GetFootprints()}
 expected={'R104':('10k','RC0603FR-0710KL',10000),'R240':('10k','RC0603FR-0710KL',10000),'R236':('4.7k','RC0603FR-074K7L',4700)}
 expected.update({r:('100k','RC0603FR-07100KL',100000) for r in ['R221','R224','R233','R218','R210','R228']})
 if set(d['scope_refs'])!=set(expected) or len(d['resistors'])!=9: raise ValueError('scope')
 for r in d['resistors']:
  ref=r['ref']; tok,mpn,ohms=expected[ref]; f=fs[ref]
  if not f.GetValue().startswith(tok+' 1%') or r['mpn']!=mpn or r['resistance_ohm']!=ohms: raise ValueError('electrical mapping')
  if r['source_value']!=f.GetValue() or r['source_net_by_pin']!={p.GetNumber():p.GetNetname() for p in f.Pads()}: raise ValueError('source identity')
  if r['conditional_height_above_copper_mm']!=.70 or r['body_height_max_mm']!=.55 or r['assumed_solder_assembly_allowance_mm']!=.15: raise ValueError('height')
  if r['electrical_5V5_resistor_only_screen_W']>=.1: raise ValueError('power')
 return True
d=json.loads((D/'contract.json').read_text());check(d)
for case in ['capacitor','wrong_mpn','low_height','wrong_source']:
 x=copy.deepcopy(d)
 if case=='capacitor':x['scope_refs'].append('C103')
 elif case=='wrong_mpn':x['resistors'][-1]['mpn']='RC0603FR-0710KL'
 elif case=='low_height':x['resistors'][0]['conditional_height_above_copper_mm']=.55
 else:x['board_sha256']='0'*64
 try: check(x)
 except (ValueError,KeyError):pass
 else:raise RuntimeError('negative accepted '+case)
print('PASS: 9 exact refs, native source identity, 4 negative tests; NOFAB')
