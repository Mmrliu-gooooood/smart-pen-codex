import pcbnew as p,json,sys,uuid
from pathlib import Path
def unique_object(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise RuntimeError('Duplicate JSON key/UUID: '+k)
  d[k]=v
 return d
def validate(board_path,contract_path):
 j=json.loads(Path(contract_path).read_text(),object_pairs_hook=unique_object)
 if not isinstance(j,dict):raise RuntimeError('Expected contract must be an object')
 expected=j['expected'] if 'expected' in j else j
 if not isinstance(expected,dict) or not expected:raise RuntimeError('Empty or non-object expected-net contract forbidden')
 for key,value in expected.items():
  try:uuid.UUID(key)
  except (ValueError,TypeError,AttributeError) as error:raise RuntimeError('Invalid expected UUID: '+str(key)) from error
  if not isinstance(value,str) or not value.strip():raise RuntimeError('Empty/non-string literal expected net for '+key)
 b=p.LoadBoard(str(board_path))
 if b is None:raise RuntimeError('Failed to load board')
 actual={}
 for t in b.GetTracks():
  key=t.m_Uuid.AsString()
  if key in actual:raise RuntimeError('Duplicate copper UUID in board: '+key)
  actual[key]=t.GetNetname()
 bad={key:{'expected':value,'actual':actual.get(key),'missing_uuid':key not in actual} for key,value in expected.items() if actual.get(key)!=value}
 result={'board':str(board_path),'expected_item_count':len(expected),'failures':bad};print(json.dumps(result,indent=2))
 if bad:raise RuntimeError('STOP: missing UUID or literal expected-net mismatch after load')
 return result
if __name__=='__main__':validate(Path(sys.argv[1]),Path(sys.argv[2]))
