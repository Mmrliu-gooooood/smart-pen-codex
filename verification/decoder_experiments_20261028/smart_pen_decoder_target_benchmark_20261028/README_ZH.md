# ESP32-S3 独立解码基准——仅编译验证，未上板

**不要运行构建日志自动打印的 `idf.py flash` 或 `write_flash` 建议。那是 SDK 通用尾注，并不适用于本实验 RAM 镜像。没有自动刷机脚本，也没有执行设备命令。**

## 边界

- 与主固件分离；冻结 `smart_pen_app_pipeline_20261028` commit `84476fce1655b299147b2a47089a3f2d25f595de` 的优化解码器，未混入后续候选修复。各源码 SHA256 在 verification/static-check.json。
- 连续纸张夹具来自独立上游点阵生成器 commit `0f8b569176c77dad34aaf83bb008eb118c9f1208`，0.3mm 网格，都是**理想合成图，不是真实打印扫描/相机照片**。fixtures/upstream_provenance.json 记录来源；PGM及manifest可离线重建嵌入头。
- 三个 200×200、全视场5/6/7mm夹具，冻结解码器预期均为 `PEN_ROI_DETECTION=-2`，不得算作成功或高FPS。另三个成功夹具是200px原视场中的96/80/96px裁剪，**不是成功处理完整200px视场**。空白图预期拒绝。没有使用诊断边缘过滤版本。
- 解码输入只有灰度像素、尺寸、710×1000纸张边界/section10,2、工作区及上一轮像素获得的几何先验。答案坐标仅在返回后比对；不输入真实位置、点中心或答案方向。
- 输出坐标是纸张窗口原点，不是笔尖姿态/真实笔迹。成功坐标比较不等于物理准确度验收。
- cold=清空几何prior；**不代表CPU缓存已冲刷**。warm=同一固定像素，复用刚成功解码的prior；非运动相机序列。warm局部搜索不提供cold全局唯一性保证。

## 默认安全性与必要限制

默认 `PEN_DECODER_BENCH_RUN=n`；启用后只跑内置图。无相机、LED、压力、电池、BLE/Wi-Fi、NVS初始化或写入、OTA、签名密钥/eFuse操作。无自定义分区表/擦除流程。禁用 task watchdog 是为了允许长cold搜索，保留系统其他默认保护；不要用于正式产品。

默认是官方**实验性 RAM-only + PURE_RAM_APP**：不初始化外部Flash/PSRAM/cache/MMU。已验证镜像无IROM/DROM映射段，含DRAM/IRAM及SDK的小RTC内存段；仅构建/链接，不证明在你的板上可启动。

**这不是“零影响”操作**：进入ROM下载模式、连接工具/复位和执行RAM程序都会中断原固件、改变易失RAM并改变控制台输出。SDK控制台为UART0 115200及secondary USB Serial/JTAG；这些控制台焊盘并非无输出。任何外接相机/LED/电池/执行器等先物理断开；核对板图、控制台引脚与接线，不能把“不调用GPIO provider”当作所有引脚保持静止的保证。

## 先识别、先备份、再征求执行同意

目前仅有用户提供的DevKit N16R8标记，未看实物、芯片修订、USB口、Flash ID/实际容量、PSRAM型号/模式或已有分区。**N16R8文字和SDK默认flash参数均不能代替实物核实。** 不可假设现有 digital_pen 固件/数据为空，不可无条件擦除。

