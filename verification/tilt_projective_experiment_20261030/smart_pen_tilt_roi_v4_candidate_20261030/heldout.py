"""Independent pull-rasterized physical plane fixtures and projective result oracle.
No truth enters the C decoder. Pixel coordinates use integer pixel centres.
200x200 is a raw contiguous sensor sample crop, NOT a rescaled VGA frame.
"""
from pathlib import Path
import hashlib, json, math
import numpy as np
P=Path(__file__).resolve().parent
DIRECTIONS_PATH=P.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy'

def rotation(axis,angle):
    c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    if axis=='z': return np.array([[c,-s,0],[s,c,0],[0,0,1]],float)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]],float)

def homography(s):
    """P=.3mm, distance Z=12mm by default; fpx=pitch*Z/P.
    Tilt about an in-plane axis with azimuth phi, then optical-axis roll.
    Tilt is optical-axis-from-normal, NOT the user's pen-axis angle.
    """
    pitch=s.get('pitch',10.);z=s.get('z_mm',12.);phi=s.get('azimuth',0.)
    r=rotation('z',s.get('roll',0))@rotation('z',phi)@rotation('x',s.get('tilt',0))@rotation('z',-phi)
    cx,cy=s['center'];principal=np.array([99.5,99.5]);den=.3/z*r[2,:2]
    h=np.eye(3);h[:2,:2]=pitch*r[:2,:2]+principal[:,None]*den
    h[:2,2]=principal;h[2,:2]=den
    shift=np.array([[1,0,-cx],[0,1,-cy],[0,0,1]],float)
    return h@shift

def project(h,xy):
    a=np.asarray(xy,float);p=np.concatenate((a,np.ones(a.shape[:-1]+(1,))),axis=-1)@np.asarray(h,float).T
    return p[...,:2]/p[...,2,None]

def omitted(x,y,s):
    if s.get('kind')=='missing_rows':return (y % 6)==s.get('missing_phase',2)
    if s.get('kind')=='missing_checker':return ((x+y) % 5)==0
    return np.zeros(np.broadcast_shapes(np.shape(x),np.shape(y)),bool)

def render(s,dirs=None):
    """Inverse homography per subpixel; no forward dot bounding boxes.
    The dot remains inside its nearest-cell Voronoi square (offset+radius=1/3).
    All supersamples are in original raw-crop pixels; no image resizing.
    """
    if dirs is None:dirs=np.load(DIRECTIONS_PATH)
    h=homography(s);inv=np.linalg.inv(h);yy,xx=np.mgrid[:200,:200];cov=np.zeros((200,200),int)
    if s.get('kind')=='random_codes':dirs=np.random.default_rng(s['seed']).integers(0,4,dirs.shape,dtype=np.uint8)
    for sy in range(4):
        for sx in range(4):
            xy=np.stack((xx+(sx+.5)/4-.5,yy+(sy+.5)/4-.5),axis=-1)
            q=project(inv,xy);ix=np.rint(q[...,0]).astype(int);iy=np.rint(q[...,1]).astype(int)
            assert np.all((ix>=0)&(ix<dirs.shape[1])&(iy>=0)&(iy<dirs.shape[0]))
            d=dirs[iy,ix];dx=np.choose(d,[0,-1,1,0])/6;dy=np.choose(d,[-1,0,0,1])/6
            cov+=((q[...,0]-ix-dx)**2+(q[...,1]-iy-dy)**2<=1/36)&~omitted(ix,iy,s)
    im=np.rint(240-210*cov/16).astype(np.uint8)
    sigma=s.get('blur',0)
    if sigma:
        rad=math.ceil(3*sigma);k=np.exp(-np.arange(-rad,rad+1)**2/(2*sigma*sigma));k/=k.sum();buf=im.astype(float)
        for axis in (0,1):buf=np.apply_along_axis(lambda a:np.convolve(np.pad(a,rad,mode='edge'),k,mode='valid'),axis,buf)
        im=np.rint(buf).astype(np.uint8)
    if s.get('noise',0):
        noise=np.random.default_rng(s['seed']).integers(-s['noise'],s['noise']+1,im.shape)
        im=np.clip(im.astype(np.int16)+noise,0,255).astype(np.uint8)
    kind=s.get('kind','positive')
    if kind=='mirror':im=np.ascontiguousarray(im[:,::-1])
    if kind=='quarter_turn':im=np.ascontiguousarray(np.rot90(im))
    if kind=='thin_stroke':im[98:100,40:160]=30
    if kind=='diagonal_stroke':
        for i in range(45,155):im[i,i-1:i+2]=30
    if kind=='clutter':
        rng=np.random.default_rng(s['seed'])
        for x,y in rng.integers(55,145,(80,2)):im[y,x:x+4]=30
    if kind=='blank':im[:]=240
    if kind=='random_pixels':im=np.random.default_rng(s['seed']).integers(0,256,im.shape,dtype=np.uint8)
    return im,h

