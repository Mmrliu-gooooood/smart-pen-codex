"""Portable fixed-PGM host regression adapter (new r5 helper, not frozen source).

No downloads/devices; compiles only the verified bundled C sources in a temporary
folder. Uses Python standard library + installed cc/libm. No timing is reported.
Frozen artifacts are never written. Output is a new JSON report on stdout.
"""
import argparse
import ast
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
FROZEN_SHA = 'dc8303fef58385b15ca652618bd52082f3078dc887c52fee1397f1dd4f3a4c62'
ORACLE_SHA = '191f83e9a3b62d31ec9e2efd34ed640c3e5c7caed1d59ecd02b7a199480f5571'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def child(root, relative):
    relative = Path(relative)
    require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe relative path')
    path = root / relative
    require(path.is_file() and not path.is_symlink(), str(path))
    require(path.resolve().is_relative_to(root.resolve()), 'path escapes source root')
    return path


class Config(C.Structure):
    _fields_ = [('w', C.c_uint16), ('h', C.c_uint16), ('u', C.c_uint8), ('v', C.c_uint8)]


class Result(C.Structure):
    _fields_ = [('x', C.c_uint16), ('y', C.c_uint16), ('dots', C.c_uint16),
                ('windows', C.c_uint16), ('pitch', C.c_float), ('angle', C.c_float),
                ('residual', C.c_float), ('directions', C.c_uint8 * 36)]


class Opt(C.Structure):
    _fields_ = [('decoded', Result), ('y_scale', C.c_float),
                ('candidates', C.c_uint32), ('used_warm', C.c_uint8)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir', type=Path, default=HERE / 'smart_pen_viewport_audit_20261028')
    parser.add_argument('--benchmark-dir', type=Path, default=HERE / 'smart_pen_decoder_target_benchmark_20261028')
    args = parser.parse_args()
    audit, source = args.audit_dir.resolve(), args.benchmark_dir.resolve()
    frozen = child(source, 'verification/FROZEN_SOURCE_SHA256SUMS').read_bytes()
    require(digest(frozen) == FROZEN_SHA, 'benchmark frozen list mismatch')
    checks = {}
    for line in frozen.decode().splitlines():
        expected, relative = line.split(maxsplit=1)
        require(digest(child(source, relative).read_bytes()) == expected, relative)
        checks[relative] = expected
    require(len(checks) == 31, 'frozen source count')
    oracle_bytes = child(audit, 'regression_manifest.json').read_bytes()
    require(digest(oracle_bytes) == ORACLE_SHA, 'viewport regression oracle mismatch')
    oracle = json.loads(oracle_bytes)
    require(len(oracle['fixtures']) == 44, 'fixed fixture count')
    # uint8 data only; never np.load()/pickle or import the historical generator.
    encoded = child(audit, 'upstream_directions.npy').read_bytes()
    require(encoded[:8] == b'\x93NUMPY\x01\x00', 'unsupported NPY')
    n = struct.unpack('<H', encoded[8:10])[0]
    header = ast.literal_eval(encoded[10:10+n].decode().strip())
    require(header == {'descr': '|u1', 'fortran_order': False, 'shape': (1000, 710)}, 'NPY shape/type')
    directions = encoded[10+n:]
    require(len(directions) == 710000 and max(directions) <= 3, 'NPY payload')
    # Pin the saved upstream matrix separately, in addition to the package manifest.
    require(digest(encoded) == 'd82439c4d9bac955ef56876035715bcad64f1e1e451bb42f0598c235b02ae0c7', 'upstream matrix hash')
    records = []
    with tempfile.TemporaryDirectory(prefix='smartpen-r5-replay-') as tmp:
        tmp = Path(tmp)
        bridge = tmp / 'bridge.c'
        bridge.write_text('#include "roi_opt.h"\nsize_t ws_size(void){return sizeof(pen_roi_workspace);}\n')
        library = tmp / 'replay.so'
        command = ['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-shared', '-fPIC',
                   '-I' + str(source / 'vision'), str(bridge), str(source / 'vision/roi_opt.c'),
                   str(source / 'codec/anoto.c'), '-lm', '-o', str(library)]
        subprocess.run(command, check=True)
        lib = C.CDLL(str(library))
        lib.ws_size.restype = C.c_size_t
        workspace_bytes = lib.ws_size()
        workspace = (C.c_double * ((workspace_bytes + 7) // 8))()
        decode = lib.pen_roi_decode_opt
        decode.argtypes = [C.POINTER(C.c_uint8), C.c_size_t, C.c_uint, C.c_uint, C.c_uint,
                           C.POINTER(Config), C.c_void_p, C.c_void_p, C.POINTER(Opt)]
        decode.restype = C.c_int
        cfg = Config(*oracle['paper_config'])
        for row in oracle['fixtures']:
            pgm = child(audit, row['fixture']).read_bytes()
            magic, dimensions, maximum, pixels = pgm.split(b'\n', 3)
            width, height = map(int, dimensions.split())
            require(magic == b'P5' and maximum == b'255' and len(pixels) == width*height, 'PGM framing')
            require(width == height == row['size'], 'fixture dimensions')
            require(digest(pixels) == row['image_sha256'], 'PGM pixel hash')
            image = (C.c_uint8 * len(pixels)).from_buffer_copy(pixels)
            result = Opt()
            C.memset(C.byref(result), 0xa5, C.sizeof(result))
            before = bytes(result)
            status = decode(image, len(pixels), width, height, width, C.byref(cfg), workspace, None, C.byref(result))
            expected = row['cold']
            require(status == expected['status'], row['fixture'] + ': status')
            extra = {}
            if status == 0:
                x, y = result.decoded.x, result.decoded.y
                require((x, y) == (expected['x'], expected['y']), 'frozen coordinate oracle')
                require(x+5 < 710 and y+5 < 1000, 'decoded coordinate bounds')
                independent = [directions[(y+dy)*710+x+dx] for dy in range(6) for dx in range(6)]
                require(list(result.decoded.directions) == independent, 'upstream direction oracle')
                pitch = 60 / row['fov_mm']
                left = row['ox_cells'] + (200-width)/2/pitch
                top = row['oy_cells'] + (200-height)/2/pitch
                require(left-1/3 <= x and x+5 <= left+width/pitch+1/3, 'horizontal viewport oracle')
                require(top-1/3 <= y and y+5 <= top+height/pitch+1/3, 'vertical viewport oracle')
                require(result.used_warm == 0, 'NULL prior must not use warm path')
                extra = {'coordinate': [x, y], 'encoded_symbols_match': True, 'viewport_match': True}
            else:
                require(bytes(result) == before, 'failure output preservation')
                extra = {'failure_output_preserved': True}
            records.append({'fixture': row['fixture'], 'status': status, 'passed': True, **extra})
    print(json.dumps({'adapter': 'portable_replay.py new r5 adapter', 'scope': 'host fixed-image functional regression only',
                      'device_measured': False, 'synthetic_only': True, 'physical_safety_claim': False,
                      'cold_prior': 'NULL', 'input_oracle_injected': False,
                      'frozen_source_manifest_sha256': FROZEN_SHA, 'regression_manifest_sha256': ORACLE_SHA,
                      'frozen_source_files_verified': len(checks), 'workspace_bytes_host_abi': workspace_bytes,
                      'count': len(records), 'passed': len(records),
                      'accepted': sum(r['status'] == 0 for r in records), 'records': records}, indent=2))


if __name__ == '__main__':
    main()
