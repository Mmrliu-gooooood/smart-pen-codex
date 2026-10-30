# 连续纸张 V2：ESP32-S3 独立纯RAM冷启动对照（未上板）

**仅本地源码、构建/链接与host功能证据。没有刷机、设备连接、RAM加载或上传。不要执行SDK构建日志末尾自动生成的flash/write_flash建议。**

## 当前结论

同一批完整200×200像素送入两个隔离实现：冻结原 `pen_roi_decode_opt`（符号重命名为`pen_roi_decode_opt_frozen`，源码字节不变）与新 `pen_roi_decode_continuous` V2。原始基准目录保持历史不变，新工程不接入应用/摄像头。

| 固定输入（全200px、理想合成连续纸张） | 冻结原core | continuous V2 |
|---|---:|---:|
| 5/6/7mm FOV，各phase0 | -2 DETECTION | 0，坐标/36方向/crop/双向变换核对 |
| 45°旋转 | -2 | -3 NO_GRID |
| 独立审查深边墨迹 case063 | -2 | -2 |
| 9mm超密度压力图（**超出5–7mm目标范围**） | -2 | -2 |

正向三例不代表通用覆盖。上游V2有限合成扫测分数仍为**小数FOV17/36、平面旋转60/96**；没有物理打印、实际相机、笔尖位置/倾斜或实时保证。全200px输入不等于全图拟合：V2选中心96px（密度过高时80px）并执行有界边缘策略，选中ROI外证据不检查。失败不能解读为“没有纸”。

输入来自上游commit `0f8b569176c77dad34aaf83bb008eb118c9f1208` 的0.3mm纸张编码；不是answer拼出的孤立6×6图，也不是真相机照片。fixtures/upstream_target_manifest.json SHA256=`3dc40e3dc8578c13b7288bae6e24af548494031ac9233161ef57f9b29efd4aaa`，candidate最终冻结见verification/CANDIDATE_SNAPSHOT.json。所有x/y、crop、方向、变换仅返回后核对，不作为解码输入。

## 冷启动计时与资源

- **cold only**。原core传NULL prior，wrapper没有prior API；不虚构warm速度，不宣称CPU cache已清空。
- `esp_timer_get_time`只包围一次完整函数调用；V2的选裁剪、复制、边缘处理、检测、冷搜索、变换计算均在计时内。夹具RLE解压、malloc、串口打印在计时外。不是相机FPS/整链路延迟。
- internal heap显式申请工作区**31,104B**及原始Gray8 **40,000B**，共71,104B，且另有RTOS/任务栈/代码/夹具/printf开销。workspace不放小任务栈，两个decoder串行复用其中core，不并发。申请失败fatal，不能算通过。
- 主任务栈16KiB，输出每次调用后的stack最小剩余字节与heap free/min/largest。minimum是本次启动累计低水位，非单调用独立峰值。`.su`只给每函数静态帧，不能代替运行高水位。linker `.dummy`段存在内部RAM别名占位，`size`总和不是实测heap余量。
- 此独立profile仅internal，PURE_RAM_APP不初始化Flash/PSRAM，PSRAM明确skip。不因N16R8文字擅自启用octal或推断内存容量/电气配置。

## 修复旧基准的newlib格式风险

历史原基准开启`CONFIG_NEWLIB_NANO_FORMAT=y`但以PRId64打印微秒。官方IDF v5.4明确nano不支持64位整数格式；所以旧版build和host parser通过**不证明其真实串口输出可用**，不推荐执行旧镜像。历史文件未改。

本变体effective config关闭nano，源码#error阻止误启用。目标map/symbol实际链接full `libc.a(libc_a-vfprintf.o)`、IRAM `_vfprintf_r`/`_dtoa_r`/`snprintf`，不是仅查defaults。启动时用目标`snprintf`检查`4294967297|1.25`，失败fatal且不跑样本；随后输出mandatory超32位和double格式探针供parser复核。**该自检尚未实际执行；host mock不代替目标libc实测。**

## 安全门：设备识别 → 私密备份 → 用户确认允许中断 → 再制定执行步骤

