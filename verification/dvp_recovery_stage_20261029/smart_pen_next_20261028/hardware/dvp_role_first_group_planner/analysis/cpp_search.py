import subprocess,struct
CPP_COUNTER=0
def cpp_search(starts,goals,obs,vb,soft=None,softvia=None,penalties=(5.,10.,1.)):
 global CPP_COUNTER
 CPP_COUNTER+=1
 if not starts or not goals:return None,'blocked anchors'
 soft=np.zeros_like(obs)if soft is None else soft;softvia=np.zeros_like(vb)if softvia is None else softvia
 target=np.zeros((NX,NY),bool)
 for k,x,y in goals:target[x,y]=True
 h=ndimage.distance_transform_edt(~target).astype('<f4');enc=lambda a:(a[0]*NX+a[1])*NY+a[2]
 f=D/f'cpp_input_{CPP_COUNTER}.bin';out=D/f'cpp_output_{CPP_COUNTER}.txt'
 with f.open('wb')as z:
  z.write(struct.pack('<5i',N,NX,NY,len(starts),len(goals)));z.write(struct.pack('<3d',*penalties))
  for q in[obs,vb,soft,softvia]:z.write(q.astype('u1').tobytes())
  z.write(h.tobytes());z.write(np.asarray([enc(a)for a in sorted(starts)],dtype='<i4').tobytes());z.write(np.asarray([enc(a)for a in sorted(goals)],dtype='<i4').tobytes())
 r=subprocess.run([str(D/'grid_astar'),str(f),str(out)],capture_output=True,text=True)
 if r.returncode not in[0,5]:raise RuntimeError('CPP_FAILURE '+str(r.returncode)+' '+r.stderr)
 lines=out.read_text().splitlines();head=lines[0].split()
 if head[0]!='1':return None,'bounded/exhausted '+head[1]
 path=[tuple(map(int,s.split()))for s in lines[2:]]
 # Independent step validity using the exact input arrays; do not accept executable output blindly.
 if path[0]not in starts or path[-1]not in goals:raise RuntimeError('BAD_ENDPOINTS')
 for aa,zz in zip(path,path[1:]):
  k,x,y=aa;l,u,v=zz
  if obs[l,u,v]:raise RuntimeError('HARD_OBSTACLE')
  if k!=l:
   if (x,y)!=(u,v)or vb[x,y]:raise RuntimeError('BAD_VIA')
  elif max(abs(x-u),abs(y-v))!=1 or(x!=u and y!=v and(obs[k,u,y]or obs[k,x,v])):raise RuntimeError('BAD_STEP')
 return path,{'pops':int(head[1]),'cost':float(lines[1].split()[0]),'input':f.name,'output':out.name}
