# MCU / USB 评审版 — 2026-10-28重新构建 / NO FAB

**不是昨日原件恢复，不沿用昨日检查。没有主PCB、Gerber或整笔制造批准。** 原工程丢失后依据原厂资料和已记录设计边界重新构建；GPIO分配属于本次新提案，必须与固件重新同步。

## 已提供与本次检查
- 原生可编辑三级文件：根 `mcu_usb.kicad_sch`，子页 `mcu_core.kicad_sch`、`usb_entry.kicad_sch`；本地符号库、项目、生成器和独立检查器。
- `python3 tools/build.py`生成；`python3 tools/verify.py`实际调用KiCad9 ERC与XML导出，使用**独立手写网络合同**逐脚检查，拒绝空/部分网表。
- 本次结果以 `verification.json` 和 `erc.rpt` 为准：**34个元件、171个引脚、0差异；ERC 0错误/0警告**。包含所有有意NC脚，且核对已赋封装的焊盘编号集合；不是尺寸/钢网审查。
- 首轮生成曾因括号错误产生空网表并显示ERC0，该结果已明确撤回；现检查强制元件集合与所有引脚覆盖，避免同类假通过。
- `review.pdf`是图面审查用，不是生产资料。所有器件绘为明确编号的功能框，不能当作已完成PCB摆放。

## 原厂核对与安全边界
- [Espressif PICO v1.2](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf)：采用真实ESP32-S3-PICO-1-N8R8，57焊盘；2/3/20/46/55/56接3V3，57接地。29 VDD_SPI按外围参考图外部NC；28及38–42被PSRAM占用，30–35/53–54为NC。36是GPIO48、37是GPIO47，不能套裸芯片脚位。
- GPIO19/20固定原生USB；GPIO0上拉、45/46下拉，GPIO3上拉；EN 10k/1u为起始候选，慢升电/棕断待测试。BOOT低且GPIO46低用于下载。
- [TI TPD4E05U06 RevO p4](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf)：1/2/4/5保护通道、3/8地、6/7/9/10NC。实际库 `USON-10_2.5x1.0mm_P0.5mm` 编号匹配，最终land/paste需审查。
- [TI TPD1E10B06 RevG p3](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf)明确DYA为2pin SOD-523，附录也称SOT-5X3。D1为VBUS瞬态保护候选，不是持续过压或短路保护；其实际焊盘尺寸仍待制造核对。
- USB4105库四个屏蔽焊脚都使用S1编号，因此符号单S1接地覆盖四脚。CC1/CC2各独立5.1k 1%；不支持PD；VBUS保护、连接器选项/图纸、输入浪涌/USB挂起及整机ESD均未验证。22Ω USB串阻为SI候选，原PICO参考为0Ω，须实测再定。

## 29个GPIO已全部分配，不是空闲扩展接口
见 `gpio_assignment.json`。GPIO18/21为专用USB_EN1/2，100k复位下拉在独立电源页，不能重复到共享UART。J3是拾笔逻辑接口；3V3_AON、GND、AON_I2C_SCL/SDA、PICKUP_INT_N、NIB_CONTACT_N与其合同相同。只有拾笔页放I²C上拉。

J2只是**3.3V主控侧逻辑网络清单，不是摄像头FPC**，未实现任何电平转换或电源隔离！传感器1.8V IO不能直连；模块内部调压、FPC映射、PWDN实际功能、时序和PCLK兼容性仍待证据。J2甚至不是完整供电连接器，不能凭此接实际模块。

|复位网络|当前电路|后续不可省略的要求|
|---|---|---|
|CAM_PWR_EN / CAM_IO_EN / CAM_BUS_EN / ILLUM_STROBE|100k下拉|隔离电路必须把低解释为禁用；不得直接套到低有效/OE|
|CAM_RESET_UART_TX GPIO43 / CAM_PWDN_UART_RX GPIO44|共享UART测试口|ROM可能输出，必须由硬件默认禁用的隔离挡住；相机断电/隔离时才可UART测试|
|摄像头侧RESET/PWDN|尚未实现|真实模块脚位/有效电平确认后选择摄像头侧拉阻；不能假定低都安全|

先关闭UART日志、配置控制GPIO，再使能转换器；原生USB+BOOT/EN是主要恢复路径。没有这些物理隔离就不能给相机上电。J4不是与相机同时工作的独占UART。

J5仅接受**安全调理后的ADC输出**，不可接电池。被动1M/330k/100n仅计算候选：4.23V和1%电阻时节点最高约1.0654V，连续电流最高3.213µA，RC0.1%稳定最坏约190.5ms；3V3掉电时仍会向GPIO施压，微安限流不等于掉电安全，因此未画入/未装配。独立电池保护与NTC不能被ADC代替。

8MiB内部Flash还需双OTA和元数据。当前64B×100Hz约23.04MB/小时；2MiB日志仅约5.46分钟。PSRAM易失；没有空闲4pin SPI，不得声称轻松扩容或全天离线。压缩/降采样或重新分配隔离总线/硬件灯控后再审存储方案。

## 物理与制造未完成项
PICO/RF/天线/逻辑接头未分配最终封装；没有主PCB，不能声称小于100×100或能装入18mm笔壳。12mm窄板只是机械协同目标。RF匹配L1、C6/C7和天线待射频布局调试；C6/C7为DNP。电容具体MPN/偏压、功率瞬态、保护/电芯与NTC资格、两支报价、续航与坐标准确性均未验证。符号库功能块不表示元件物理尺寸。
