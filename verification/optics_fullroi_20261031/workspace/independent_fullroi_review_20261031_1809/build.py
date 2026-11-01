from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'publication_20261031/target_repo'
V3=ROOT/'verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029'
def build(out,enabled,sanitize=False,seed_cap=64):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 flags=['-std=c11','-O1' if sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-pedantic','-fPIC']
 if sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 units=[(ROOT/'firmware/vision/roi_opt.c',['-Dpen_roi_decode_opt=pen_roi_active_decode_opt']), (V3/'firmware/vision/roi_opt.c',['-Dpen_roi_decode_opt=pen_roi_v3_decode_opt',f'-DPEN_ROI_REFINE_MAX_SEEDS={seed_cap}']), (ROOT/'firmware/codec/anoto.c',[]),(HERE/'candidate.c',[f'-DCANDIDATE_ENABLE_REFINEMENT={int(enabled)}',f'-DPEN_ROI_REFINE_MAX_SEEDS={seed_cap}','-I'+str(V3/'firmware/vision')])]
 objs=[]
 for i,(src,extra) in enumerate(units):
  obj=out/f'{i}.o';subprocess.run(['cc',*flags,*extra,'-I'+str(HERE),'-c',str(src),'-o',str(obj)],check=True);objs.append(obj)
 so=out/'candidate.so';subprocess.run(['cc','-shared',*flags,*map(str,objs),'-lm','-o',str(so)],check=True);return so
