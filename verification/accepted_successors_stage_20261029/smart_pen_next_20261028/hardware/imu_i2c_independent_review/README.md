# 两条 IMU I²C 网限定独审

**接受最终6b44作为后继静态布局基线；不是I²C时序/唤醒/射频/完整产品/制造通过。NOFAB。** 不修改冻结源，不发布外部。

输入 `../imu_i2c_completed_candidate/manifest.json` SHA `2d160083077c53e1d2545e62e73b1fc99ebe59a40c1b38c85c2fc25e35171cbd`，115项逐个验证。当前 PCB **`6b44e149edf7e3b6c843375125a71247ece6c664eb531686dd3b451e1586ee71`**，基线已审IRQ `752f83d57fa15450862dcf1c3751041b49f9830fd2c541443d717c6e99d1b229`。未将旧781预版或128mm中间结果混作最终。

## 结果与实铜

- 隔离同basename工程 fresh KiCad9.0.2完整 **17违规 / 33未连 / parity0，exit5**；完整17项finding multiset不变。fresh ERC **0错误/1既有VBUS警告**，不豁免原违规。
- 102实体/356端点、10个原生MPN及全部原理图/库/pro/dru字节保持；全规则轮廓/层/禁止flags与基线完全相同。制造资格前置门仍拒绝。
- GPIO5/U101.10 → U501.1/R501.2，GPIO6/U101.11 → U501.4/R502.2，分别三端实际闭合，未共享/短接；两10k 1%上拉保留。只两I²C pad分量合并，全部旧pad不拆分，6个AON及4个GND真实填铜岛接原核心。
- 删除4旧track、新增302tracks+7vias，无既有器件/旧via移动。新增总线0.15mm与0.45/0.20mm通孔为既有条件规则override，不是DFM批准。
- 独立对两I²C及CAM_D0、CAM_D7、CAM_PWDN_UART_RX全网有限铜逐层检查异网正面积交叠：基线和最终均零；不是只核网名/中心线。
- 原始序列网身份检查、精确delta重放fresh-fill同SHA，独立对当前完整工程再填铜逐zone-layer一致。JP301 OPEN及物理隔离继承源/铜检查，充电commissioning未关闭。

## 改动高速网、参考面及RF边界

D0局部4.644975mm→4.644975mm、总24.830590mm不变；D7局部9.125→9.477082mm，总30.961449→31.313530mm；PWDN局部7.775→8.562006mm。所有DVP源与pad保留；改动局部无新增参考投影缺口，D7既有约0.89mm缺口保留。完整D0–D7/PCLK/HREF/VSYNC/XCLK统计见 `measurements.json`。长度差不作为任意硬等长标准，也不是时序通过。

未改F/In3/B旧track新丢失参考投影筛未发现超过 **1e-8mm²** 的面积，非数学精确零或EM资格。In1/In4新反焊盘各约3.083734mm²，In2约2.709544mm²；面积小不是安全证据。

最终顶部SDA via确在 **(5.20,1.35)mm**；新In1空洞距实际RF线/pad **0.376670mm**、距时钟2.448602mm，无投影交叠/六层RF区域侵入。通过的是 **0.35mm项目敏感区筛**，不是50Ω/天线/边缘场/射频实测资格。

AON狭条反事实仅从两个MCU总线孔周围In2填铜删除额外0.514514mm²（清空半径0.375→0.55mm）；不加任何导体，全部旧AON pad关系仍保持。说明约0.0745mm边缘条不是必要连通颈，**不证明其他通路截面、电流密度、温升或整板PI**。这是内存实填多边形反事实，不是实际候选变更/制造版。

## 总线、MEMS及功能门

最终SCL **88.336048mm /92tracks/2vias**，SDA **130.156340mm /197tracks/5vias**；合计136个<0.1mm短段，不能称优雅量产布局。连续同层参考中心线最大缺口0.406774mm（采样≤0.005mm、边界不确定度0.010mm），换层最近地via最远约4.19mm，仍保留返回/EMI门。

最终pin1/pin4 F外逃落在明确左向接近带或原生pad内，带外面积0；中央禁穿越/全body禁通孔与pour保持。这是项目几何筛，不是ST精确免审尺寸。端排12.5µm pad重叠勘误与旧外围GND横连人工符合性门继续保留，见此前MEMS独审。

10k上拉、总线电容/上升时间/恢复、固件IRQ模式与首笔唤醒仍待实测；100kHz是待测起点，不保证400kHz。静态IMU各信号连接闭合不等于器件已工作。未知相机不得接电，充电/回灌/热、机械、成本与17违规/33未连等仍未完成。

## 复现与证据

先复制本目录到隔离副本再重跑，勿回写冻结。`run_native_checks.py`执行同basename源导出、ERC、preflight及完整DRC；原生命令/退出码见 `native_command_results.json`。完整DRC参数：

```sh
kicad-cli pcb drc --all-track-errors --schematic-parity --severity-all --exit-code-violations --format json -o REPORT native/mainboard_revD.kicad_pcb
```

normal/-O运行 `verify.py`、`compare_drc.py`、`measure.py`、`continuous_reference.py`、`via_plane_screen.py`、`return_plane_delta.py`、`aon_neck_counterfactual.py`、`mems_approach_screen.py`、`extra_checks.py`，9组输出等价。`negative_tests.py`5类×2按精确错误类别拒绝，`replay.py --output NEW-EMPTY-DIR`精确重放；`final_checks.py`显式检查所有结果及几何门。

算法为作者工具隔离重跑加独立全源/规则/freshfill/实际pin与拉阻/两总线及改动三网全有限铜检查，不宣称两个完全独立几何内核。历史依赖仅引用稳定目录，未复制移动trial。冻结汇总见manifest。
