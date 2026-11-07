R3 first full execution stopped on a test-counter expectation, not a candidate source failure.
The new direct ACK test expected lifetime syncs==2 after reopening the store.
Actual pen_log_open calls sync once, so lawful ACK should add exactly two syncs to the count at ACK entry.
Changed only the test to measure write/sync deltas; candidate source unchanged.
Initial failure trace:

$ <FROZEN_GUARD_R3>/build/runner store
maintenance line 35: pen_store_ack(&store,7,0,1)==0&&writes==2&&syncs==2
[exit 1, expected 0]
