# Independent review: isolated cross-language offline ACK tests

2026-11-02. **PASS for the bounded software-model deliverable only.** No firmware integration, board power, fabrication, radio or real power-loss release follows.

## Exact reviewed input

- Author directory: `offline_ack_crosswire_20261102_0404`.
- Author manifest SHA-256: `766d6a52894e03b4d97ad3e1d97355734d7deb4277480e85a06414e44689f739`.
- All 17 listed payload byte counts and SHA-256 values match.
- The provided 8 source files match their pinned SHA-256 and Git blob SHA-1 identities. The author's source receipt associates those blobs with public commit `d413b45684d18c744dcfe550ec80136d86856f75`; this independent pass verifies the local byte chain, not a fresh remote commit-tree retrieval.
- No author files were edited. Test binaries, temporary databases and mutation copies used temporary directories.

## Replayed checks

`review.py` executes and records return codes, rather than relying on a final shell command's status:

- Source identity check: PASS.
- 12 cross-language test methods: PASS in normal Python and `-O`.
- Existing actual C storage regression: PASS.
- Four negative mutations, each tested under `-O`, all rejected: ACK before journal acceptance; using cumulative frontier as ACK instead of current offered sequence; omitting SQLite commits; allowing reclaim of unacknowledged records.

The four mutations are negative controls of the harness, not product changes. Their logs show executable test failures; none was accepted as a candidate fix.

## Code-level findings

The native fixture compiles unchanged `store.c` and `pen.c`, uses NOR-like immediate 1→0 programming, and retains media across `fixture_boot`. It does not replace storage logic with a Python mock. Host processing uses the actual Packet/Journal/framing implementation and SQLite. The child-process `os._exit` test checks persisted host records after abrupt process exit.

The integration distinction is real: `Journal.accept` returns a contiguous durable frontier; `pen_store_ack` accepts only the exact currently offered session and sequence. The test-only adapter appropriately waits for successful host acceptance and sufficient frontier before acknowledging the exact packet. The cumulative-frontier scenario is a legitimate adversarial compatibility state, not evidence that the present serial product path necessarily reaches it.

The 12 ACK cuts cover byte offsets before completion of an 8-byte body and 4-byte commit marker. Both sync failure points are covered. Immediate persistence can legitimately leave the ACK marker complete after the second sync reports failure; tests correctly permit this only after the host record was committed. Failed host writes and conflicts leave the device unacknowledged and unable to reclaim in the modeled state.

## Limits retained

- The model is 16 slots × 64 bytes, not the product's physical flash configuration. Erase-intent metadata writes are atomic in this fixture. Real page/controller caching, torn metadata, supply collapse, endurance and concurrent operations are outside this proof.
- Existing upstream storage tests provide additional modeled erase interruption coverage; that is not new cross-language coverage or a physical flash qualification.
- SQLite FULL still relies on OS/filesystem/hardware sync semantics. Process termination is not host power loss.
- The test fixture directly supplies the authenticated flag. Application connection epochs, callback races and real BLE authentication are not tested here. No active application/provider or host receiver was modified.
- Current sample/session limits and 24-hour capacity target are unchanged. No PCB, mechanical or electrical gates are relaxed.

No blocking defect was found for saving this deliverable as an isolated verification artifact with these limitations intact.
