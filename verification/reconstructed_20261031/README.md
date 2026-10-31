# 2026-10-31 关键设计资料归档

**静态研究 / NOFAB / NOPOWER。** 先读[根状态页](../../CURRENT_STATUS.md)。本目录补齐已冻结资料中的必要内容及复现依赖，不替换根目录活动固件，不将 ZIP 文件堆叠为新的并行产品版本。

## 阅读顺序与工程入口

以下 `workspace/` 为原始相对工作区路径；如采用去重存储，请先依本目录 SOURCE_MAP 与重建脚本还原到新的可写工作区，不能直接混搭已有工程。映射以文件 SHA-256 为准。

| 内容 | 工作区相对入口 | 当前边界 |
|---|---|---|
| 最新静态 PCB | [reconstruction_control_service_20261031_0510/README.md](workspace/reconstruction_control_service_20261031_0510/README.md)、`final_candidate/mainboard_revD.kicad_pcb`、`RUN_CHECKS.md` | 7522… / 0/37/0；不是整笔验收 |
| 独立复核 | [independent_control_service_full_20261031_0533/REVIEW.md](workspace/independent_control_service_full_20261031_0533/REVIEW.md) | 有限静态范围；须连同 advisory 阅读 |
| 保存的 CAD | [reconstruction_saved_cad_d855_20261031_0317/README.md](workspace/reconstruction_saved_cad_d855_20261031_0317/README.md) 及四组 FCStd/STEP | 保存元数据仍是 d855；RevD_BENCH 非笔壳 |
| 后继几何绑定 | [reconstruction_control_service_final_mechanics_20261031_0524/README.md](workspace/reconstruction_control_service_final_mechanics_20261031_0524/README.md) | 位姿/板框未变，名义几何沿用；非重新保存 7522 CAD |
| 禁用采集适配器 | [capture_actor_adapter_20261031_0600/README.md](workspace/capture_actor_adapter_20261031_0600/README.md)、[review_capture_adapter_20261031_0610/REVIEW.md](workspace/review_capture_adapter_20261031_0610/REVIEW.md) | host 限定复核；未接入活动构建；provider NULL |
| 采集集成差额 | [sc031gs_integration_delta_20261031_0556/INTEGRATION_DELTA.md](workspace/sc031gs_integration_delta_20261031_0556/INTEGRATION_DELTA.md) | 软件接口约束，不是现货模块/镜头资格 |
| 离线容量与成本 | [offline_storage_budget_decision_20261031_0607/DECISION.md](workspace/offline_storage_budget_decision_20261031_0607/DECISION.md) 及关联方案 | 24 小时目标未满足；760 元总预算未闭合 |
| 未完成探索 | [reconstruction_enable_group_20261031_0541/README.md](workspace/reconstruction_enable_group_20261031_0541/README.md) | 56e01… / 0/34/0；仅必要状态证据，不是可采用后继 |

光学纠正另见 [纠正说明](optics/CORRECTIVE_OVERLAY_ZH.md)与[参数化联合验证合同](optics/CODESIGN_VALIDATION_ZH.md)。公开版为明确标注的衍生文档，移除私人消息标识和私有分析路径；原始来源哈希、改动说明见公开 provenance manifest。原始用户照片、PDF、私有分析和资料库收据不在本归档中，不能声称这些私有实物分析可从公开仓库完整重现。

## 复现与使用边界

使用去重映射还原依赖后，在**新可写副本**按各模块 RUN_CHECKS / README 执行；保持冻结源字节不变。历史目录是被脚本、manifest 或保存模型消耗的依赖，不意味着重新采用旧硬件。公开包未复制原始 ZIP 和不必要的完整历史快照；必要文件按哈希映射到既有或新增仓库路径。

KiCad 原生检查、FreeCAD 重开/STEP 检查、host 测试分别证明各自有限范围，不能相互替代。新执行记录应独立存放，不能改写历史 PASS/PENDING/失败证据。本目录中的测试替身、合成数据和空生产配置均不是实物资格。

## 精确去重复现

[SOURCE_MAP.json](SOURCE_MAP.json) 绑定 2435 个原始相对路径。运行 `python3 verification/reconstructed_20261031/reconstruct.py /绝对路径/新空目录`，逐项校验并还原；不下载资料、不运行恢复的源码。774 个新增唯一文件，其余复用既有或本包相同字节。先重建完整目录，不能直接把去重后的残缺子目录当作完整 KiCad 工程。历史报告内绝对临时路径仅为当时运行记录；复现须按相对目录入口与当前工具环境进行。

## 可直接浏览/下载的当前关键文件

这些链接是仓库内真实存储路径；完整原生工程及复现依赖仍须用 SOURCE_MAP 重建。CAD 元数据绑定 d855，不称为重新保存的 7522。

- [capture_actor_adapter_20261031_0600/include/adapter.h](workspace/capture_actor_adapter_20261031_0600/include/adapter.h)
- [capture_actor_adapter_20261031_0600/src/adapter.c](workspace/capture_actor_adapter_20261031_0600/src/adapter.c)
- [reconstruction_control_service_20261031_0510/final_candidate/mainboard_revD.kicad_pcb](workspace/reconstruction_control_service_20261031_0510/final_candidate/mainboard_revD.kicad_pcb)
- [reconstruction_saved_cad_d855_20261031_0317/ACCESS19_NEW_d855_RESEARCH_NOFAB.FCStd](workspace/reconstruction_saved_cad_d855_20261031_0317/ACCESS19_NEW_d855_RESEARCH_NOFAB.FCStd)
- [reconstruction_saved_cad_d855_20261031_0317/ACCESS19_NEW_d855_RESEARCH_NOFAB.step](workspace/reconstruction_saved_cad_d855_20261031_0317/ACCESS19_NEW_d855_RESEARCH_NOFAB.step)
- [reconstruction_saved_cad_d855_20261031_0317/ACCESS20_NEW_d855_RESEARCH_NOFAB.FCStd](workspace/reconstruction_saved_cad_d855_20261031_0317/ACCESS20_NEW_d855_RESEARCH_NOFAB.FCStd)
- [reconstruction_saved_cad_d855_20261031_0317/ACCESS20_NEW_d855_RESEARCH_NOFAB.step](workspace/reconstruction_saved_cad_d855_20261031_0317/ACCESS20_NEW_d855_RESEARCH_NOFAB.step)
- [reconstruction_saved_cad_d855_20261031_0317/RevC_NEW_d855_RESEARCH_NOFAB.FCStd](workspace/reconstruction_saved_cad_d855_20261031_0317/RevC_NEW_d855_RESEARCH_NOFAB.FCStd)
- [reconstruction_saved_cad_d855_20261031_0317/RevC_NEW_d855_RESEARCH_NOFAB.step](workspace/reconstruction_saved_cad_d855_20261031_0317/RevC_NEW_d855_RESEARCH_NOFAB.step)
- [reconstruction_saved_cad_d855_20261031_0317/RevD_BENCH_NEW_d855_RESEARCH_NOFAB.FCStd](workspace/reconstruction_saved_cad_d855_20261031_0317/RevD_BENCH_NEW_d855_RESEARCH_NOFAB.FCStd)
- [reconstruction_saved_cad_d855_20261031_0317/RevD_BENCH_NEW_d855_RESEARCH_NOFAB.step](workspace/reconstruction_saved_cad_d855_20261031_0317/RevD_BENCH_NEW_d855_RESEARCH_NOFAB.step)
- [review_capture_adapter_20261031_0610/REVIEW.md](workspace/review_capture_adapter_20261031_0610/REVIEW.md)
