def blocks(s):
 depth=0;quoted=False;escape=False;start=None;out=[]
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True;continue
  if c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:out.append((start,i+1,s[start:i+1]))
   depth-=1
 return out
