#ifndef FULLROI_CANDIDATE_H
#define FULLROI_CANDIDATE_H
#include "roi_opt.h"
#ifndef CANDIDATE_ENABLE_REFINEMENT
#define CANDIDATE_ENABLE_REFINEMENT 0
#endif
/* Standalone research only. No crop, fake prior, production provider or active integration.
 * Caller owns non-reentrant workspace; allocate as arena, not inferred target task stack.
 * Input/config/workspace/result/diagnostics must be disjoint. Overlap/range-wrap returns
 * ARGUMENT before any write; otherwise diagnostics reset per call, result unchanged
 * on failure. Gate OFF uses exact active cold; ON executes ALL bounded V3 consensus.
 */
typedef struct { pen_roi_workspace core; pen_roi_refine_seed seeds[PEN_ROI_REFINE_MAX_SEEDS]; } candidate_workspace;
int candidate_decode(const uint8_t *,size_t,unsigned,unsigned,unsigned,const pen_roi_config *,candidate_workspace *,pen_roi_opt_result *,pen_roi_refine_diagnostics *);
size_t candidate_workspace_size(void);
size_t candidate_result_size(void);
size_t candidate_diagnostics_size(void);
#endif