默认`PEN_DECODER_BENCH_RUN=n`。没有相机、LED、压力、电池、无线、NVS、OTA、eFuse/密钥写操作。Task watchdog禁用以容纳长冷搜索，勿用于产品固件。

纯RAM是减少非易失写风险，不是“零影响”或设备执行授权。ROM下载模式/工具连接/复位/执行会中断旧固件、改变RAM；SDK UART0 115200及secondary USB Serial/JTAG控制台会输出，相关焊盘并非静止。先断开相机/LED/电池/外部执行器，核对实物接线和板图；不靠“不调用GPIO”保证所有板上引脚无动作。

用户仅提供DevKit N16R8标记，尚未核实实物、芯片revision、Flash ID/实际容量、PSRAM模式、已有分区及旧digital_pen数据。SDK参数不证明物理16MiB。第一步只要正反面和模块丝印/USB口照片、电脑系统、现有固件是否必须保留、是否允许后续停机，不执行设备命令。

之后取得同意再按安装版本官方esptool进行只读识别与整片实际容量备份。识别也可能复位；v4 `read_flash 0 ALL <private_backup.bin>`是官方整片读取形式，容量不符就停止；两次独立读取核长度/哈希/一致性，先确认同板恢复条件。Secure Boot/Flash加密/下载限制可能阻止读取或只得到密文；不force、不改eFuse，不假设拿到文件就能恢复。

备份/原固件可能含账号、Wi-Fi凭据、笔迹、设备密钥，放本机非仓库私密目录，**不得传GitHub/Library/公开issue或发给助手**。gitignore不是安全边界。未确认身份/备份/恢复路径/中断同意，不执行RAM镜像，更不能无条件擦除或写Flash。

官方实验性RAM-only镜像可考虑ROM no-stub load_ram，但本工程仅验证无IROM/DROM加载段，不能证明任一N16R8实物可启动。这里不给无条件设备加载/刷写脚本。旧7样本基准的安全流程原文另存BASELINE_SAFETY_REFERENCE_ZH.md作历史参照；它的性能/格式状态不得覆盖本页勘误。

## 离线复现

激活同一 ESP-IDF v5.4（GCC14.2, esptool4.12），无设备连接：

```sh
. /verified/path/to/esp-idf/export.sh
python tools/embed_fixtures.py
python tools/check_host.py > verification/host-functional.json
python tools/check_geometry.py
python tools/test_serial_parser.py
./tools/build_only.sh disabled
./tools/build_only.sh enabled
```

build_only仅接受disabled/enabled并固定执行build；不含设备命令。每profile独立SDKCONFIG；defaults不能覆盖已有config，修改配置请使用明确清理/全新构建目录（仍不连接设备）。`check_static.py`读取现有目标nm/map/image_info证据，使用另一个机器时先重新生成这些证据。完整记录见verification/RESULTS.md。

## 日志schema2与严格核对

固定顺序header（fixture/source digest）→runtime_config→format_probe→memory before/allocated→每图每repeat依次frozen_opt、continuous_v2的decode+memory→memory after_free→PSRAM skip→complete。默认3次，支持1..10。所有失败记录不输出旧坐标/变换；无成功NOFIT混合平均或FPS换算。

后续用户自主执行、回传**脱敏**完整串口文本后：

```sh
python tools/summarize_serial.py /private/path/to/serial.txt
```

parser核header绑定、format探针、整数时延、准确样本集合/顺序、每个状态、36方向、crop/edge统计、双向6系数变换容差和逆变换。数据错误或不完整拒绝；功能错误exit1；即使一致也exit2并`identity_verified=false, overall_pass=null`。hash字符串不能认证实体板或日志真实性，**不提供整体设备通过结论**。matrix replay容差1e-5；独立几何核对另见verification/independent-geometry.json（以生成器`p*(cell-origin)-0.5`计算36网格中心，不复制拟合变换作真值）。

## 官方参考（2026-10-29核查）

- [IDF v5.4 nano格式限制](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/kconfig.html#config-newlib-nano-format)
- [IDF v5.4 RAM/PURE_RAM_APP](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/kconfig.html#config-app-build-type)
- [esptool v4 RAM加载限制](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/advanced-commands.html)
- [只读识别/整片读取/镜像检查](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/basic-commands.html)
