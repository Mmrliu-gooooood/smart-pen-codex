# IMU 紧凑去耦后继 — NOFAB，PI 尚未资格

## 本轮落实
基线为 `mainboard_input_imu_power_routing` 的 PCB **405920aa…93eea7a**。保持 J106 输入 0.50 mm 主干、U501 位置、JP201/JP202、全部其他系统功能不变；没有扩大板或改变 RF 线宽。

|Ref|实际新位置/方向|源与实体|
|---|---|---|
|C501|F (6.2,80.7)，0°|100 nF，KEMET C0402C104K4RACTU，0402|
|C502|F (6.2,82)，0°|同上|
|C503|F (5.3,84.5)，0°|10 µF，KEMET C0805C106K8RACTU，0805|
|R501|F (2.6,86.5)，0°|原 10 kΩ 上拉，值/封装不变|

R502 保持原位。只替换这两颗 100 nF 的封装/高度，不能推广到其他电容。完整源绑定 `imu_decoupling_0402_source_fix`，manifest `92e8f68b5bba70b8a8e8d7c84ebc765cd6b61a98c93f4311484f5e14eb4c21cf`。原 1 µF 不再作为本候选生产用量。

去除上轮 36 项 IMU 局部铜并重布；额外移除旧局部 AON 三段线/两颗 via，腾出真实去耦回流空间。它们不是整机输入主干。精确删除 UUID 见 `placement_delta.json`，新增铜见 `new_local_routes.json`。不是把旧铜暂时断开后假称闭合：最终全 pad 有限铜图证明原连接集合未拆散。

## 完整验证结果
- KiCad 9.0.2，`--all-track-errors --severity-all --schematic-parity --exit-code-violations`：**135 违规、58 未连、parity 0，退出 5**。对应基线相同模式为 136/58/0；不要混用旧默认枚举的 124。
- 与基线完整违规集合比较：**新增 0、消除 1**。新铜/新位置器件没有违规。既有 135 项仍然禁止投板/接电。
- Fresh 原生源 102 实体 / 356 端点；ERC 0 错误，仅继承 VBUS_5V 边界警告。
- 正常与 Python `-O` 的 `audit_compact.py` 结果一致：逐源值、封装、完整 symbol 路径及每个真实 pad 网名一致；所有原先相连 pad 集合保持。AON 尚 3 个分量（核心、U301、C301），GND 尚 17，不能说整板供电全部完成。
- 六层实际 pad/track 多边形、扣孔 via 环和各个填充铜岛以正面积交集连接，不以同名网络代替真实铜。MEMS 区六层填充平面/via 的精确多边形侵入为 0。
- 7 类负例分别在正常/优化模式拒绝：原始文件错铜网、删除输入 via、改旧线宽、改 C501 pad 网、MEMS 平面侵入、删除 MEMS 规则、关闭 JP301。负例文件单独隔离，不是候选。
- `pcb_preflight.py` 绑定同 basename 工程/规则、netclass、六层和 CLI 版本，DRC 前后配置及 PCB 不变；完整命令与退出码见 `preflight.json`。

## 实际回路几何改善，不是 HF/PI 证明
逐 UUID 原生量测（只计线中心，不计 pad 内、via 或平面阻抗）：

|路径|本版|上轮独审|
|---|---:|---:|
|C501 → VDD_IO|1.185 mm，0.20 mm 宽|1.967 mm，0.15 mm|
|C502 → VDD|1.061 mm，0.20 mm 宽|1.360 mm，0.15 mm|
|各 100 nF → 本地 GND via|各 0.780 mm，0.25 mm|0.762 / 1.510 mm|
|两去耦地 via 至芯片地 via 的平面直线分离|均 2.405 mm|5.263 / 4.182 mm|
|U501.8 → 芯片地 via|2.053 mm|1.995 mm|
|10 µF → 芯片地 via|1.128 mm|不作等值比较|

本地 AON spine 改 0.30 mm，不再用 0.15 mm 共享供电颈。芯片地仅 LGA pad 逃线 0.3375 mm 使用 0.15 mm，后续主段 0.25 mm。两 100 nF 共享一个 **0.45/0.20 mm** 小信号地 via；其他新 via **0.60/0.30 mm**。均非盲埋孔；小孔工艺/成本仍须厂商确认。

地 via 间直线距离不是平面电流真实路径或回路电感。芯片地中心线并未缩短，改进是去耦与芯片地的相对集中及局部导体加宽，不能宣称瞬态/噪声已通过。需实物电源波形、启动、I²C/MEMS 测试。

## 器件、机械和叠层边界

- 原厂当前 KEMET 资料：`docs/electronics/imu_0402_decoupling_candidate` 和 `docs/electronics/imu_decoupling_correction`。0402 的 3.3–3.6 V 偏压曲线仅典型约 −4%～−6%；0805 10 µF 在 3.3 V 典型约 8 µF，在 3.6 V 约 7.5–7.7 µF，未叠公差/温漂/老化，不保证有效 ≥10 µF。
- 0402 原生焊盘 0.56×0.62 mm、中心距 0.96 mm。按原厂端接范围作居中尺寸相交筛选，最小纵向覆盖约 0.20 mm；不是贴装误差/钢网/回流资格。见 `land_dimension_screen.json`。
- 机器机械合同：C501/502 最大本体 1.05×0.55×0.55 mm，加 0.15 mm 焊料后高 0.70；C503 最大本体 2.2×1.45×1.45，加焊料高 1.60。其余高度不降，真实联合机械复核待独立报告。
- 显式候选叠层 JLC06081H-2116：nominal 0.83 mm，机械上界 0.93，中心介质 0.2028。未选定制造商/报价；KiCad 保存填入的 Dk 4.5/loss .02 是未资格默认值，不用于阻抗计算。`preflight.json` 同时保存 raw stack 与已知几何 hash。
- JP301 继续 OPEN，未授权相机/电池接电、采购或制造。其他 58 未连、旧违规、完整头部/线束与射频/USB/热/安全资格仍未结束。

## 重现

按顺序运行 `build.py`、`route_local.py`、`bind_final_source.py`，随后 fresh export/ERC、带标准全枚举选项的 DRC、`audit_compact.py`、`measure_local.py`、`negative_tests.py`、规则 preflight。`build.py` 使用按 UUID 精确删除原生块，不循环对已删除 SWIG 对象操作；曾遇到 SWIG 句柄失效的早期占位尝试未被作为结果。源 0402 绑定必须执行，不能拿中间 parity 非零版发布。
