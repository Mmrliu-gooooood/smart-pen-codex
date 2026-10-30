# V3 RAM accounting — compile/link only

One internal heap workspace **32,640 B** = old core21,888 +64 seed records×24 =1536 +crop9216. Frozen old core and V3 reuse the same core allocation sequentially; **not two workspaces**. One raw input allocation40,000 B: total **72,640 B**, before RTOS/libc/stacks and static data.

Nine palette-RLE arrays total **105,864 B**, palettes **125 B**, plus names/pointers/alignment. All immutable fixture data are internal DRAM in PURE_RAM, not Flash. Exact raw PGM bytes/SHA are preserved; packing changes no decode image. Palette compression reduced data pressure versus triple-byte RLE; no allocation-success claim follows.

Final ELF size reports text135,314 B/data139,925 B/bss-labelled121,688 B. Text includes frozen and V3 decoders, full printf/snprintf/dtoa, trace shim and IDF; bss-labelled includes alias/dummy reservations, so naive sum is not physical peak. Load image275,344 B. See sections-enabled.txt and compiler-stack-usage.txt.

Main task stack16KiB, other RTOS stacks additional. `.su` lists individual frames only. Diagnostic shim adds4 uint32 counters +call count static storage and bounded stack; copies are inside V3 timing. Full printf dynamic heap/stack not measured. Need real per-record heap/stack to establish margin.

Actual target static_assert confirms32,640 B workspace and production64-seed bound. Build/link fit is NOT proof that72,640 B heap allocation pair succeeds on physical boot. Allocation failure or trace-capture mismatch emitsfatal and returns withoutcomplete; strict parser rejects partial logs, never grants partial throughput success. No target execution occurred.
