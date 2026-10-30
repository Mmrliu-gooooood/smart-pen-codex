# 主板阶段恢复索引｜2026-10-29 19:00 UTC

正式接受基线仍为9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038，完整17违规/21未连/0parity，必须伴随原独审与两份VIO/微小参考投影勘误。未宣布整笔完成。JP301 OPEN；未知30针相机不接电。

## 本轮实铜增量（仅限定后继）

`hardware/dvp_reserved_corridor_study_1826/low_speed_trial`，108文件manifest SHA61e55b7d8217d476d4a1218af890af655aeb3f008d472e85bea099d308a9461b。PCB1d844c44e62e75a01f82e743e87b084707dd50d78afa94c9513aea6b034f5d94。

USB_EN1和TRIG回接、12条假定右侧轴向槽清空；102实体/源/其它铜/旧pad分量/电源地核心保持。原版绑定门、同basename规则、完整--all-track-errors为17/21/0。normal/-O、4负例、serialized delta和freshfill同SHA通过。初次漏all-track参数的16项报告明确拒绝，不是KiCad版本修复短路。

独审 `hardware/dvp_corridor_independent_review_1845`，24文件review_manifest SHA859c81c13f13bdddb493b17ad9b2bd1090879316f11ed8c28640660a84882155。17违规multiset相同，5个未连代表端条目变化被保留，不能说所有原生finding逐条一致。新参考缺口面积USB .217748384mm²、TRIG .180983582mm²（已扣孔）；USB最差附近GND via3.794898mm；TRIG末孔粗body名义余量.075mm。动态/制造/装配资格未关，不提升为正式主板基线。

## 三个新只读/研究冻结清单

1. `hardware/dvp_reserved_corridor_study_1826/manifest.json`：18文件SHA2ded01ab5062772e86d883d5af24ef5055b00395b8b2d7b1ee6434b059ac8ecc。仅上层槽几何/失败模型证据，不递归囊括独立low_speed_trial清单。
2. `hardware/dvp_rotated_group_placement_1835/manifest.json`：83文件SHAd272c878b88c7a5cb60d3c56ea2cdd28e6b1d5185f53bb63bdb1d9a77e965713。未选27实体旋转/去耦/偏置布置；PCB7d197c4db87e936bd26fc9bb6052036aaf42c3a0e3e92032eac445e4909a6ff1。**主动移除全部旧铜/填铜，严格0/274/0，仅名义placement检查**，不是电气后继/整板完成。normal/-O证明同102 ref/value/footprint/pad-net及源字节、27且仅27实体改位、courtyard零重叠；机械/去耦/电源/完整返回全重开。
3. `docs/electronics/dvp_topology_handoff_1852/manifest.json`：9文件SHA845fcc97fa636ab7daddfb5051059b467013ccd949653f5965d3c947e315b522。实际12网pin-order CSV/JSON、左右层分配图、分层端点交叉图、人工接手清单。图的虚线转角是连接关系示意，不是布线或孔位置。

## 停止条件与下一步

固定旧源区/统一右入口和新旋转局部扇出模型均按有界门停止，最多6条局部源端路径，没有12网全通。已识别同层口同起点、未先放全组via等人为规划限制；不能把模型失败说成当前板数学无解，也不能重复history协商加轮。所有临时局部PCB、编译程序、大型二进制搜索输入都未列为可制板交付。

下一步仅人工拓扑规划：D0–D3右F、D4–D7左In3、时钟同步右B是**未选对照**。左槽当前实际35个唯一旧铜对象阻挡，含3V3_AON/GND，不能盲删或细线救主供电。必须把源端全组扇出、偏置stub、12个头端共同交换、through-via跨AON反焊盘及地返回画清后再决定整板重布。正式9a03不动，旧2ad部分检查点保留。新旋转布局的0违规不能继承RF、主电源、IMU或原结构资格。

未完成：DVP12条完整布线和时序、J103实际压力装配/滤波联合接口、J104/J105系统功能闭合、全机械/电气复审、实物测试和总成本资格。没有采购、制板、上电、刷写或远端推送动作。
