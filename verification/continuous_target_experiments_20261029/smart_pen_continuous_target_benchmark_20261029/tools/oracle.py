"""Post-decode output oracle; never supplies coordinates/transforms to C."""
import math

def integer(x,low=0,high=None):
 if type(x) is not int or x<low or (high is not None and x>high): raise ValueError('Invalid bounded integer')
 return x

def finite(x):
 if type(x) not in (int,float) or not math.isfinite(x): raise ValueError('Invalid finite number')
 return x

def validate(r,f):
 status=r['status'];integer(status,-5,0)
 if type(r['failure_output_preserved']) is not bool: raise ValueError('Invalid failure contract flag')
 expected=f['legacy_expected_status'] if r['decoder']=='frozen_opt' else f['expected_status']
 errors=[]
 if not r['failure_output_preserved']: errors.append('failure_output_changed')
 if status!=expected: errors.append('unexpected_status')
 if status:
  if any(k in r for k in ['x','y','crop','paper_to_frame','frame_to_paper','directions']): raise ValueError('Stale geometry on failure')
  return ('expected_nofit' if status==expected and not errors else 'unexpected_reject'),errors
 # Frozen core success is unexpected for this full-frame fixture set.
 if r['decoder']=='frozen_opt': return 'unexpected_success',['unexpected_legacy_success']
 x=integer(r['x'],0,709);y=integer(r['y'],0,999)
 if [x,y]!=[f.get('x'),f.get('y')]: errors.append('coordinate')
 dirs=r['directions']
 if type(dirs) is not list or len(dirs)!=36: raise ValueError('Invalid direction array')
 for d in dirs: integer(d,0,3)
 if dirs!=f.get('directions'): errors.append('directions')
 crop=r['crop']
 if type(crop) is not list or len(crop)!=4: raise ValueError('Invalid crop')
 for v in crop: integer(v,0,200)
 if crop!=f.get('crop'): errors.append('crop')
 for key,ref in [('crop_attempts','attempts'),('edge_components','edge_components'),('edge_pixels','edge_pixels'),('dots','dots'),('windows','windows')]:
  integer(r[key]);
  if r[key]!=f.get(ref): errors.append(key)
 integer(r['used_warm'],0,1)
 if r['used_warm']!=0: errors.append('warm_forbidden')
 integer(r['candidates'],1,26901)
 for key in ['paper_to_frame','frame_to_paper']:
  arr=r[key]
  if type(arr) is not list or len(arr)!=6: raise ValueError('Invalid transform shape')
  for v in arr: finite(v)
  if expected==0 and any(abs(a-b)>f['transform_numeric_tolerance'] for a,b in zip(arr,f[key])): errors.append(key)
 a,b=r['paper_to_frame'],r['frame_to_paper']
 for xx,yy in [(0,0),(x,y),(709,999)]:
  u=a[0]*xx+a[1]*yy+a[2];v=a[3]*xx+a[4]*yy+a[5]
  if max(abs(b[0]*u+b[1]*v+b[2]-xx),abs(b[3]*u+b[4]*v+b[5]-yy))>1e-7: errors.append('transform_inverse');break
 return ('correct_output' if not errors else 'unexpected_success'),errors
