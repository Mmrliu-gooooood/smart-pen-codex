# MEMS 分层规则研究：修正项目过严规则，不是厂家布局认证

**NOFAB。** 基线为已限定独审 J107 板 `8aa2581b…05ab5`。此研究没有移动元件、焊盘、track 或 via，没有更改源/BOM/netclass/线宽/钻孔规则；仅版本化 MEMS 局部规则及其真实重填铜。旧冻结全保留。

## 原厂依据与项目解释

[ST TN0018 Rev.8，2025-03，§3.9/3.10，p14 图15/16](https://www.st.com/resource/en/technical_note/tn0018-surface-mounting-guidelines-for-mems-sensors-in-an-lga-package-stmicroelectronics.pdf)：同侧器件下应留空，不穿越走线/via；加速度计背侧可以有信号/电源平面。已下载并实际查看p14图示。§3.2 p9 的同侧结构留空和 §3.8 p13 的地经普通走线接焊盘指导也纳入边界。

旧项目把2×2 body矩形扩成**六层无plane/via**，这是自定保守项，不能称原厂要求所有层空白。允许内层参考铜是对“同侧限制”的工程解释，并非此文提供六层叠层/应力认证；机械/焊接/温漂与噪声仍需实证。

## 规则实际分层

1. body矩形 PCB x3..5、y81..83：F.Cu 禁止pour和via；普通通孔经过F因此仍禁止。保留必要外围焊盘逃线，不把包含实际焊盘的整块矩形设成不可实现的全routing禁区。
2. 中央区域 x3.425..4.575、y81.4125..82.5875（由实际焊盘内缘界定）：新增F.Cu禁止穿越routing/via/pour的可执行规则；允许原生焊盘本身。其范围是**项目几何筛**，不是ST提供的精确禁布尺寸。
3. 移除旧全层plane禁止，内层GND/AON按原有zone边界/间距重新填充。RF规则完全不变；没有凭此改变信号网工艺约束。
4. 两条旧底排GND相邻pad边缘连接保持，单独人工审查门仍开放。它们不在中央穿越区，不能由此宣称满足所有同侧装配建议；也未无证据地称它们为安全短路或盲删地回路。

初次添加中央zone时 KiCad默认禁止pad，造成4条错误pad禁入报告；该实现被拒绝，现显式 `SetDoNotAllowPads(False)`，保留 `rejected_implicit_pad_prohibition.json` 作为反例，未拿误报逼正常pad改位。

## 有限几何与原生检查

- 4757个track/via和102个封装逐项不变，所有原生childsheet/pro/dru不变；所有网络实际pad分量完全相同。
- fresh full DRC **17 / 38 / 0**，退出5；17项完整违规multiset与基线相同，绝非整板通过。
- In1主GND、In2 AON、In4主GND各恢复4.000mm²铜；其余两区不变。AON仍6岛、GND四个实填岛均有真实有限铜路径到核心，不仅同名网络。
- F body实际pour/via和F中央穿越track检查为零。外围pad扇出/边缘连接另列，未混入“中央零侵入”结论。
- 固定same-basename工程、原始六层叠层与规则SHA进行routing preflight；manufacturing资格明确拒绝。
- 普通/优化Python全铜与配置审查；4类规则弱化/移位×2模式拒绝，另实际插入中央F track/器件下through-via，native DRC明确报keepout禁入。

## 边界与下一步

这是独立规则基线候选，尚未与移动中的IRQ/I²C路由合并。合并后必须重新填铜、全量DRC/实际连通和参考地评估，不能把本包结果与另一分支相加当整板通过。恢复参考面可能改善IRQ末端的参考缺口，但没有声称阻抗/EMI/机械应力已合格。

JP301/充电commissioning保持OPEN、未知相机隔离。真实线束、MEMS应力/焊接、温漂、IRQ唤醒、I²C上升时间、供电PI和全板剩17违规/38未连仍是开放门。没有采购/发布/通电动作。
