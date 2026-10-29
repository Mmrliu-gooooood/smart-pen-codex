# 条件 RF 馈线候选 — 仅几何/连通证据，NOFAB

**不能据此生产整笔或声称射频通过。** 本目录不含射频实测、制造商下单确认或购买授权。

## 结果与身份

- 唯一候选：`mainboard_revD.kicad_pcb`，SHA256 `b39eb6319473eb29e7cc7644769d17bb64c872602a6cae6a041148aad75ef52d`。
- 基线：`source_before.kicad_pcb`，SHA256 `af7ea5488de178176dded49c9130ccca6c76334c7df96e80d869338406449714`，来自已冻结 `hardware/obsolete_track_cleanup`；未更改该源。
- 板外形仍 **12 × 101.5 mm**，没有向左/右扩宽；与数字团队其他宽度分支不可默认混合。
- ERC **0**；完整带 schematic-parity 的 DRC：**几何违规 0、未连 1（继承 USB_EN1）、缺封装 13（继承）**。退出码 **5** 正确保留；不能称整板 DRC 全通过。
- 实际全部焊盘连通分量：仅 RF_SIP、RF_ANT 从分离变连通，其他网络全部保持基线分量；GPIO45/46、CAM_SDA、电源与地未被断开。
- 独立的有限铜多边形检查：77 个 GND 焊盘形状为同一分量，六层天线净空中没有其他铜；不是只看飞线。
- 普通 Python 与 `-O` 的全网络和有限铜检查输出相同。上述是作者检查，不能冒称独立审查结果。

## 真实改动

精确 UUID、修改前后坐标/层/线宽都在 `all_net_audit.json`，`build_rf.py` 是可复现构建逻辑，不是对正在运行的其他候选直接写入的脚本。

1. R104 保留 **10k、F 面**，移到 `(3.5, 1.7)`，方向 0°。GPIO45 从新焊盘短接原 MCU 端路径；不用旧背面回折和两处不再必要的绑带过孔。GND 从新右焊盘接真实地过孔 `(4.1,1)`。没有翻到 B 面。
2. R105 不移动、不改值。保留 `R105.2 → (5.1,4) → (4.35,4.75) → (3,4.75) → (3,4.65) → GND via(2.8,4.45)` 的主回地。裁除该地过孔与地过孔 `(4.1,1)` 间冗长的顶层桥，**不是谎称原桥悬空**；通过真实地平面、全部 pad 分量和有限铜图验证回地仍闭合。
3. 裁除 R104 移位后失效的旧地分支，但保留 C103 地焊盘 `(1.05,6.25)` 到地 via `(1.05,5.3)` 的去耦回流。PICO 和所有供电去耦器件位置/焊盘不变。
4. CAM_SDA 低速信号过孔从 `(2.3,5.05)` 改到 `(2.65,5.25)`，只同步修改其 B.Cu、In2.Cu 两段端点；其余摄像头线不动。此举为 RF 的实际参考地避空让出余量，不是任意改网络。
5. C106/C107 改为 KiCad `Capacitor_SMD:C_0402_1005Metric` 条件封装，保持原 DNP、待调值、引脚网络和原理图实例对应。坐标分别 `(6.65,1.38)`、`(9.5,1.38)`，270°；RF 焊盘 y=0.9，GND 焊盘 y=1.86。L101 到 `(8.05,0.9)`，方向 0°，待选待调。
6. C106 地用新 **0.6/0.3 mm** 通孔 `(7.6,2.1)`；C107 地接已有 `(9.275,3)` 地通孔。所有层检查无新增通孔短路/间距问题。
7. 移除旧左端匹配区的 F.Cu 地覆铜；它不再服务移位后的电容，也不能让“非共面”模型线旁意外紧贴大片共面地。In1 地平面在天线入口延到 y=0，天线净空仍不得覆铜。

## 馈线、匹配和净空：不要把条件数字说成实测

依据官方公共模板 `JLC06081H-2116` 的条件计算：L1→L2 微带宽 **0.1814 mm**；另一备选 CPWG 是 **0.1707 mm / 地隙 0.2 mm**。本候选用前者，**没有把后者参数混用**。输入合同在 `stackup_contract_snapshot.json`；厂家尚未选定，订单叠层、材料/Dk、蚀刻公差、阻焊、阻抗券均未确认。CAD 原有 0.8 mm 厚度属性不是已批准的实际叠层；模板成品标称约 0.83±0.10 mm。制造前必须在最终集成工程落实完整叠层合同。

