#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
r=Path(__file__).resolve().parents[1]
incs=['include','frozen/application','frozen/runtime','frozen/vision','frozen/storage','frozen/codec','frozen/portable']
with tempfile.TemporaryDirectory(prefix='pen-camera-test-') as d:
 cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wconversion','-Wshadow','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']
 cmd += [f'-I{r/p}' for p in incs]
 cmd += [str(r/p) for p in ['src/pen_capture.c','src/pen_capture_app.c','src/pen_capture_profiles.c','tests/test_capture.c']]
 cmd+=['-o',d+'/test']
 subprocess.run(cmd,check=True);subprocess.run([d+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})

with tempfile.TemporaryDirectory(prefix='pen-sc031-test-') as d:
 u=r/'third_party/esp32-camera'
 cmd=['gcc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Werror','-fsanitize=address,undefined','-g','-O1']
 cmd += [f'-I{p}' for p in [r/'tests/stubs',u/'driver/include',u/'driver/private_include',u/'sensors/private_include']]
 cmd += [str(p) for p in [r/'tests/test_sc031gs.c',u/'sensors/sc031gs.c',u/'driver/sensor.c']]
 cmd += ['-o',d+'/test']
 subprocess.run(cmd,check=True);subprocess.run([d+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})

with tempfile.TemporaryDirectory(prefix='pen-sccb-test-') as d:
 u=r/'third_party/esp32-camera'
 cmd=['gcc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Werror','-fsanitize=address,undefined','-g','-O1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections']
 cmd += [f'-I{p}' for p in [r/'tests/stubs',u/'driver/include',u/'driver/private_include']]
 cmd += [str(r/'tests/test_sccb_checked.c'),'-o',d+'/test']
 subprocess.run(cmd,check=True);subprocess.run([d+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})

# v2 actual table writer and complete camera-probe-reset chain regressions.
for test in ['test_sc031gs_tables','test_driver_api','test_hal_cleanup']:
 with tempfile.TemporaryDirectory(prefix='pen-camera-v2-') as d:
  u=r/'third_party/esp32-camera'
  stub=r/('tests/stubs' if test=='test_sc031gs_tables' else 'tests/driver_stubs')
  cmd=['gcc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-int-to-pointer-cast','-Wno-pointer-to-int-cast','-Werror','-fsanitize=address,undefined','-g','-O1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections']
  cmd += [f'-I{p}' for p in [stub,u/'driver/include',u/'driver/private_include',u/'sensors/private_include',u/'target/private_include']]
  if test=='test_hal_cleanup':cmd += ['-Wno-sign-compare']
  cmd += [str(r/'tests'/f'{test}.c'),str(u/'driver/sensor.c')]
  if test=='test_driver_api':cmd += [str(u/'sensors/sc031gs.c')]
  cmd += ['-o',d+'/test']
  subprocess.run(cmd,check=True);subprocess.run([d+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})

for test in ['test_idf_backend','test_core_extra']:
 with tempfile.TemporaryDirectory(prefix='pen-camera-v2-extra-') as d:
  u=r/'third_party/esp32-camera'
  cmd=['gcc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Werror','-fsanitize=address,undefined','-g','-O1']
  cmd += [f'-I{r/p}' for p in incs]
  cmd += [f'-I{p}' for p in [r/'tests/driver_stubs',u/'driver/include',u/'driver/private_include']]
  cmd += [str(r/'tests'/f'{test}.c'),str(r/'src/pen_capture.c')]
  if test=='test_core_extra':cmd += [str(r/'src/pen_capture_app.c'),str(r/'src/pen_capture_profiles.c')]
  cmd += ['-o',d+'/test']
  subprocess.run(cmd,check=True);subprocess.run([d+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
