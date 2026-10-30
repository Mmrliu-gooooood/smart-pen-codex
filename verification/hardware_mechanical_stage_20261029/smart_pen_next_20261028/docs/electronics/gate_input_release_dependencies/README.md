# 门控输入冻结版的本地发布依赖闭包

仅本地归档建议，不授权或宣称远端发布。当前可复验包为 **135 违规 / 54 未连 / parity 0，NOFAB，JP301 OPEN**；正在变的完整门控试验不属于本闭包。

四个直接完整包共413个列明成员，另含各自manifest。原独审 `source_rules.py` 会逐项验证这些manifest，因此不能裁掉列明成员后仍说原脚本可以原样复跑。它不递归执行所有祖先builder；无需复制整个多版本树。`closure.json` 明确当前验证范围、所需KiCad版本/标准库和额外原厂/历史证据allowlist。

C503旧BOM的dimension_evidence记了旧README路径和哈希；同一路径后来补入真实偏压曲线。旧内容没有丢失，冻结的 `imu_decoupling_c503_source_fix/manufacturer_basis_snapshot.md` 恰为原哈希。闭包给出按内容身份解析的历史映射；不改旧BOM，不把新README伪装为旧文件。旧C503 manifest仅证明这一个历史snapshot的成员身份，不宣称收齐整个旧源包。当前补充曲线作为另一个明确版本并存。

源MPN仍为候选，缺机械、动态、电源完整性、成本与安全资格。制造export不得仅拿XML忽略ProcurementStatus和外部BOM，也不得从此闭包推导已可采购/投板。

按主任务发布策略，原厂PDF和页面图像只留本地，公开候选包保留摘要、官方URL及原始SHA；`external_evidence_not_in_publication` 明列四个不随包的原厂文件。因而外部资料包仅文本子集，不宣称它们的旧完整manifest在发布目录可全项复验。当前四个原生设计/独审包仍全项完整，其审核脚本不依赖被省略的原厂PDF二进制。

闭包生成器支持平坦hash、`files`→hash和`files`→`{sha256,bytes}`三种实际清单形态；未识别格式直接失败。首次临时验证曾把dict错与字符串比较，造成虚假README漂移警报，已纠正并重新实际核完整413项，未修改任何冻结包。
