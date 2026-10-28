# 独立电气审查 — 2026-10-28

**结论：当前原理图可作为 NO FAB 工程候选稿；不构成制造、充电或整机功能批准。未发现已确认的关键引脚接错。拾笔 PCB 的新导出连接、规则与原理图一致性检查通过；不等于实物验证。**

## 本次实际核验

直接从本次三套原生原理图重新导出 KiCad XML，核对非空器件及网络，未沿用其他版本的检查结果。独立导出的网络签名与交付 XML 相同；另以手工定义的关键引脚期望检查实际 XML。

| 模块 | 器件数 | 网络数（含NC） | 网表节点数 | 本次独立ERC |
|---|---:|---:|---:|---|
| mcu_usb | 34 | 64 | 171 | 0违规 |
| power_core | 19 | 19 | 61 | 0违规 |
| pickup_contact | 11 | 8 | 36 | 0违规 |

ERC为连接检查，不证明器件参数、布局、实物功能或安全。上述范围不包括完整主板；目前只有拾笔模块存在PCB。

## 电路审查结果

- **PICO：** 六个3.3V电源焊盘及EP57接线正确；GPIO47/48分别对应pad37/36；USB D−/D+分别到pad25/26。存储专用pad28、38–42及VDD_SPI pad29保持外部NC，未挪作应用GPIO。BOOT上拉、GPIO45/46下拉及GPIO3上拉合理；N8R8内存电压为3.3V。新GPIO分配必须与固件同步，不能依赖其他版本表格。[Espressif PICO v1.2，表1-1、2-1及启动配置](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf)
- **USB：** A6/B6共同D+，A7/B7共同D−；两个CC分别5.1kΩ下拉。TPD4E05U06的1/2/4/5为保护信号，3/8接地，6/7/9/10明确NC，映射正确。[TI TPD4E05U06，表4-2](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf)
- **D1封装：** TPD1E10B06DYA确属SOD-523；不能把此名称当错选封装。它为双向器件，VBUS/GND两端无极性接反问题。所选KiCad库焊盘0.6×0.7mm、中心距1.4mm，与TI示例0.67×0.4mm、中心距1.48mm不完全相同；这不是已证明不可焊，但必须保留精确land/paste/mask审核，不能仅凭库名批准。[TI TPD1E10B06 Rev G，DYA0002A封装/布局](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf)
- **充电：** BAT2/3与OUT10/11成对接对；CE由VBUS经10kΩ上拉，JP1保持常开/DNP；NTC接口为PACK_NTC及保护后GND，没有图示裸电芯负极旁路。ISET范围约91.12–113.73mA；ILIM3.24kΩ最坏约536.23mA，并非500mA硬上限；CE开路典型约16.95µA和闭合约0.5mA均绕过IN限流。新电源说明已记录这些边界。[TI BQ24074，表7-1、8.5](https://www.ti.com/lit/ds/symlink/bq24074.pdf)
- **升降压：** TPS63802引脚、SW_L1/L2电感、EN到SYS_RAW、MODE接地正确。511kΩ/91kΩ反馈约3.3077V，91kΩ未超过原厂低侧100kΩ上限；输入10µF及输出2×22µF仅为标称值，不能代替偏压后有效电容、饱和电流与布局资格。[TI TPS63802，表7-1及§10.2.2](https://www.ti.com/lit/gpn/tps63802)
- **拾笔/触点：** LIS2DW12的CS/SA0高、RES7接地、NC5接地、供电9/10及INT1=12正确。主机J3与拾笔J1的1–6分别为3V3、GND、SCL、SDA、拾笔中断、触点；两中断独立。[ST LIS2DW12 DS11811表1](https://www.st.com/resource/en/datasheet/lis2dw12.pdf) 100kΩ/1kΩ/1nF触点网络在3.3V闭合约32.7µA、32.7mV；释放至0.75VDD约0.138ms。仍需去抖、输入阈值/漏电和机械噪声验证。

## 必须保持的未放行项目

1. 摄像头实际模块映射、受控电源与默认关闭隔离尚未实现；CAM_BUS_EN下拉不能单独保证未知低有效OE隔离器关闭。UART兼用控制线禁止直接接未确认相机电平域。
2. 未选合格保护电池、真实NTC及温度窗口；禁止短接JP1测试未批准电池。转换器低压运行不是正常欠压停机策略。
3. USB源识别、VBUS状态感知、枚举/挂起电流、上游偏置总电流、输入浪涌和持续错误高压防护仍未验证；TVS不替代这些功能。
4. 独立工程同名网络不会自动物理连接；电源输出、输入和GND不能只按连接器位置猜接。当前J6=VBUS/3V3/GND，J7=EN1/EN2/GND。
5. I²C的10kΩ上拉不保证400kHz；须对实际电容测上升时间。RF、ADC前端、天线、主板封装/布线及完整整机测试仍未完成。

## 拾笔PCB最终独立检查

2026-10-28 03:52 UTC，对冻结源重新执行 `kicad-cli pcb drc --schematic-parity --all-track-errors --severity-all --exit-code-violations`：**0违规、0未连接、0原理图一致性问题**。同次重新导出三模块XML并重新执行ERC及关键引脚断言，结果与上表一致。

- 逐一比较PCB焊盘网络与本次新导出XML，无差异；3V3_AON不存在检查发现的断岛。
- 实际151段铜线均为0.15mm；全局最小线宽、铜间距与Default网络类间距均为0.15mm，未通过放宽间距或豁免隐藏问题。此结果是该规则下的通过，不代表任何板厂的制造承诺。
- 独立几何检查：背面走线连同半线宽包络不穿过MEMS的2×2mm本体区域；正面保留必要引脚扇出。两面规则区域禁止过孔和铺铜，但允许走线，不能声称它自动禁止一切后续错误布线。
- 仍需装配商审查LGA焊盘/钢网、实际板厚及工艺，验证应力、回流、噪声、去耦、触点ESD与整机功能。没有出具Gerber生产放行。

## 受审源文件身份

下列SHA-256绑定本次检查范围。更改电路、规则或布局后应重新检查；报告不是对未来版本的授权。


| 文件 | SHA-256 |
|---|---|
| `hardware/mcu_usb/Pen.kicad_sym` | `686f935ef75805d76466519a729e69225bb226f818d32762edda8306150fcc7a` |
| `hardware/mcu_usb/mcu_core.kicad_sch` | `011c00823fa4fa46d90841f6211d7e64cb9279099c540818a352908fef3076ad` |
| `hardware/mcu_usb/mcu_usb.kicad_pro` | `c0d1eaf0acd480779b7aee5a734d5562814993441bc656ec22becdc4be4d76e3` |
| `hardware/mcu_usb/mcu_usb.kicad_sch` | `a011b965f8dbd2b9fe48ced57eb8d672dbc0a178d1442fd4a938613d0d2772d4` |
| `hardware/mcu_usb/usb_entry.kicad_sch` | `a8d61125d80976696b3ddd9600d7a2690416732ef0078584b72f72c58e5bba07` |
| `hardware/power_core/PowerCore.kicad_sym` | `8e52471bc28431d20d46369f171e5fc0ce0879499a47ef7a4c81c8306394cd6b` |
| `hardware/power_core/power_core_NOFAB.kicad_pro` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `hardware/power_core/power_core_NOFAB.kicad_sch` | `976bcd141f092594218b4edb5197e8636853c0787cb0774e26340c687f3455de` |
| `hardware/pickup_contact/Pen.kicad_sym` | `32d0a41f63f017ac71675daee21575a2601149103def6f40246233e9eda961b3` |
| `hardware/pickup_contact/pickup_contact.kicad_pcb` | `cffbce0855927b44d69afd9d8066e561420eee146a1887a90861c8f56285c061` |
| `hardware/pickup_contact/pickup_contact.kicad_pro` | `c568c84ba0c3a84f1fd37e3ff21375d5763e9e664f080673e830cc6ed75c93aa` |
| `hardware/pickup_contact/pickup_contact.kicad_sch` | `868432bbe38588a13ebcd7abc2724533f78347e6d53b12219a94fe3e1e5b2b27` |
