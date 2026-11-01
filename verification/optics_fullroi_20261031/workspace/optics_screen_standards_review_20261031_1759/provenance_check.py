import json,hashlib,pathlib,subprocess
r=pathlib.Path('/workspace/scratch/fe148e758944/publication_20261031/target_repo')
d=pathlib.Path('/workspace/scratch/fe148e758944/optics_paper_screen_20261031_1752')
print('disk HEAD',subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip())
for f in ['SOURCE_HASHES.json','decoder_probe/summary.json','decoder_probe/controls_summary.json']:
 j=json.loads((d/f).read_text()); hs=j.get('source_sha256',j)
 disk=[p for p,h in hs.items() if hashlib.sha256((r/p).read_bytes()).hexdigest()!=h]
 commit=[p for p,h in hs.items() if hashlib.sha256(subprocess.check_output(['git','-C',str(r),'show','f92911bc:'+p])).hexdigest()!=h]
 print(f, 'entries',len(hs),'disk mismatches',disk,'f92911bc mismatches',commit)
 if disk or commit:raise RuntimeError('hash mismatch')
