# LIS2DW12 本地去耦修复依据（候选，NOFAB）

2026-10-29。4059 输入/IMU 供电块仅获几何和连通限定审查，不构成电源完整性资格。原 pickup `tools/build.py` 将 C3 硬编码为 1u X7R，迁主板成为 C503；未找到偏离原厂建议的工程证明。旧 pickup 板不得作为当前可投板推荐。

## 原厂依据

- [ST DS11811](https://www.st.com/resource/en/datasheet/lis2dw12.pdf) Rev 9 §4 p19：VDD pin 9 附近 100 nF + 10 µF；VDDIO 独立 100 nF。
- [ST 官方评估板 BOM](https://www.st.com/resource/en/bill_of_materials/steval-mki179v1_bom.pdf) 的 C2 为 10 µF / 0805，Farnell 2118132；[评估板电路](https://www.st.com/resource/en/data_brief/steval-mki179v1.pdf) 对应本地 VDD bulk。
- [ST 技术版主 2024-11-22](https://community.st.com/mems-sensors-48/lis2dw12-accel-schematic-review-142734) 明确答复同型号可以采用陶瓷，不必为文字中的 aluminum 强塞铝电解。
- [精确候选官方规格](https://yageogroup.com/component-documentation/download/specsheet/C0805C106K8RACTU?lang=en)：KEMET C0805C106K8RACTU（别名 C0805C106K8RAC7800），10 µF ±10%，10 V，X7R，0805；当前官方 L=2±.2、W=1.25±.2、T=1.25±.20 mm。机械采用本体上界 2.2×1.45×1.45 mm，再加明示焊料/安装高度 .15 mm；不能沿用旧 2017 表的 1.40 mm 厚度上界。

## 不能用远处电容替代的现状

4059 原生 pad 到 U501.9 的欧氏距离下界（不是铜长/阻抗）：C102 22 µF 为 63.752 mm；C301 10 µF 为 18.797 mm 且当前仍在隔离 AON 铜分量；C503 1 µF 为 4.024 mm。没有共享 bulk 的充分依据。

独审实际铜还发现芯片地回到共享 via 约 2 mm，去耦地 via 与芯片地 via 平面直线分开约 4.18/5.26 mm，以及共享 .15 mm 颈。低直流电流不能证明高频回路合格。后继同时调整局部 C501/C502/C503、供电及地 via，不仅改标称数值。

## 尚未关闭

官方精确料号页面提示无 simulation data，但实际 PDF 图像另有曲线（见下节）；规格表的 10 µF 为 1 kHz、1 Vrms 测量，并非 3.3 V 偏压后的保证。X7R 温漂、±10% 初始公差和每十倍时间 3% 老化与 DC bias 不能混为一个已知减额。曲线不是规格，尚无有效容量最低保证，不能写“运行时至少 10 µF”。当前只将该 MPN 作为有官方评估板先例的原生占位候选；取得偏压曲线/实测并核启动、噪声与温度后才可关闭。未采购、未修改旧冻结源。

## 00:32 UTC 新取得原厂 PDF 图像证据（修正上面的“尚无曲线”）

网页正文虽提示无 simulation data，实际下载的同料号原厂 PDF 第 2 页含 **Capacitance Change vs. DC Voltage Bias** 图。已保存原始 PDF 与渲染页 `official_page2.png`，不能仅依网页抽取文字断言没有曲线。图示在 3.3 V 约 −18% 到 −20%，3.6 V 约 −23% 到 −25%（视觉读数，只保留约数）；对应标称 10 µF 的典型值约 8 µF、7.5–7.7 µF。不是最低保证，也未叠加初始公差、温度及老化。原厂第 4 页明确图为典型模拟，不是规格保证。

因此已有偏压效应的典型证据，可据此开展 source/BOM/布局候选，而不是拒绝一切布局；但不能声称偏压后至少 10 µF。原厂 eval 采用该名义容量/封装与官方答复支持这条路线，最终仍需本地供电瞬态、噪声/唤醒实测或厂家书面最低界限。不要另行自动升为 22 µF 以制造虚假“保证10 µF”，那会改变尺寸、启动与供电负载。