- RF 源端至 C106 的路径点、实际长度见 `route_proposal.json`；无 RF 换层/过孔。
- 匹配区位于 y>0 的有参考地区，不能把左侧匹配直接横穿 6.5 mm 辐射净空。
- **终端**仅沿 x=9.5 从 y=0 接到 AE101.1 的 y=−1.9：这是本候选的 **1.9 mm 无地过渡**，不是 50 Ω 微带，也不是 Johanson 官方规定的该长度。其图上的 1.9 mm 标注属于参考匹配区尺寸，不能偷换含义。
- 原生 all-layer 规则持续禁止整个 `x5.5..12,y−6.5..0` 区域中的覆铜、过孔；第二条带窄槽的规则禁止其余走线。窄槽只为这段 F.Cu RF_ANT 终端。有限铜检查额外禁止任何其他网络/焊盘侵入，不能把 CAD 窄槽当任意布线许可。
- AE101.2 仍为原理图 **NC 机械焊接端**，不是地。Johanson 2450AT18A0100001E Rev4 原生研究封装和角落净空不变。
- 实际填充 In1 铜覆盖所有有参考段的有限线宽（y=0 端帽的负 y 半圆计入终端过渡）。`reference_screen.json` 给逐段证据。额外 0.35 mm（约 3×0.1164 mm）侧向地包络是**本项目筛查假设**，非官方强制阈值；源端局部仍有微小包络缺口，天线入口包络必然进入无地区。
- `coplanar_proximity.json` 记录源端 C103/其地过孔附近约 0.31–0.325 mm 的同层地接近。**器件焊盘、源端逃线、匹配区及天线入口是非均匀过渡；不能声称整条线路已经严格 50 Ω。** 必须做电磁/厂商复核及 VNA/装壳调试。
- 当前外部网络仍是原设计的 π 占位，不是假装复制 Johanson 的 tee 参考网络。未照搬其评估板元件值；若厂家调试要求 tee，应先修改源图及布局再复核。当前待调/DNP 状态不等于射频硬件已经可工作。

## 检查和复现

使用 KiCad 9、`/usr/bin/python3` 的 pcbnew，以及本目录 `tools/`。源身份在构建前显式检查。

```sh
export XDG_CONFIG_HOME=/tmp/pen-rf-check/config
export XDG_CACHE_HOME=/tmp/pen-rf-check/cache
export XDG_DATA_HOME=/tmp/pen-rf-check/data
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints
kicad-cli pcb drc --format json --schematic-parity --exit-code-violations -o /tmp/rf-drc.json mainboard_revD.kicad_pcb
/usr/bin/python3 audit_all_nets.py
/usr/bin/python3 check_finite_copper.py
/usr/bin/python3 check_rf_reference.py
/usr/bin/python3 check_coplanar_proximity.py
```

`build_rf.py` 只应复制到新研究目录后运行；它会生成新 UUID 和暂存板，不能用来覆盖本冻结交付。审查/合并应使用冻结 PCB 和明确差量，复核目标分支的全图、全部铜及实际板壳截面，而非只套检查计数。

拒绝过的方案：12 mm 板边 x≈0.25 的无足够返回地绕行；R104 原位翻 B 与 CAM_SDA 冲突；0603 匹配与原数字区碰撞；没有完整参考地的横穿天线净空。这些不是本目录的交付 PCB。

## 制造/产品仍待完成

- 合并其他主板修改后，完整 ERC/DRC/一致性与实际铜再查；EN1 和13个缺封装不能被此分支掩盖。
- 具体 RF 元件料号、0402额定/公差与可焊性、匹配拓扑、采购报价和单笔380元完整BOM仍未批准。
- 最终天线与电池、手握、笔夹/金属、线束、壳体材料和组装偏差一起测试；不能因净空二维合格就声称18mm外壳/射频合格。
- 去嵌/校准夹具、VNA S11、匹配调谐、BLE 全频段包错率/吞吐/距离、充电/书写时噪声及真实握姿测试；不伪造结果。
- 没有采购、上传、无线发射测试或制造放行。

## 一手资料

- [Johanson Rev4 数据表，尤其第2–3页](https://www.johansontechnology.com/docs/3827/Antenna-2450AT18A0100001E-Rev4.0.pdf)
- [JLCPCB 官方阻抗计算器](https://jlcpcb.com/pcb-impedance-calculator)；完整取证见仓库 `docs/research/stackup_qualification/`。
- [Espressif ESP32-S3 PCB RF指导](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#rf)
- [ESP32-S3-PICO-1数据表](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf)：SiP内部已有匹配，不能无辨别复制裸片匹配/开路stub。
