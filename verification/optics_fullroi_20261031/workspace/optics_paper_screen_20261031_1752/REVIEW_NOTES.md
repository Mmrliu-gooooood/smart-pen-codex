# Bounded review notes

Independent geometry reviewer checked actual model/test files: ideal pinhole projection/Jacobian and positive-depth enclosing-square corner containment agree with declared model; no fixed-grid classification blocker identified. It supplied a transposed numerical oracle and pointed out dot minor diameter must use minimum singular value, not minimum column norm. Implementation uses `sigma_min=abs(det J)/sigma_max`; regression with expected1.96182853324px minor diameter flags the <2px proxy. Generic extreme-depth underflow was identified; numeric domain now fails closed and has a1e−300 regression. Fourteen tests pass in normal and optimized Python.

Review does not approve optical hardware, all possible parameter values, real decoder performance or paper choice. Full independent product acceptance is not claimed. The actual C probe is a separate agent's deterministic test, not a replacement for external review of a new algorithm; no algorithm was changed.

Reproduction inputs are published source paths plus hashes. Generated source code, data and reports may be checkpointed privately. Public publication of this new study is not performed by this task. The previously published source repository remains unchanged by this study.

Final independent enumeration reproduced551/829/5637/183 and14tests; reviewed model SHA256 a9457fde04df4b235c2310d3f665c7d2f7106ee18a64a051e264553aae387488. Nonblocking caveats: field blur_bound_px is only the documented sampled first-order estimate, not rigorous integrated-motion bound; INVALID_DEPTH catch is accurate for this fixed grid but future out-of-domain ranges need a separate numeric-invalid label. Test direct-entry unittest.main was moved after all classes, so direct execution now also discovers all14.
