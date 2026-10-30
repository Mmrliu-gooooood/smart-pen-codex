# 相机隔离默认态与 OE 动态补充审计（独立于冻结 0628）

**红色门槛：当前 R203=10k + Q201 被动释放 OE 不能声明满足动态输入规范；JP201 闭合后的量产默认安全 OFF 尚未证明。0 DRC、静态电阻默认态和有限几何连通都不能代替这些证明。NO FAB / NO POWER。**

本轮只读原生设计；没有换料、改阻值、桥接、写 eFuse、实现固件或发布。0628 PCB `63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c` 与 manifest `be6b0eabfd477ab6c3a932204f4b9f05b9e6cab9f8b7c5a41f79514e745f06c3` 原样核对。所有 commissioning 跳线仍 OPEN，provider 仍 NULL。

## 1. GPIO42 / MTMS：纠正“JTAG 引脚一律复位上拉”的误读

官方 ESP32-S3 datasheet v2.2 第17页表中，package48=MTMS/GPIO42：After Reset 为 IE，没有 WPU；At Reset 栏为空，不能据此声明复位过程主动拉低。第18页注7的 eFuse 条件上拉仅标在 **MTCK/GPIO39**，不在 MTMS。第22页 I1 说明的是未选中该复用功能时内部外设输入常1，不是引脚上拉。[Espressif datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

TRM v1.8 第493–494页 Table6.12-1：GPIO42 的 RST=1；释义是输入使能；WPU 对应3，只有 MTCK 标1*。Register6.36 的 FUN_WPU 是可写控制，默认表不限制之后软件。Chapter8 Table8.5-1 给出 USB-JTAG/pad-JTAG/eFuse/GPIO3 选择。原厂默认 USB-JTAG 不意味着应用、调试器、下载模式或全部复位/睡眠恢复过程永远保持该引脚高阻无上拉。[Espressif TRM](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf)

PICO-1 v1.2 第16页 JTAG选择表与SoC相符，内部原理图 MTMS 引出至48。实际 N8R8 的 eFuse、启动镜像、调试连接和引脚状态均没有读回实测；本轮不烧写 eFuse。[PICO datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf)

**结论：没有证据证明 GPIO42 原厂正常复位必然上拉；也不能把未审查的软件/调试状态抽象成永久高阻。**

### 如果上拉真的被启用，100k是否能压住？不能。

实际网络：R107=100k对地；JP201若闭合，经R201=1k到Q201.G，R202=100k对地。用官方45k**典型**内部上拉作反例：

`Rload = R107 || (R201+R202)`；`Vgate = VDD × Rload/(Rup+Rload) × R202/(R201+R202)`。

| AON | gate（45k典型、外阻标称） |
|---:|---:|
|3.0V|1.566989V|
|3.3V|1.723688V|
|3.6V|1.880387V|

这不是内部上拉必然存在，也不是45k的最坏界限；只是证明当前弱下拉对“允许出现内部上拉”不具备无条件OFF保证。外部调试器主动驱动MTMS高更不能由100k抵消。GPIO42不能同时被当作不受约束的pad-JTAG输入和安全使能。

## 2. Q201：准确器件与温度边界

实际源值 PMV30UN2，SOT23 G1/S2/D3。其25°C、ID250µA阈值范围0.4–0.9V；阈值不是“低于该值就零电流”的保证。25°C Rds上限：Vgs1.5V/ID0.1A时100mΩ，1.8V时59mΩ，2.5V时43mΩ。4.5V栅压150°C有50mΩ限值，不能迁移到1.5–3.3V栅压。IDSS1µA和|IGSS|100nA各有25°C测试条件，不能当热态最大值。[Nexperia datasheet](https://assets.nexperia.com/documents/data-sheet/PMV30UN2.pdf)

因此上述1.57–1.88V反例足以否定“必然关断”，但不据此输出未经测试的精确OE电压。真实装配MPN/丝印/批次尚未确认。即使JP201 OPEN，R202钳制到低的静态意图也不等于任意热态、污染、上电耦合/Miller或断电顺序均已合格。

## 3. 五路OE总泄漏：预算，不是漏电通过报告

AXC8一只OE + AXC4四只OE，共5输入。两份官方表均列control II：-40..85°C每输入±0.5µA；-40..125°C±1µA，且测试条件限定电源与VI端点。最热控制输入筛算总5µA。[AXC8 datasheet](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf)、[AXC4 datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf)

在AON最低3.0V、OE高阈值2.0V、R203最大10.1k的条件假设下，总下拉泄漏预算 `(3−2)/10100=99.0099µA`；扣除5µA后留94.0099µA给Q201/板面等。这只是预算：**没有Q201热态上限、污染上限、所有中间输入电压泄漏保证、VIO掉电时适用的control-II完整条件，故不能签发最坏OFF证明。** 不把A/B端口Ioff偷换成OE输入漏电规范，不把Q201的25°C数据和AXC的125°C数据拼成全温通过结论。

## 4. OE慢上升沿：本轮最重要的动态红旗

视觉核对AXC4 §5.3与AXC8 §5.3，10ns/V在**MAX**列。不是最小斜率时间，也不是10ns总时间。AXC4 §7.3.1描述标准CMOS输入需要符合该速率，慢/噪声信号应先整形；没有OE豁免。因此设计审查按OE也必须符合10ns/V处理，除非TI针对实际MPN给出正式例外。不能把“推荐上拉以维持上电默认禁用”解释为“任何上拉阻值/负载的运行中释放沿都合规”。

每个OE控制输入电容4.5pF是**典型值**，不是最大/最小；五路合计22.5pF。先忽略Q201漏极电容、46.64mm走线、9个OE过孔、探头和封装寄生，只作标称RC模型：

`Δt(0.8→2.0V)=10k×22.5pF×ln[(AON−0.8)/(AON−2.0)]`。

| AON | Δt/1.2V |
|---:|---:|
|3.0V|147.836ns/V|
|3.3V|122.611ns/V|
|3.6V|104.928ns/V|

已比10ns/V慢约10–15倍。**这是明确需要修正/论证的模型红旗，不是最坏电容值或实测失败的替代品。** PMV30UN2 Coss典型70pF是在Vds10V条件，不能直接当当前3V处的定值；但也绝不可当不存在。R202100k放电栅极的过程还可能延迟Q201真正关断。datasheet的35ns典型关断延时使用6Ω栅极驱动等完全不同条件，不适用于这里。

## 5. 下一轮仅限两个候选方向（均未采纳、未改源）

**A：AON域主动推挽OE驱动/整形。** 在保留默认禁用意图下，以具有明确上电/失电行为的适当逻辑级替代被动释放路径；输入默认态和复位/电源有效联锁共同确保OE高。需确定输入极性、阈值、最大传播/转换时间、输出能力、Ioff/钳位、AON/VIO任意时序、五OE最大负载和MCU掉电场景。若仅在慢输入后放一个无Schmitt普通门，不能声称解决慢输入本身问题。

**B：保留分立反相思想，重审Q201及R203/R202。** 更低电容开关、更强上拉/下拉只能作为有限候选；必须以温度覆盖的最大负载/泄漏/门限计算。仅用22.5pF典型RC可算出的数百欧上拉，不可直接下单：Q201电容会进一步收紧，OE低时直流电流、GPIO/开关能力、续航和热都要重算。更强下拉也不能防止调试器主动高驱动，且45k内部上拉无min/max范围，不足以完成全温最坏设计。

共同必需的发布条件：固定并审计JTAG/eFuse策略（不自动烧写）；reset/brownout/bootloader/download/sleep-wake/崩溃各态；AON先/后上掉电、VIO渐降/卡中间电压、MCU未上电；五路OE总负载最大值与最远端波形、逻辑阈值、转换速率、无毛刺禁用；头部回灌/电流、温度/电池安全。然后重新源审查/ERC/parity/layout/DFM及台架实测。

## 文件与保全

`calculate.py`从冻结netlist重核器件值，输出可重复计算；normal/-O一致。`sources_index.json`记录URL、版本、页码与本地下载hash。`sources/`仅本次只读研究缓存，不纳入发布manifest，避免把整份厂家PDF误当项目自有成果。原始页仅本地视觉检查，未改图。期间云执行服务短暂掉线，恢复后先检查先前下载没有执行，再补取；没有针对拒绝反复写入冻结目录。
