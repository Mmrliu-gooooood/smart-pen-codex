# 安全接线/实机门：本文件不是接线指南

**不要让用户猜GPIO、试排线或给未知模组上电。当前没有一块已审核profile；所有名字均拒绝。** 用户已购实际SC035HGS定制30pin，不是本候选SC031GS；旧AI30pin、generic24pin和小型SC031GS销售页均不能证明该30pin兼容。没有采购、厂家联系、实机授权或任何物理图像证据。

## 已核对的现有native，但没有导入任何运行profile

只读检查的本地源为`pen_publication/verified_revisions_r10/verification/hardware_mechanical_stage_20261029/smart_pen_next_20261028/hardware/gate_supply_native_mpn_source/system_master/mainboard_revD.xml`，SHA256 `9be62659bf08c3897090e63e6db8af0cbfa571e786390677ca328ecdc9384948`。

该版本仍见CAM_PWR_EN/IO_EN/BUS_EN及RESET_UART_TX/PWDN_UART_RX旧复用网络；不是取消UART/GPIO44改状态灯的新版本。J107三线只有USB_EN1、USB_EN2、GND（关联GPIO18/21），没有CE许可。**这些是现native审计差异，不是本相机的可用接线表**。102件native仍是v4；v5新头/管脚提案未实施。此候选不填写以上GPIO，不改native。

## 未来允许注册一个profile前必需的证据

1. 指定精确板修订、实际ESP32封装/Flash/PSRAM型号、sensor ID、实际模组料号/连接器方向及逐脚电气证明；不得以相同pin数/芯片系列推断。
2. 明确各rail电压、I/O电压、板载稳压/电平转换、reset/pwdn真实网络、上电时序、掉电时IO反灌与隔离；审查未供电输入状态。所有camera power/enable/control GPIO必须写进该profile的显式review清单并与本版native对应，不能使用教程默认。
3. 专属prepare/on/off实现：先安全隔离/复位/时钟状态，按真实供电时序执行；任何失败能安全结束。不可把切regulator当作所有IO安全；未获准的模块/板不得填假回调返回成功。
4. 用适当设备先证实真实XCLK/PCLK、占空比、同步极性与电平、有效8位顺序；PCLK不得超过S3官方40MHz指导上限。平均字节率/降FPS不能代替此门。scope记录绑定板、模组、模式、日期；不能写“推算33.6MHz”冒充实测。
5. 限定获准台架先核ID读取、VGA测试图/真实未缩放RAW，307200字节/640stride、帧完整性/丢帧/错误恢复、电流温升、PSRAM与DMA余量；不先进行整笔运动书写。
6. 分开验证近焦视野、四角、笔轴/纸面姿态、真实点阵/墨水；其后才设计传感器200×200、曝光写序、短曝光与高fps。内部官方表存在不是200模式资格。
7. 提供压力边沿队列/安全停机/板级复位、新source epoch约定、真实笔尖mapper与光学标定；再进行录制，不可先把sensor来源标记当camera_qualified。

## 当前硬阻断

SC031GS模组连接/光学仍未冻结；真实板级power hooks空；无PCLK测量；无PSRAM运行配置；无物理mapper；无真实图像。因此本包只交付源码和构建/host异常测试，不提供可执行的接线、上电、刷写步骤。实机需要未来明确授权，不能因编译通过就扩大范围。

补充SDK约束：当前编译为专用SCCB I²C port1、100kHz，新I²C driver会启用SoC内部上拉；真实profile审核必须包含这条上拉/电平转换的安全性和总线独占，不能把低压裸sensor直接接上。每次I²C传输SDK超时1000ms，probe/初始化是有限步骤但不是200ms帧deadline；不能在需要及时处理压力边沿的actor内执行初始化，也未证明启动看门狗/总耗时预算。
