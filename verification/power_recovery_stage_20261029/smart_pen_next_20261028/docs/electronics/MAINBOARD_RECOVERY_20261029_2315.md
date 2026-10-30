# 主板恢复索引｜2026-10-29 23:15 UTC

## 放行边界

正式接受的旧研究基线仍为 `j202_low_speed_reference_candidate`、PCB **9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038**、完整 **17违规/21未连/0parity**，且必须附原独审与两份VIO/参考投影勘误。它不是可制板成品。

下列新路线是为整组DVP与供电重排建立的独立研究分支。其最初移除了旧铜，因此不能拿新的“0违规”与旧板17/21直接比较而声称整板进步到完成。所有未连计数、供电/返回不足都必须保留。JP301保持OPEN，未知30Pin相机禁止直接上电；无采购、制板、刷写或实物验证。

## 19:00以后已冻结路线

1. `docs/electronics/dvp_analytic_topology_1933`、`dvp_joint_feasibility_1942`：解析整组12网两端拓扑；后者14项manifest **5042728ce459c68277eade07a70fb5cecaa038937d01c6a0f9d7327ee4ec9d22**。同102实体/24针，固定J103/J106，不把直槽容量当完整可路证明。
2. `hardware/dvp_joint_native_candidate_1950`：12链真实实例化，60线16孔，PCB **184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81**，69项manifest **98c8617fcd3c5341bd82cbde4db9012ad2cfa70e58377e33443249a8f628845e**。全0/262/0。独审 `dvp_joint_native_independent_review_1955` 清单 **4361184f854f7c43b3227b45b53e622b4dad774abecb2dfa2f5a87f2b218ab3c**。
3. `hardware/dvp_mechanical_clearance_successor_1957`：仅R206移至B(9,46)，J107原点移至B(3.2,84)，旧76铜不变；PCB **f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19**，78项manifest **3d7b7f7e2aa94ff436a1b90f4c3ca75650c20a6b4d7de29e7f26b698bc26f461**，0/262/0。保留完整安装预算后，两实体在四机械上下文无撞，名义间隙约0.603/0.45mm。机械独审在兄弟目录 `smart_pen_mechanics_dvp_two_ref_20261029_1958`，manifest **299032c7b306134d9cf92aeb76eb1f38dae74cfc772a5e4c28b4a3b9d79a180c**。RevD外台架R222顶圈碰撞与ACCESS虚拟B70.5/原生B52差异仍开放。
4. `docs/electronics/copper_recovery_plan_2005`：旧5317铜对象逐对象/子图比较，不允许全部旧铜无条件加回。
5. `hardware/complete_net_restore_candidate_2014`：精确恢复19完整网392原UUID铜，PCB **4d7bd85ae460928a48967c00adae133c05df5ef259a6789470c04e986b856f8a**，85项manifest **9dad722c58c1f91b8d7faa3475d9a62c9ba7c130af12b65aaca7b4fccac86b1b**，0/233/0。独审 `complete_net_restore_independent_review_2020`，清单 **d84e73386a422e568aef98b92cb5e7d180e2b8208ab87d986de14021eb8259ae**。
6. `docs/electronics/power_backbone_recovery_2124`：8个入口方案拒绝，只有局部桥/去耦几何筛可用，非完整供电；14项manifest **9085e1b441e5aa924c9a8d70ea024979ccc440e8396834fadcc39d7e9b1af5b9**。PAD.GetLayer导出的42条side值有误，必须配下条勘误；网/UUID/XY不变。
7. `docs/electronics/head_power_joint_plan_2129`：联合调整头部信号端部、供电/地入口；所有封装不动。29项manifest **0ad2b3831a6423c4381c425f2de4d7baed8e75e80fa7e68c7a5048d9dd077962**，附366实际pad层表和42条精确side勘误。判几何应使用IsOnLayer/GetLayerSet而非PAD.GetLayer。
8. `hardware/head_power_joint_native_candidate_2141`：保392旧对象+141联合对象，PCB **7e639fa62f08ba04dd5507f383e38ce1134877c5108e2527b855eb9b00b39115**，116项manifest **5ac49e42b4be0917c28ea8761afe98cc1bf064cc4cc6631761d0706674b2c8e4**，4/232/0；四悬端/单层孔不豁免。独审 `head_power_joint_independent_review_2149` 清单 **3071f65b0f02ff79570922855aae5f902c0073a3d66e9829993b5dcee6c0ac34**。
9. `hardware/power_zone_freshfill_candidate_2150`：同zone源真实重填，PCB **d64594c0ddfcddc7b8c3a40043fe56e144f25d4c59d2fa33e30a9595054c3de5**，77项manifest **349430e89df67b0ceee7a500c5698c37c7b5df14ff933ca8688e1de8b1c12151**，2/232/0。GND四区接核心，AON入口与zone相差0.10mm；不是供电完成。独审 `power_zone_freshfill_independent_review_2159` 清单 **c8cc269802625b7a7bc44fce8687d67d87bcd9a4dcff2c96425dbf51f446d0fa**。
10. `hardware/aon_entry_bridge_candidate_2156`：仅加0.5×0.9mm In2入口段，PCB **fd989bf844a8bc224f315dd3d2559d7a55ae1ba8f9384b0c06b6e301b6668454**，80项manifest **7fb911519bb3532f609d797852fdb8058d9f3a28094ce3c71642f9359a735c39**，0/231/0。AON1/39、GND2/102 physical pads接核心。独审 `aon_entry_bridge_independent_review_2159` 清单 **82bb6321cefc8b9e54deedf30e269059dff37a2fcb1ca786cb90de54b5199598**。