def cases():
    rows=[]
    # Independent phases, not original audit phase0/17. All safely within paper.
    centers=[(321.193,552.827),(413.673,631.219)]
    for tilt in (15,25,35,45,55,60):
        for roll in (-30,-15,15,30):
            for phase,center in enumerate(centers):
                rows.append(dict(group='heldout_pose',tilt=tilt,roll=roll,azimuth=23 if phase else 0,center=center,pitch=10.))
    # fpx varies with pitch at same Z: pitch32 means hypothetical full640=6mm.
    # Its raw200=1.875mm and fixed96=.9mm cannot support full six-dot rows.
    for pitch in (8.,12.,16.,32.):
        for tilt in (0,30,60):
            for roll in (-15,15):
                rows.append(dict(group='sampling_density',tilt=tilt,roll=roll,azimuth=0,center=centers[0],pitch=pitch))
    for tilt in (25,45,60):
        for noise in (4,12,24):
            for blur in (0.,.5):
                rows.append(dict(group='noise_blur',tilt=tilt,roll=15,azimuth=23,center=centers[1],pitch=10.,noise=noise,blur=blur))
    for tilt in (0,30,60):
        for kind in ('mirror','quarter_turn','thin_stroke','diagonal_stroke','clutter','missing_rows','missing_checker','random_codes','blank','random_pixels'):
            rows.append(dict(group='negative',tilt=tilt,roll=0,azimuth=0,center=centers[0],pitch=10.,kind=kind,must_reject=True))
    for i,s in enumerate(rows):s.update(id=f'heldout_{i:03d}',seed=91091+i,z_mm=12.,focal_pixels=s['pitch']*12/.3)
    return rows

def oracle(s, result, dirs=None):
    """result normalized dict: x,y,directions,H (9 values), roi=[l,t,w,h].
    Checks canonical orientation, exact symbols, window support and geometry.
    """
    if dirs is None:dirs=np.load(DIRECTIONS_PATH)
    x,y=int(result['x']),int(result['y']);a=np.asarray(result['H'],float).reshape(3,3);h=homography(s)
    in_bounds=0<=x<=dirs.shape[1]-6 and 0<=y<=dirs.shape[0]-6
    if not in_bounds:return dict(correct=False,reason='decoded origin outside paper')
    exact=list(map(int,result['directions']))==dirs[y:y+6,x:x+6].reshape(-1).tolist()
    pts=np.array([(xx,yy) for yy in range(y,y+6) for xx in range(x,x+6)],float)
    pred=project(a,pts);expected=project(h,pts);err=np.linalg.norm(pred-expected,axis=1)
    l,t,w,hh=result['roi'];support=True
    for xx,yy in pts.astype(int):
        d=dirs[yy,xx];dx,dy=((0,-1),(-1,0),(1,0),(0,1))[d]
        # Conservatively verify four corners of enclosing ink square, not center only.
        corners=project(h,[[xx+dx/6+rx,yy+dy/6+ry] for rx in (-1/6,1/6) for ry in (-1/6,1/6)])
        support &= bool(np.all((corners[:,0]>=l-.5)&(corners[:,0]<l+w-.5)&(corners[:,1]>=t-.5)&(corners[:,1]<t+hh-.5)) and not omitted(xx,yy,s))
    # Compare basis direction at every cell, not just determinant/one origin.
    orientations=[]
    for delta in ([.01,0],[0,.01]):
        va=project(a,pts+delta)-pred;vb=project(h,pts+delta)-expected
        orientations.extend((np.sum(va*vb,axis=1)/(np.linalg.norm(va,axis=1)*np.linalg.norm(vb,axis=1))).tolist())
    orientation=bool(np.all(np.isfinite(orientations)) and min(orientations)>math.cos(math.radians(5)))
    finite=bool(np.all(np.isfinite(a)) and np.all(np.isfinite(pred)))
    ok=finite and exact and support and orientation and max(err)<=.1*s['pitch'] and not s.get('must_reject',False)
    return dict(correct=bool(ok),exact_symbols=bool(exact),window_supported=bool(support),orientation_correct=orientation,max_grid_error_px=float(max(err)),min_basis_cosine=float(min(orientations)))

if __name__=='__main__':
    out=[]
    for s in cases():
        im,h=render(s);out.append(dict(**s,image_sha256=hashlib.sha256(im.tobytes()).hexdigest(),H=h.reshape(-1).tolist()))
    (P/'heldout_manifest.json').write_text(json.dumps(dict(renderer='independent inverse planar pinhole rasterization',directions_sha256=hashlib.sha256(DIRECTIONS_PATH.read_bytes()).hexdigest(),synthetic_only=True,raw_pixel_crop=True,cases=out),indent=2)+'\n')
    print(f'{len(out)} independent heldout cases generated and hashed')
