"""Self-test the independent oracle and crosscheck rasterizers only after freezing."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import heldout
P=Path(__file__).resolve().parent

def main():
    dirs=np.load(heldout.DIRECTIONS_PATH);spec=heldout.cases()[0];x,y=318,550
    result=dict(x=x,y=y,directions=dirs[y:y+6,x:x+6].reshape(-1).tolist(),H=heldout.homography(spec),roi=[0,0,200,200])
    ideal=heldout.oracle(spec,result,dirs);assert ideal['correct'];result['H']=np.asarray(result['H']).copy();result['H'][0,:]*=-1
    bad=heldout.oracle(spec,result,dirs);assert not bad['correct'] and not bad['orientation_correct']
    (P/'heldout_oracle_selftest.json').write_text(json.dumps(dict(ideal=ideal,bad_homography=bad),indent=2)+'\n')
    sys.path[:0]=[str(P/'source/tools'),str(P/'source/tests')]
    import continuous_roi_sweep as frozen
    checks=[]
    for old in json.loads((P/'baseline_eight.json').read_text()):
        spec=dict(pitch=10.,center=(old['ox']+10,old['oy']+10),tilt=old['camera_tilt_deg'],roll=0,azimuth=0)
        independent,_=heldout.render(spec,dirs);reference=frozen.render(dirs,old)
        central=int(np.count_nonzero(independent[52:148,52:148]!=reference[52:148,52:148]));assert central==0
        checks.append(dict(tilt=old['camera_tilt_deg'],phase=old['phase'],central96_different_pixels=central,full200_different_pixels=int(np.count_nonzero(independent!=reference))))
    (P/'renderer_crosscheck.json').write_text(json.dumps(checks,indent=2)+'\n')
    print('PASS oracle selftest; eight central96 renders pixel-identical')
if __name__=='__main__':main()
