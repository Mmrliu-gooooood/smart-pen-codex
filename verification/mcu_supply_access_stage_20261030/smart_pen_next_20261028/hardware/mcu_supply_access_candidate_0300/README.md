# MCU VDD3P3 局部接入原生研究候选 — 0300

**NOFAB / NOPOWER。仅可检查研究版，不是制板或上电批准。**

## 来源与最小变更

- 输入 `hardware/gate_power_candidate_0228/native/mainboard_revD.kicad_pcb`：SHA256 `66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141`，0/137/0。
- 严格执行已冻结 `docs/electronics/mcu_supply_access_study_0242` 的28文件提案（manifest `596bc4a249bec1d935ebc66690e262c74ac3b250a8b9db690c942e6066e8b41a`）。
- C103 F由(1.2,7.025)移至(.8,7.025)，90°不变；R503 B由(2.5,7.5)移至(2.5,11.5)，0°不变。其他100个FP不变。
- 780旧铜对象全部保留，按提案精确添加7线+2颗.60/.30mm通孔，共789；未改EN/BOOT/RF/连接器；原理图、project、规则原字节不变；没有豁免。
- R503=100k压力接点上拉，两端AON/NIB_CONTACT_N原来均孤立，移位没有断开旧连通，但本轮也未完成这两个网络的剩余接入。
- 原生输出SHA256 `8fe809b685633dd86dddc36ec33961d61ef7fad9fca52286bc47bd72a4f614e5`。

## 实测工具结果（非硬件实测）

两次真实KiCad fresh-fill幂等；独立从源重放字节完全相同。完整 `--all-track-errors --schematic-parity --severity-all`：**0 violations /134 unconnected /0 parity**。尚有134未连，绝非整板完成。

`verification.json`：所有旧物理pad连通分量保持；九个同号U101.57地pad以UUID分开计数。AON核心25→28/39，增加U101.2、U101.3、C103.1；GND61/102，SENS12/12不变。normal及python -O结果一致。有限铜模型用真实六层、环铜扣除孔，并对zone执行一次有保护的Unfracture及扣除所有真实通孔，不以centerline/同号pad合并假设代替物理连通。

`physical.json`：新铜对全部旧铜/实际各层pad、异网.15mm、同网via-pad排除、.25mm钻孔间距、.25mm板边、实际禁布区检查无新增冲突。**这不涵盖制造公差/焊接工艺资格**。

`plan_and_planes.json`：精确9对象与提案逐项比对；源宽长/通孔统计。实际refill后In1/In4主地各减少1.220222845666mm²；AON fill原生polygon没有自动挖同网钻孔，物理扣孔后减少.133615691533mm²。所有有保护展开并扣孔的plane在.25mm侵蚀后各保持一个连通体。旧F→In1、B→In4、In3→In2/In4信号参考投影无新增损失。不是阻抗/IR-drop/瞬态电流资格。

## 原生反事实与回退

每个例都真实保存、fresh-fill、full DRC、物理组件检查（`native_negative.py`）。这些板只用于测试，禁止误当候选发送生产。

|独立变更|DRC/未连/parity|物理结果|
|---|---|---|
|删U101.2短逃线|0/135/0|pin2脱离AON core|
|删U101.3短逃线|0/135/0|pin3脱离AON core|
|删两供电通孔|1/135/0|U101.2/.3/C103.1一同脱离AON core；唯一warning为遗留stub的track_dangling|
|删新增C103 GND补强|0/134/0|C103.2仍接地：旧stub仍接触移位pad，不能把新尾巴称为唯一回流|
|删9对象、恢复两FP原位|0/137/0|整板SHA精确恢复66d534输入|

工具异常记录保留：最初SWIG `Board.Remove`循环发生段错误，改为按UUID删除完整native对象块；随后首次负例断言错误地要求删除双via后零warning，实为预期dangling，已以明确类型校验修正。原失败脚本/日志保留；不是原生候选DRC冲突。重复多板SWIG生命周期在-O复跑又发生段错误，现将每个反事实fill隔离到独立进程，保留该异常日志并重新运行normal/-O。

## 仍未关闭的硬门

1. 新via5与U101/C103 F courtyard分别交叠.0287694271705/.0040350770455mm²；via8与C103交叠.011259537403mm²。实际pad铜不相交不能替代封装底面、阻焊、钢网、工艺容差审查。完整DRC不报告这些不代表该门关闭，**未设置任何豁免**。
2. .4mm pitch下的.25mm短逃线总路径pin2=.775mm、pin3=.975mm，低于Espressif通用20mil支路建议；.635mm合流约2.170824mm，并有双标准孔。来源与适用性见原提案及 `mcu_supply_path_assessment_2338/REPORT.md`。SiP局部逃线/瞬态/IR-drop/热资格未确认，不得声称完全符合推荐。
3. 原有MCU EP8个via-in-pad、23.8µm临界边缘、继承的.05mm裕度，以及外供SENS时序/反灌、未知相机/电池/充电安全门均不变。
4. `mechanics_linked.json`原样关联四套CAD环境/原完整安装预算。C103预算.95×1.45×2.45mm、R503为2.45×1.45×.95mm，没有缩小/置零。原同位置筛查无正体积碰撞；未知MPN真实高度/焊料/公差仍未知，不是新全整笔装配验证。
5. 无Gerber/生产批准、无采购、无烧录、无上电。只有检查源与证据，不授权量产或实验接电。

`native_view.png`已实际查看，是从新原生几何生成的局部F/B图，不是GUI截图。橙色courtyard交叠明确显示。
