"""Exact integer conditional capacity arithmetic, no implementation code."""
import json
rows=[]
for capacity,page in [(64,4096),(128,2048),(256,2048),(512,4096)]:
 per=(page-128)//64
 slots=(capacity*1048576*3//4//page)*per
 slack=1024*(per-1)
 n=(slots-slack)*5184000//5984000
 extra=lambda x:(x*800000+5184000-1)//5184000
 assert n+extra(n)<=slots-slack and n+1+extra(n+1)>slots-slack
 rows.append(dict(capacity_MiB=capacity,container_bytes=page,records_per_container=per,slots=slots,session_slack=slack,max_observations=n,extra_events=extra(n),hours_60Hz=n/216000))
print(json.dumps(rows,indent=2))
