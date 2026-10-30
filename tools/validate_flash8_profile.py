#!/usr/bin/env python3
"""Read-only profile verification; never flash. --idf selects official SDK tools."""
from __future__ import annotations
import argparse, ctypes, csv, hashlib, json, os, pathlib, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAIN=ROOT/'firmware/application_idf/main'
CSV=ROOT/'firmware/application_idf/profiles/flash8.csv'
def require(ok, text):
    if not ok: raise RuntimeError(text)
def run_host():
    results=[]
    with tempfile.TemporaryDirectory(prefix='pen-profile8-host-') as td:
        for enabled in (0,1):
            for mode,flags in [('normal',[]),('ndebug',['-DNDEBUG']),('asan_ubsan',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
                exe=pathlib.Path(td)/f'guard-{enabled}-{mode}'
                cmd=['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',*flags,f'-DTEST_PROFILE_ENABLED={enabled}',
                     '-I'+str(ROOT/'tests/profile8_stubs'),'-I'+str(MAIN),str(ROOT/'tests/test_partition_profile8.c'),
                     str(MAIN/'partition_profile.c'),str(MAIN/'partition_profile_idf.c'),'-o',str(exe)]
                subprocess.run(cmd,check=True,capture_output=True,text=True)
                env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0') # LSan unavailable under ptrace; ASan/UBSan remain on.
                p=subprocess.run([str(exe)],check=True,capture_output=True,text=True,env=env)
                results.append({'profile_enabled':bool(enabled),'mode':mode,'exit':p.returncode,'stdout':p.stdout.strip()})
    return results
def verify_sdk(idf, python):
    tool=idf/'components/partition_table/gen_esp32part.py'
    require(tool.is_file(),'official partition tool not found')
    with tempfile.TemporaryDirectory(prefix='pen-profile8-table-') as td:
        td=pathlib.Path(td); binary=td/'table.bin'; roundtrip=td/'roundtrip.csv'
        cmd=[str(python),str(tool),'--flash-size','8MB','--offset','0x8000']
        subprocess.run(cmd+[str(CSV),str(binary)],check=True,capture_output=True,text=True)
        subprocess.run(cmd+[str(binary),str(roundtrip)],check=True,capture_output=True,text=True)
        rows=list(csv.reader(x for x in roundtrip.read_text().splitlines() if x and not x.startswith('#')))
        def number(v):
            v=v.strip();return int(v[:-1],0)*{'K':1024,'M':1024*1024}[v[-1]] if v[-1:] in ('K','M') else int(v,0)
        types={'app':0,'data':1};subs={'nvs':2,'ota':0,'phy':1,'ota_0':16,'ota_1':17}
        class Part(ctypes.Structure):
            _fields_=[('label',ctypes.c_char_p),('address',ctypes.c_uint32),('size',ctypes.c_uint32),
                      ('type',ctypes.c_uint8),('subtype',ctypes.c_uint8),('encrypted',ctypes.c_uint8),('readonly',ctypes.c_uint8)]
        values=[]
        for row in rows:
            name,typ,sub,offset,size,flags=[v.strip() for v in row]
            require(not flags,'unexpected table flags')
            subtype=subs[sub] if sub in subs else int(sub,0)
            values.append(Part(name.encode(),number(offset),number(size),types[typ],subtype,0,0))
        shared=td/'profile.so'
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-shared','-fPIC',str(MAIN/'partition_profile.c'),'-o',str(shared)],check=True,capture_output=True)
        lib=ctypes.CDLL(str(shared));lib.pen_profile8_validate.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Part),ctypes.c_size_t]
        lib.pen_profile8_validate.restype=ctypes.c_int
        arr=(Part*len(values))(*values)
        require(lib.pen_profile8_validate(0x800000,0x800000,arr,len(values))==0,'official decoded table rejected by actual C runtime contract')
        mutations={'overlap':('0x420000,0x3e0000','0x400000,0x3e0000'),
                   'app_not_64k_aligned':('ota_0,app,ota_0,0x20000,0x200000','ota_0,app,ota_0,0x21000,0x1f0000'),
                   'beyond_8mib':('0x420000,0x3e0000','0x420000,0x400000')}
        negatives=[]
        for name,(old,new) in mutations.items():
            source=CSV.read_text();require(old in source,'negative mutation not applied')
            bad=td/(name+'.csv');bad.write_text(source.replace(old,new,1))
            p=subprocess.run(cmd+[str(bad),str(td/(name+'.bin'))],capture_output=True,text=True)
            require(p.returncode!=0,f'official tool accepted invalid {name}')
            negatives.append({'case':name,'exit':p.returncode,'stderr':p.stderr.strip()})
        return {'sdk_commit':subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip(),
                'official_roundtrip_csv':roundtrip.read_text(),'binary_bytes':binary.stat().st_size,
                'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
                'runtime_contract_accepts_official_table':True,'negative_cases':negatives}
def main():
    p=argparse.ArgumentParser();p.add_argument('--idf',type=pathlib.Path);p.add_argument('--sdk-python',type=pathlib.Path,default=pathlib.Path(sys.executable));p.add_argument('--output',type=pathlib.Path)
    a=p.parse_args();result={'host_tests':run_host()}
    if a.idf: result['official_sdk']=verify_sdk(a.idf.resolve(),a.sdk_python.resolve())
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:
        require(not a.output.exists(),'refuse to overwrite verification evidence')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    print(text)
if __name__=='__main__':main()