## 当前最后一个有界恢复块

`hardware/gnd_conservative_recovery_2305`，PCB **ead39fa832de2aabff4fbec9ce67d12199094ac9d77e700de54920d8fec86959**，清单见该目录 `manifest.json`。

- 从fd989精确恢复17个旧GND完整子图、96原UUID对象，原宽/孔不变。全 **0/203/0，exit5**。
- GND核心physical pads **2→30/102**，还72未连；AON仍 **1/39**，还38未连。12DVP、SW、局部地14链与19完整网保持。
- 原未冻结 `gnd_fixed_branch_candidate_2159` 的18组/110对象方案为拒绝比较，不接受其0/201/0作为较优结果。它使AON在0.25mm侵蚀下7片变8片。
- 18个整组移除+绑定project/rules的freshfill反事实证明，只有整组37（C207.2/U204.4，14对象，via3.9,66.6）撤回能恢复7片，因此整组不接回。不削线、不裁桥。
- 四个GND填充及原SENS参考投影不变，17孔对信号投影无交。AON仍因其他via反焊盘少8.796752166mm²，不能声称AON几何不变、载流合格或全部回流能力继承。
- normal/-O、17组断开反例、精确重放、真实删除96对象+freshfill退回fd989/0/231/0通过。该块待另行独立审查，不提升为正式整板基线。

## 恢复后不应重复的误判

1. 临时native必须同basename绑定原`.pro/.dru`；否则fill/DRC数字不可和原证据比较。2305首次未绑定临时比较明确拒绝并保留，不作结论。
2. fullDRC必须带`--all-track-errors`。旧16项误报来自漏参数，不是版本修复。
3. 不把0违规忽略203未连，不把内层plane恢复当SMT焊盘已接，不把0.25侵蚀片数当0.5mm实际载流通路保证。
4. 不用PAD.GetLayer推断实际SMT铜层。重复编号U101.57应按9个物理pad UUID分别统计。

下一步必须在新版本继续未接电源/地与功能网的机电联合设计；本次范围已止于保守旧GND复用。不重复全目录上传或覆盖冻结包。远端上传状态由父任务单独核实，本索引不宣称已推送。