1. 先提供板子正反面、模块丝印和USB口照片、现有固件用途、电脑系统及串口；断开外设并确认可以暂停原程序。分享截图时隐藏设备唯一ID/凭据。
2. 用户确认后，使用安装版本对应的官方 esptool 文档做只读识别。v4命令名为 `flash_id`，v5使用连字符；先 `python -m esptool version`/`--help`。识别命令也可能复位设备，所以本项目不自动执行。
3. 在设备容量、安全启动/Flash加密/下载模式等得到核对后，备份**整片实际容量**而不是只备份应用分区。官方v4 `read_flash 0 ALL <private_backup.bin>`可自动探测容量；探测与模块标记不符时停止调查，不能盲信。备份过程可能临时使用RAM stub；不会有意写Flash但会中断应用。
4. 在本机非仓库私有目录保存两次独立读取，核对长度、SHA256和两次一致性；记录原分区和恢复条件。受保护设备可能拒绝读取，或只能取得密文，**不要用force绕过，不要改eFuse/加密配置**；备份成功也不自动证明可恢复，先制定同板恢复方案。
5. 备份含Wi-Fi凭据、账号/笔迹/设备密钥等敏感信息：不得上传GitHub、Library、公开issue或发给助手。项目.gitignore不是安全边界；只分享脱敏摘要。未能确认备份/恢复条件时不执行RAM测试或Flash变更。
6. 只有用户确认板型、允许中断、备份与恢复方案、控制台路径后，才进一步制定**针对实物**的手动RAM加载步骤。官方 v4 的 `--no-stub load_ram` 要求可加载内存段，避免与RAM stub重叠。本包不给现阶段可直接复制的设备执行命令；不把普通Flash app用load_ram加载。

## 可复现构建（只编译，不连接设备）

已使用 ESP-IDF v5.4，工具链/配置在 verification 中。先在自己的受控环境激活相同IDF：

```sh
. /verified/path/to/esp-idf/export.sh
python tools/embed_fixtures.py
python tools/check_host.py
./tools/build_only.sh disabled
./tools/build_only.sh enabled
```

脚本只允许disabled/enabled，固定执行 `idf.py build`。每个profile独立build目录/sdkconfig；配置改变后已有sdkconfig不会被defaults覆盖，应使用新的目录/config或在无设备情况下明确清理旧构建。host脚本只验功能，不输出可误解为实机的时间。

启用构建约216KB镜像；工作区为21888字节（host ABI检查，target静态布局可由ELF/DWARF再核对），运行时另申请40000字节Gray8，主任务栈16KiB；真正余量看实机heap/stack输出，链接成功不是运行成功。

## 输出与PSRAM

串口JSONL，schema1：header / memory / decode / warm_skip / skip / complete。每图3个cold/warm对；cold失败不伪造warm样本。`decode_us`是esp_timer微秒差，仅包围解码调用，**不含**夹具解压、分配、串口、采图；保留每次原始数据，成功/预期NOFIT/意外拒绝/意外成功分开统计，不把NOFIT延迟当成功吞吐。

`memory`记录internal free/minimum/largest、PSRAM free、当前任务stack最小剩余字节。minimum是自启动累计低水位，非该次调用独立峰值；compiler .su不是运行高水位。打印和系统中断仍可能影响系统状态，非硬实时保证。

默认纯RAM配置不支持PSRAM，必报not_opted_in。源码留有显式 `PEN_DECODER_BENCH_PSRAM` 编译开关，并仅在已经初始化的MALLOC_CAP_SPIRAM池非零时尝试；输入图和workspace一同迁移，栈/代码/输出不迁移，分配失败清楚skip。**本次没有提供或验证PSRAM可运行profile**，实际存在和对应电气/引脚/模式确认后才能建另一个非PURE_RAM配置。不要为了试PSRAM盲目启用octal/改变Flash模式；RAM-only内部数据结果不可直接当作Flash运行或PSRAM部署性能。

## 请求用户的最小下一步

先只要板子照片/丝印、现有程序是否要保留、电脑系统、哪个USB口及是否允许后续停机。确认和备份之后，再请求一次完整启动至complete的脱敏串口文本；我们会分别汇总正确坐标、NOFIT、cold/warm时间和堆栈余量。**当前没有S3 FPS、实机准确率、相机可用或<=380元整笔可行性结论。**

## 官方依据（2026-10-28查阅）

- [ESP-IDF v5.4 RAM构建/PURE_RAM_APP](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/kconfig.html#config-app-build-type)
- [esptool v4 RAM加载/限制](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/advanced-commands.html#load-a-binary-to-ram-load-ram)
- [esptool v4 只读识别/整片读取/image_info](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/basic-commands.html)
- [ESP Timer](https://docs.espressif.com/projects/esp-idf/en/release-v5.3/esp32s3/api-reference/system/esp_timer.html)
- [FreeRTOS高水位的ESP-IDF字节语义](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/performance/ram-usage.html)
