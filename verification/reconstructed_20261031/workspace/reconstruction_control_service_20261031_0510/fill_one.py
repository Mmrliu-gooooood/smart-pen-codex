import os,sys,json,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
f=sys.argv[1];b=p.LoadBoard(f);fill=p.ZONE_FILLER(b);fill.Fill(b.Zones());p.SaveBoard(f,b);print(hashlib.sha256(open(f,'rb').read()).hexdigest())
