# Append-only correction: non-vacuous raw-footprint evidence

Some prior MCAD auxiliary text scanners looked for newline immediately after `(footprint`, whereas native KiCad has `(footprint "library:name"`. Those particular rawfootprint comparisons could therefore compare emptylists. Their old assertions do not constitute rawidentity evidence. Other nativepcbnew pose/pad/finitebody/savedscene checks were independent; no board difference is assumed merely from this verification bug.

Corrected scanner accepts namedfootprint syntax and explicitly requires exactly103 nonemptyfootprint blocks and103uniqueReferences for EVERY input. It independently re-audits ten snapshots spanning base28→TP27→combined26→EXTCLK25→D5_24→617a→cb462→f679→1639→unaccepted4ab. All actual rawchanges match the recorded allowlists: TP301 only; then none/none/none; J107 only; R108 only; none; none; R230 only. Exactsourcepaths/hashes and comparison counts are in results.json. In particular the requested accepted617a→cb462→f679→1639 chain has no unauthorized difference.

Emptyinput and deliberately deletedfootprint reject on103count; deliberately changed unchangedR224 block is detected. Normal/-O outputs match. Thus this is correction/strengthening of validation evidence, NOT a nativechange or an invitation to mutate historicalmanifests. Frozen earlier reports remain unchanged and should cite this supplement for their rawfootprint claims. Independent ECAD additionally enforces nonempty103-count parsing; this supplement does not depend on that separate check.

NewR230 final must use corrected103-count scanner and explicitly authorized J107EN1text-only difference; old4ab is still unaccepted in this historical audit. No general body/operation exception or power/FAB release follows.

Replay `/usr/bin/python3 check.py` and `-O` with the exact nativepaths/hashes listed in results. A publication that omits these historicnative inputs must call this a documentary validation record, not claim portable replay. No native or oldmanifest file modified.
