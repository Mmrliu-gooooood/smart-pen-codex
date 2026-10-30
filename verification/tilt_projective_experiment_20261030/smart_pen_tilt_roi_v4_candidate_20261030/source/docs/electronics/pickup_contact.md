# 拾笔/二值触点评审板 — 2026-10-28 重建，NOFAB

**本目录是新重建版本，不是找回昨日原件。所有通过结论来自本次生成与实际检查，不沿用2026-10-27结果。** 这是12×20mm、0.8mm、双层内部电气测试小板，不是完整笔主板，也不是已批准投板包；没有Gerber/钻孔发布。完整笔中宜把这些电路整合主板，不能假定本小板可放在笔芯旁。

## 文件与本次检查
- 原生 `pickup_contact.kicad_sch/.kicad_pcb/.kicad_pro`、本地 `Pen.kicad_sym` 和内部焊盘 `Pen.pretty`，可编辑。
- `tools/build.py`生成原理图/本地库；`layout.py`放置；`route.py`生成MEMS向外扇出与两层互连。路由算法不是制造认证；修改后必须重跑检查。
- `tools/verify.py`独立硬编码官方引脚合同，不读取生成器 `design.json` 作为预期值，检查实际KiCad XML：35个已连接引脚+1个明确NC；同时逐PCB焊盘核对，校验尺寸/厚度，执行ERC和包含原理图一致性的DRC。
- `erc.rpt`、`drc.rpt`、`verification.json`是本次真实日志，未配置DRC/ERC忽略项。`review`含原理图和板层预览；`routing_attempt.json`记录最终连接路径尝试，不是测试波形。

## 接线、器件与默认状态
J1从PCB正面左到右：1=3V3_AON、2=GND、3=AON_I2C_SCL、4=AON_I2C_SDA、5=PICKUP_INT_N、6=NIB_CONTACT_N。J2从正面左到右：1=CONTACT（CT）、2=GND（G）。都是内部焊线焊盘，不是用户可触摸/可热插拔接口，焊线必须在壳体上另作应力释放。

只允许稳压3.3V输入，不接电池或USB5V。LIS2DW12TR的CS和SA0接高，I²C地址0x19；保留脚7接地、NC5按官方许可接地、INT2明确不接。供电和主机I/O必须协同，避免断电灌电。C1/C2各100n、C3为1u；最终器件MPN/直流偏压尚未采购审核。

R1/R2=10k是拾笔总线唯一一组上拉，主板不要重复安装。首次100kHz：近似30–70%上升时间0.8473RC，100pF约847ns；线束电容/波形必须实测，不能保证400kHz。拾笔固件候选为50Hz低功耗模式1、关闭低噪声；20ms采样周期不是总唤醒延迟保证。1.6Hz的625ms周期不适合直接承诺快速预唤醒。睡眠前必须配置INT1低有效、锁存、正确路由；清除历史事件、读回配置并确认线恢复非有效，再启用RTC唤醒。这些还没有固件/实物验证。

R3=100k上拉，R4=1k串联到外置常开干接点，C4=1n C0G。只检测接触，不测压力。名义释放τ=0.1ms，到0.75VDD约0.139ms，对应0.5m/s时约0.069mm；电阻±1%和电容±5%使τ上限约0.106ms，尚未计GPIO漏电/阈值、弹跳、噪声和固件延迟。闭合静态约32.7µA。不要通过增加电容掩盖接点问题；需保存边沿前后时间戳/坐标缓冲并验证首次落笔。

## 布局及制造门槛
- 标准LGA-12 2×2mm、0.5mm间距封装，0603无源器件；U1自带方向标志，J1丝印1–6，J2 CT/G。F.Fab提供装配参考号，不能用隐藏的参考号替代装配图。
- 0.15mm走线/间距；过孔0.6/0.3mm；铜至板边规则0.5mm。板厂及装配商仍须确认能力、报价、阻焊桥和返修工艺。当前是偏保守扇出测试布局，不声称最优整笔布线。
- MEMS本体下两面禁铺铜/过孔；背面无穿过本体的信号，正面只有必要引脚连接。不得取消禁布。无地平面不等于整机EMC通过，最终主板需重新评审回流路径与机械应力。
- 钢网开口没有作为量产参数冻结：须按ST TN0018和装配商整体工艺复核；不可直接把默认F.Paste当最终批准。禁止超声清洗，避免板弯和夹紧MEMS；本板不应承担笔尖机械载荷。
- 无外露接口ESD器件；如果笔芯/触点可向人体传导，须补充绝缘/ESD方案后重审。没有宣称整笔电气安全、寿命、坐标准确性或续航已验证。

## 重建/复验
在KiCad9及其Python绑定环境运行（必须使用有pcbnew的Python）：
```sh
export XDG_CONFIG_HOME=/tmp/pen-kicad/config
export XDG_CACHE_HOME=/tmp/pen-kicad/cache
export XDG_DATA_HOME=/tmp/pen-kicad/data
/usr/bin/python3 tools/build.py
/usr/bin/python3 tools/layout.py
/usr/bin/python3 tools/route.py
/usr/bin/python3 tools/verify.py
```
工具初次默认配置写入只读home失败后，改用正常XDG可写/tmp路径，未申请越权。系统本地日志可能显示+0900，JSON另外记录UTC，均为本次检查。

## 重新核验的原厂来源
- [ST LIS2DW12 DS11811 Rev9](https://www.st.com/resource/en/datasheet/lis2dw12.pdf)：引脚表、供电、封装、工作模式。
- [ST TN0018 Rev8](https://www.st.com/resource/en/technical_note/cd00134799.pdf)：MEMS布局/搬运/装配注意事项。

所有实物、报价、板厂能力及整笔集成均待验证；NOFAB状态不因软件检查通过而解除。
