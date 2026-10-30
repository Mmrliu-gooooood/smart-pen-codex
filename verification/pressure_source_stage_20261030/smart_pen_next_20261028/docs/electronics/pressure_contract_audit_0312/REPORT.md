# 当前触压前端只读审查

范围：8fe809b685633dd86dddc36ec33961d61ef7fad9fca52286bc47bd72a4f614e5，未改变任何PCB/原理图/固件。状态NOFAB/NOPOWER，接通压力线路不能解决以下产品门。

## 实际源与器件

实际PCB：R503=100k 1%，B(2.5,11.5)，3V3_AON→NIB_CONTACT_N；R504=1k 1%，B(3,54.25)，NIB_CONTACT_N→CONTACT；C504=1n C0G，B(4.25,9.75)，NIB_CONTACT_N→GND；J103实际B(3,52)，pad1 CONTACT、pad2 GND。逐pad位置/原生字段在results.json；不能把47k候选或机械虚拟B70.5当现有源。当前字段未提供已批准47k替代MPN。

U101.7=NIB_CONTACT_N，对应GPIO2/RTC_GPIO2，不是GPIO7。[Espressif PICO规格](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf)。GPIO2具RTC唤醒能力不等于已经配置。[官方休眠接口](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html)。实际应用候选 firmware/application_idf/main/board_provider_absent.c 返回0，不能宣称落笔唤醒已跑通。

## 必须处理的阻断

1. [ALPS官方SPVE110100](https://tech.alpsalpine.com/e/products/detail/SPVE110100/) 的最低电阻负载50µA/3V。现100k+1k在3.3V名义32.673µA；即使3.6V且两阻最小，也不足50µA。现组合不能作为符合该触点最低负载的产品前端。
2. 条件47k+1k、±1%、AON假定3.0–3.6V、触点0–1Ω时，最小61.880µA，最大低电平约76.6mV。仅条件筛选，不代表真实AON最低3V已获保证。需另版本修改R503源/BOM/MPN、重导网表/parity及测试；本审查不修改冻结版。
3. 现RC是1n电容，理想释放到75%电源上界约147µs（100k）、69µs（47k；从零起更保守）。微秒RC不能保证机械弹跳消除；应带时间戳采样、测弹跳、软件去抖并校验起收笔延迟。接触瞬时电容电流不能代替最低直流负载。原厂要求电容性使用另核、正确处理bounce。
4. 官方寿命测试50,000次，不是预计失效日，也不是高频消费级书写寿命保证。必须定义落笔次数目标并做低负载耐久与可维修性评估。
5. CONTACT→1k→GPIO只有限流/滤波，不是已验证ESD保护。所审压力网没有独立TVS/钳位器件；是否需增保护应按可接触笔芯/线束/壳体放电路径及钳位电压、漏电、RC、AON反灌统一设计，不能靠芯片内部ESD额定替代整机测试。
6. RTC wake需明确低有效唤醒、外部pullup保持、唤醒后RTC到数字GPIO切换、落笔仍按住时防立即重复唤醒、断线/短路诊断、掉电/棕断电状态。没有实际firmware/provider或实物测试，不能声称实现。

## 结构/布线下一步

J103保留B52，ACCESS长线虚拟B70.5未实施；R504靠当前入口，C504在MCU旁，约44mm的入口到MCU连接不是完整短局部RC。布线需同时验证输入回流、暴露线束耦合及去抖，不仅连通。

机械0.25mm候选行程、姿态下笔尖位移、开关动作公差、回弹和换芯工艺均是独立门。官方ON位置/总行程不是已校准笔尖行程。不能由此报告推导坐标精度或儿童安全。

建议在连接压力供电前明确采用SPVE还是其他机构。如果保留SPVE，优先另版选择47k且建立有效轨≥3V写入状态门，连同实际GPIO阈值/漏电/ESD、寿命与软件验证一起关闭；这不是建议通过拉高电压弥补任何未知器件限制。

## 复核边界

计算仅纯电阻和理想RC，不含漏电、寄生、弹跳、温漂或实测波形。audit.py normal/-O复算。首次JSON导出因KiCad UTF8非可序列化失败，已改明确str转换；该失败未产生有效结果，不计通过。

补充：47k候选3.6V/两阻−1%/触点0Ω最大75.758µA；R503最坏耗散不足0.3mW（不是ESD脉冲资格）。原生R503字段仅通用值/0603封装，无厂商MPN，不能称现有已批准100k MPN的直接替换；需另选47k±1%同0603且额定电压/功率满足3.6V连续和实际瞬态，不能据低平均功耗省略脉冲规格。
