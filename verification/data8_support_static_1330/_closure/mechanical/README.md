# Isolated mechanical verification: accepted data8/support

25 accepted scripts, normal and optimized: **50/50 exit 0**. All 492 selected frozen input bytes remain exact. Obsolete independent_exits.py/log were removed only from local reconstruction after root-confirmed narrowing; the already scheduled two obsolete invocations were skipped before file access, not counted as passes.

Original saved CAD reopen, exact source-hash binding, nominal contacts, and the three earlier zero-gap specimens used as negative controls all pass. NOFAB/NOPOWER; no SI, material, dynamic or manufacturing qualification inferred.

## Exactness
24/25 normal/-O output-JSON pairs byte-equal. The support reconstruction JSON differs solely in three actual regenerated FCStd SHA256 fields, validated against the generated container bytes. Both screen report variants now bind the later-frozen author manifest instead of the old NOT_YET_FROZEN/0 report metadata. OUTPUT_DELTA_WHITELIST.json records exact pointers and before/after values, no broad hash-key removal accepted. All remaining geometry fields equal frozen expected values.

## Reproduce from selected aliases
Place reproduce_final492.py, launcher.py and sitecustomize.py together. Reconstruct the aliases selected by FINAL_SOURCE_MAP.json into an input directory using the publication source-map instructions. Run:

    /usr/bin/python3 reproduce_final492.py --source-map FINAL_SOURCE_MAP.json --input-root /path/to/reconstructed --output /path/to/fresh-empty-output

Setup hashes all selected inputs against pinned final492 map. Requires system pcbnew and FreeCAD/Part (/usr/lib/freecad-python3/lib); offscreen Qt. One native subprocess at a time; timeout300s each. Outputs must be fresh, not reused. All normal and -O scripts run in separate private output folders, other aliases symlink the frozen view. Original absolute inventory paths are relocated in memory only. Inherited sitecustomize Python guards prohibit live-workspace/source fallbacks and frozen writes, including the child Python pcbnew extractor. Child startup records .audit_processes.jsonl evidence. This is NOT a native syscall-sandbox proof.

The executed original run_all.py remains local audit only; it started with the approved494 proposal. Its obsolete final494 invariant consequently found one removed file after all tests completed. finalize.py applied the confirmed492 scope and created the authoritative SUMMARY.json/ACCEPTED_RESULTS.json. The standalone runner uses final492 from the start and needs no original workspace setup access. Do not publish run_all.py/finalize.py or obsolete scheduler rows as reusable acceptance scripts.
