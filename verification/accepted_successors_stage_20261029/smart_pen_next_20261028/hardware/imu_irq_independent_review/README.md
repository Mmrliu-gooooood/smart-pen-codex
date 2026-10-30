# IRQ + MEMS 真实合并板限定独立复核

**接受作为后继有限布局研究的静态基线，NOFAB；不是 IRQ 唤醒功能/完整 IMU/PI/制造或安全通过。** 本报告不修改冻结源，不发布外部。

输入 `../imu_irq_layered_candidate/manifest.json`：`723aafa5f6f80f25f4d7406150defeb074f3932f80a033c5e9e6405de4e01d6f`，115项逐个SHA复核。当前 PCB **`752f83d57fa15450862dcf1c3751041b49f9830fd2c541443d717c6e99d1b229`**。铜比较基线为 J107 的 `8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5`；MEMS规则逐项比较已独审 `../mems_layered_rule_study`，不叠加分支报告替代合并检查。

## 独立复现

- 同 basename native pro/dru/条件六层叠层 preflight 正确；fresh KiCad9.0.2完整 **17违规 / 37未连 / parity0，exit5**，17项完整finding multiset与J107完全相同。fresh ERC **0错误 / 1既有VBUS_5V global-label警告**。制造前置门仍明确拒绝。
- 全部102实体、356源端点、原生MPN和所有源/库/工程字节保持。真实 GPIO1=U101.6 到 INT1=U501.12；仅IRQ pad分量合并。所有旧pad分量不拆分，BOOT pad完整保持；AON6岛/GND4岛均经有限宽度铜和真实填铜接核心。
- 确认delta仅BOOT局部出口和IRQ及声明MEMS规则；原始网名序列检查防加载修补掩盖异常。独立对整个IRQ/BOOT实际铜逐层检查异网正面积交叠，均零。该检查不免除仍存全板违规。
- 精确delta重放与独立fresh fill都得到同一完整PCB SHA，并再次通过有限铜检查。所有MEMS/RF规则轮廓、层、pad/track/via/pour/footprint禁止标志与已审规则合同一致。
- IRQ **118.169488mm / 86段 / 3via**，28段小于0.1mm。参考链声明逐段与实际native nm几何对齐，补全MCU额外2段F扇出和1个via，未把117.439382mm长段当全网。
- IRQ/BOOT小孔为0.45/0.20mm，理论环宽0.125mm；同名规则未弱化，仍Default0.15mm线宽与间距。仅是既有条件工艺override，不是制造商钻孔/叠层DFM批准。

## 参考地与MEMS边界

连续同层参考缺口重算 **0.383607mm**，采样步长≤0.005mm，边界采样不确定度0.010mm；F参考In1、In3/B参考In4。三个换层点最近GND via中心距约 **2.7045 / 0.6915 / 2.9532mm**。这不是回流电流/电感仿真；长IRQ、换层返回与EMI门继续开放。

新F pin12连接与body交叠0.042863mm²，其中pad之外0.007569mm²；实际完全在声明的向外接近带内，中央禁穿越区零侵入。接近带为项目解释，不是原厂免审尺寸。中央筛端排12.5µm pad重叠勘误、旧外围GND横连人工符合性门均保留；沿用 `../mems_layered_independent_review` 资料边界，不重称全部同侧无铜或六层原厂资格。

JP301 OPEN与两侧物理隔离保持，充电commissioning仍开路。`PICKUP_INT_N`名字不证明实际极性；固件输出模式/偏置/唤醒配置、掉电域、丢首笔必须验证。I²C两网仍各3个独立pad，合计4项未连；不能称完整IMU接口闭合。未知相机、充电安全、全板17违规/37未连、机械、制造与成本门仍未关闭。

## 证据与重跑

复制本目录到隔离副本再执行，勿回写冻结目录。依赖按既有manifest引用，未复制移动trial。

```sh
/usr/bin/python3 pcb_preflight.py native/mainboard_revD.kicad_pcb --lock preflight_lock.json --report preflight.json --run-drc
# 上项完整命令为 kicad-cli pcb drc --all-track-errors --schematic-parity --severity-all --exit-code-violations --format json；预期 exit5。
kicad-cli sch export netlist --format kicadxml -o fresh.xml native/mainboard_revD.kicad_sch
kicad-cli sch erc --format json --severity-all --exit-code-violations -o erc.json native/mainboard_revD.kicad_sch
```

`verify.py`、`compare_drc.py`、`reference_and_lengths.py`、`continuous_return_screen.py`、`extra_checks.py` normal/-O五组报告等价。5类×2故意错误（旧AON网身份、IRQ网身份、IRQ缩宽、BOOT钻孔、MEMS禁via弱化）全部以预期异常拒绝。`replay_and_refill.py`锁定精确重放；`final_checks.py`显式异常门验证等价、故障、pin12接近及制造拒绝。

本复核为作者几何算法隔离重跑加独立源闭包/规则全标志/参考链原生覆盖/全IRQ与BOOT异网有限铜/ERC检查，不声称两套完全独立几何内核或电磁资格。
