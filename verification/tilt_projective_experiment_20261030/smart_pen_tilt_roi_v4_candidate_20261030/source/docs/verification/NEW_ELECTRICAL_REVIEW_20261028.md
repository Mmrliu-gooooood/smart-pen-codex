# 新增电路独立审查 — 2026-10-28

**结论：仅限 NO FAB 元件级工程候选。未发现已确认的关键引脚/方向接错；不构成接未知相机、安装调试桥、投板、光学或电池安全批准。**

范围：`illumination_driver`、`power_safety`、`camera_isolation`的原理图、真实导出网表、器件默认属性及接口说明。三模块均无PCB；没有PCB DRC、实物测试或制造放行。

## 首要资格门槛

**TCA9517与主控的带载低电平尚未得到保证。** TCA9517主控侧B端返回低电平最高0.6V，主控从B端驱动低需要满足0.4V的VILC边界，不能只比较普通0.3VCC门槛。PICO资料中的VOL≤0.1VDD、VOH≥0.8VDD明确为高阻负载、3.3V/25°C条件；不能据此推导全温下10k上拉负载或EN负载的保证。当前选型不是已证明不兼容，但在实际供电、温度和负载下证明SCCB低于0.4V、EN高于0.7VCCB以前，应保持JP2开路。相关文档已明确低电平限制。[TI TCA9517](https://www.ti.com/lit/ds/symlink/tca9517.pdf)、[Espressif PICO，表3-4及脚注](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf)

## 真实连接与默认属性

独立使用KiCad从受审原理图重新导出XML，检查非空器件/网络及关键芯片各脚、方向和调试桥的实际DNP属性，不把生成器期望或ERC零错误直接当成电气正确性证明。

|模块|真实器件|网络（含NC）|引脚节点|独立ERC|
|---|---:|---:|---:|---|
|illumination_driver|7|7|16|0违规|
|power_safety|10|8|23|0违规|
|camera_isolation|56|46|203|0违规|

四个调试桥（前两模块各JP1，相机JP1/JP2）均在真实XML含DNP属性；其符号/电路是开放链接，而非仅在名字写“DNP”。不允许用软件代替物理资格审查后的人工作业。

## 模块结论

### 照明

PMV30UN2的1=G、2=S、3=D正确，源接地、漏接LED阴极，栅极有1k串阻及100k下拉；LED阳极供电必须穿过开路JP1和330Ω±1%电阻。以3.6V及326.7Ω计算，短路LED支路约11.0193mA，电阻耗散约39.67mW，与说明一致。真实电阻全温阻值、降额和LED光学安全仍待批准；R1短路/旁路不在此限流保证内。没有把传感器LEDSTROBE与MCU输出相连。[Nexperia PMV30UN2](https://assets.nexperia.com/documents/data-sheet/PMV30UN2.pdf)

### 供电门控

TPS22918的VIN1/GND2/ON3/CT4/QOD5/VOUT6正确；ON经1k控制并100k下拉，CT电容接地，输出经100Ω到QOD，供电到负载还必须通过开路JP1。该结构不是限流、OVP或反向电流阻断器。文件正确保留了VOUT不得外部抬高、QOD瞬态功耗与负载电容、供电斜坡资格门槛。`CAM_3V3_SW`不能替代裸传感器1.8V VIO。[TI TPS22918](https://www.ti.com/lit/ds/symlink/tps22918.pdf)

### 并行与控制隔离

- AXC的A域为3V3_AON，B域为真实传感器SENS_VIO_1V8；控制/OE参考A域。U1的DIR1/DIR2=0/0使全部8位B→A；U2两个DIR低使PCLK/VSYNC/HREF B→A；U3两个DIR高使时钟/控制A→B，PW封装脚号与真值表相符。
- /OE由10k拉到3V3，PMV30UN2在正确方向下拉；其Gate有100k下拉且CAM_IO_EN经过开路JP1。禁用输出的输入仍需定义，两侧偏置及未用输入终端已画入。
- Ioff与VCC隔离可限制掉电反灌，不等于任意残余电压、慢斜坡、未知模块外部供电下零泄漏。应在撤电前禁用输出，并核算传播偏斜、PCLK建立保持及上电瞬态；不能把芯片标称高速能力当成整机72MHz通过。
- `SENS_VIO_1V8`必须来自传感器IO实际使用的同一已核实电源，不能独立向未知模块注电。J1/J2均是语义接口，无已确认30pin实物映射；新J1与主控J2针序不同，禁止1:1排线直连；`CAM_PWDN_UART_RX`旧名称也不证明模块具有PWDN或可直接改接TRIG。

依据：[TI AXC8T245 PW脚表/真值表](https://www.ti.com/lit/gpn/sn74axc8t245)、[TI AXC4T245](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf)。

### SCCB

TCA9517 VCCA=传感器1.8V、VCCB=主控3.3V，A侧与B侧各自上拉至本域，无跨域上拉；引脚1/8供电、2/3传感器SCL/SDA、7/6主控SCL/SDA、5EN、4GND正确。EN参考B域，最终R5=4.7kΩ±1%；按EN在0.2V测试点最大30µA估算，偏置约0.1424V，低于该测试点。该DC估算不是电源斜坡保证。100Ω串阻/4.7k下拉的条件分压约0.97875，按高阻VOH计算得到的约0.783VCC只能作为初算；约0.7mA负载时仍须验证EN≥0.7VCCB。不可使用100k弱下拉抵抗内部上拉。EN仅在总线空闲切换，必须检查ACK、低偏移、电容、传播延迟及带载控制电平。10k上拉和初始100kHz不代表已通过400kHz；禁用/掉电功耗不能视为零。[TI TCA9517](https://www.ti.com/lit/ds/symlink/tca9517.pdf)

## 未做的验证

没有确认旧相机30pin、电源序列、上拉/复位实际负载、波形、LED光谱或眼安全、PCB封装钢网/布局、真实器件采购、温升、EMC/ESD或15–18mm装配。未安装任何commissioning桥。没有将未实施验证转换为通过结果。

## 最终版本绑定

2026-10-28 08:50 UTC在最终冻结文件上重新导出三模块XML并执行ERC；网络、器件值、DNP签名与交付XML完全一致，独立关键引脚断言通过。相机R5真实值核为4.7kΩ±1%。说明文件已补入带载EN阈值和禁止1:1排线提醒。以下SHA-256绑定本次有限审查；任何修改需重新检查。

| 受审文件 | SHA-256 |
|---|---|
| `hardware/illumination_driver/Illumination.kicad_sym` | `fcf07535b7ba353efd729413ea0f2b912dada52be05245e3028275bf8cee9abf` |
| `hardware/illumination_driver/illumination_NOFAB.kicad_pro` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `hardware/illumination_driver/illumination_NOFAB.kicad_sch` | `e0c0f5c44932a2d684ae45144d9941cc010fa4666c59686cd5c015618ed8f3f6` |
| `hardware/power_safety/PowerSafety.kicad_sym` | `cb40222d9e6f45ba27bedebe2062b3b9015e5c53db641a5819770ae4d749c92b` |
| `hardware/power_safety/power_safety_NOFAB.kicad_pro` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `hardware/power_safety/power_safety_NOFAB.kicad_sch` | `51830aa99e49dce2f39145a99efad05d78afecff48fc96f4bfe73862739845ad` |
| `hardware/camera_isolation/Pen.kicad_sym` | `65ee3841da8a436b0bcdb9f16f3514f081816dca8035232789609d2608ddc89f` |
| `hardware/camera_isolation/camera_isolation.kicad_pro` | `a28739e17adcfcaf26f34d68d262842772fc57cde25bb3e6082f67c720fa73f2` |
| `hardware/camera_isolation/camera_isolation.kicad_sch` | `53c27c46c2615e7d6b43d81dc10631f03dc1c9355f4cd21b77166eb54f1626c3` |
| `hardware/camera_isolation/controls_sccb.kicad_sch` | `f95a0aeaa937e98b4a76e801c9659e1ffaea7e78ba6cdd1d21d35bfafc1e7c3e` |
| `hardware/camera_isolation/dvp_translation.kicad_sch` | `d0a48b2fff9fb1d052a92653882f9d1ea71a099669e6f5035d58eaddcf9020b6` |
| `hardware/camera_isolation/safe_bias_interfaces.kicad_sch` | `78a53e40e6636af7ac90dd0275c73c9a6f94269fd506ac2b6c9c0dc527b48efe` |

发布说明：上表绑定设计源文件。KiCad导出XML含运行时间及本地路径，重跑会改变其字节哈希；不能据此认定网络变化，复核应重新从绑定的原理图导出并比较元件、值、网络及DNP合同。
