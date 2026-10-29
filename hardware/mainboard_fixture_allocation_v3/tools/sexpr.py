import re,json
TOK=re.compile(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]')
def parse(s):
 stack=[];root=None
 for t in TOK.findall(s):
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:root=n
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(t)
 return root
def dump(n):return '('+' '.join(dump(x) if isinstance(x,list) else x for x in n)+')'
def tag(n):return n[0] if isinstance(n,list) and n else None
def child(n,k):return next((x for x in n if tag(x)==k),None)
def children(n,k):return [x for x in n if tag(x)==k]
def val(x):return json.loads(x) if x.startswith('"') else x
def q(x):return json.dumps(str(x),ensure_ascii=False)
def prop(n,k):return next(x for x in children(n,'property') if val(x[1])==k)
