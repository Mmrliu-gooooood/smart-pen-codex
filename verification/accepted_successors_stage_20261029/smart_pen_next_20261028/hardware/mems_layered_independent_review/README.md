# MEMS 分层规则独立复核

**结论：可作为 IRQ 后继的条件参考地规则合同；不是完整原厂布局/PI/机械/制造认证，仍 NOFAB。** 合并 IRQ 后必须重新填铜、完整 DRC/源/有限铜与参考地检查，不能相加两分支结果。本报告只本地冻结，无发布授权。

## 输入

`../mems_layered_rule_study/manifest.json` SHA `57699dacb2002f2af06b04af305912e596e73f720168d1f4e4dc538b37e73b3b` 的 82 项全部逐个复核。PCB完整SHA **`619a1307b7eb18c27d34f323e511726d95b373cca4e4dd2c11e284f03501eaf0`**。比较基线 `../j107_mode_port_closure/native/mainboard_revD.kicad_pcb`：`8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5`，沿用该源的限定独审，不复制整个历史包。

## 资料边界与准确口径

独立在线核对 [ST TN0018 Rev8 / March 2025](https://www.st.com/resource/en/technical_note/tn0018-surface-mounting-guidelines-for-mems-sensors-in-an-lga-package-stmicroelectronics.pdf)：§3.9 p14 图15限制同侧器件下走线/via，§3.10 图16允许适用传感器背侧走线/电源面；§3.2 p9同侧结构留空、§3.8 p13要求连接对称且地面不直接接焊盘。**§3.11 p15还举例要求 pin8 走线向外离开器件**。原项目的六层全面禁铜是保守扩展，不是文档明确六层禁铜要求。内层参考面许可是工程推论，不是原厂对本叠层/应力/噪声资格认可。

中央矩形是项目几何筛，不是 ST 指定尺寸。独查发现应修正候选 README“由实际pad内缘界定”的精确口径：x=3.425..4.575 mm确为侧排内缘；但 y=81.4125..82.5875 mm 相对实际端排pad内缘81.425/82.575 mm各向pad延伸 **12.5 µm**。实际pad允许标志为false禁止（即允许pad），因此不误禁正常pad；无需据此移动pad或修改冻结源。此差异已告知parent/作者，不能隐去。

外围共有9个F铜对象与body有正面积交叠，包括必要扇出和2条旧底排GND横连，全部逐件列于 `independent_normal.json`。它们均不侵入中央筛；**这不表示同侧body完全没有铜，也不自动满足§3.9/3.11**。两条横连人工符合性门继续开放，禁止把规则运行通过当完整原厂符合。

## 隔离重验结果

- 4757个track/via、102个封装：几何/源及原始序列块完全不变，避免KiCad加载修补网名掩盖变化。所有childsheet/库/pro/dru字节不变。
- 完整同basename工程与规则/条件叠层 preflight 通过；manufacturing模式明确拒绝。非MEMS规则全部轮廓/层/六项禁止标志不变。
- fresh KiCad9.0.2全量 **17违规 / 38未连 / parity0，exit5**，与基线完整finding multiset相同。不是整板通过。
- fresh fill逐zone-layer序列等于候选现填铜。实际有限宽度铜+填铜图显示全部旧网pad分量完全相同；AON 6岛和GND 4个实填岛均接其实际核心。
- In1 GND、In2 AON、In4 GND各增加4.000mm²；无铜移除，增加全部在2×2mm body内，无区外平面差量。
- F body禁pour/via，F中央禁track/via/pour、允许pads；现有必要扇出未出现新原生违规。全body普通通孔因经过F仍禁。
- 4类规则弱化/移位×normal/-O，共8次预期异常拒绝；另外原生加入中央F track、body中通孔，各正确产生命名keepout `items_not_allowed`，exit5。不是仅检查flag的“纸面规则”。
- 四组normal/-O报告一致。算法包含隔离重跑作者有限铜检查与独立raw对象/完整源闭包/freshfill/完整非MEMS规则/外围枚举；不是宣称两个独立几何内核。

## 复现

在本目录设置 XDG_CONFIG_HOME=/tmp/rf-independent/config、XDG_CACHE_HOME=/tmp/rf-independent/cache、XDG_DATA_HOME=/tmp/rf-independent/data，然后：

```sh
kicad-cli pcb drc --format json --exit-code-violations --all-track-errors --schematic-parity --severity-all -o drc.json native/mainboard_revD.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o fresh.xml native/mainboard_revD.kicad_sch
```

用 `/usr/bin/python3` 与 `-O` 运行 `check.py`、`config_and_drc.py`、`source_check.py`、`independent_extra.py`；`negative_tests.py` 生成隔离故障板并实际调用原生DRC；`final_checks.py` 核对等价和预期拒绝。保留负例摘要，临时guard板不入manifest；若重跑先复制审查目录，勿回写冻结包。

残留门：外围原厂符合性、焊接/应力/温漂与实测、完整信号/IRQ唤醒、PI/参考面资格、制造DFM、17违规/38未连均未关闭。JP301和充电commissioning保持OPEN、未知相机隔离。没有采购、通电或外部写入。
