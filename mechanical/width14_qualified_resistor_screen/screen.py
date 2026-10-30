"""Additive conditional screen; requires explicit approved-ref contract, never changes CAD."""
import json, math, hashlib, sys
from pathlib import Path
R=Path(__file__).resolve().parent
D=json.loads((R.parent/'width14_gate/input.json').read_text())
def require(ok, why):
 if not ok: raise RuntimeError(why)
def evaluate(y, parts):
 # B face fixed datum; .93 upper finished thickness goes entirely toward F.
 py=y-5.9
 terms=[(math.hypot(7,py),'power'),(math.hypot(7,py+4.15),'power')]
 terms += [(math.hypot(7,v),'outline') for v in (y,y+.93)]
 for p in parts:
  if p['dnp']: continue
  a,b,c,d=p['bounds']; h=p['height_total']
  ys=(y-h,y) if p['side']=='B' else (y+.93,y+.93+h)
  terms += [(math.hypot(x-7,v),p['ref']) for x in (a,c) for v in ys]
 rad,lim=max(terms)
 return dict(main_B_y=y,main_F_y=y+.93,power_bottom_y=py,radius=rad,limiting=lim,radial_remainder=8-rad,screen_surplus=7.9-rad,passes=rad<=7.9+1e-10,interboard_remainder_at_least=.1)
def optimum(parts):
 lo,hi=-1.,4.
 for _ in range(100):
  a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
  if evaluate(a,parts)['radius']<evaluate(b,parts)['radius']:hi=b
  else:lo=a
 return evaluate((lo+hi)/2,parts)
def make_parts(contract,jx,moves):
 require(contract['board_sha256']==D['sha256'],'Contract board mismatch')
 approved={c['ref']:c for c in contract['resistors']}; out=[]
 require(set(approved)==set(contract['scope_refs']),'Scope mismatch')
 for p0 in D['parts']:
  p=dict(p0);p['bounds']=p0['bounds'].copy();ref=p['ref']
  if ref in approved:
   c=approved[ref]
   require(ref.startswith('R') and c['functional_qualification'],'Unspecified resistor function')
   require(c['body_height_max_mm']==.55 and c['assumed_solder_assembly_allowance_mm']==.15,'Unexpected height contract')
   require(c['mpn'] and c['datasheet_url'],'Missing MPN/evidence')
   p['height_total']=.70;p['height_basis']='Explicit candidate contract: .55 body + .15 solder'
  if ref in moves:
   p['bounds'][0]+=moves[ref];p['bounds'][2]+=moves[ref]
  if ref=='J109':p['bounds']=[jx-.9,18.1,jx+.9,25.1];require(p['height_total']==2.,'Wire height changed')
  out.append(p)
 return out
if __name__=='__main__':
 require(len(sys.argv)==2,'Usage: screen.py explicit_ref_contract.json')
 cpath=Path(sys.argv[1]);contract=json.loads(cpath.read_text())
 require(hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['sha256'],'Native source changed')
 rows=[]
 for jx in [13.,12.5,12.25,12.0]:
  parts=make_parts(contract,jx,{})
  rows.append(dict(J109_x=jx,moves={},optimized=optimum(parts)))
 y=5.9-math.sqrt(7.9**2-7**2)
 need={}
 for p in make_parts(contract,12,{}):
  if p['dnp']:continue
  a,b,cc,d=p['bounds'];h=p['height_total']
  top=y+.93+h if p['side']=='F' else max(abs(y),abs(y-h))
  lim=math.sqrt(7.9**2-top**2)
  if a-7 < -lim:need[p['ref']]=7-lim-a
 refined=[]
 for shift in [.075,.1,.15,.2]:
  moves={ref:shift for ref in need}
  refined.append(dict(moves=moves,J109_x=12,optimized=optimum(make_parts(contract,12,moves))))
 print(json.dumps(dict(status='Conditional geometry only; NOFAB',source_sha256=D['sha256'],contract_sha256=hashlib.sha256(cpath.read_bytes()).hexdigest(),rows=rows,minimum_Bdatum_for_power_screen=y,necessary_left_translations_at_minimum_Bdatum=need,refined_rows=refined),indent=2))
