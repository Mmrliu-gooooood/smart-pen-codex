# V3纯RAM目标基准：V2后的最小独立后继（未上板）

**仅本地编译/链接/静态及host功能验证，未连接、识别、加载RAM、刷写或上传任何设备。不要执行SDK构建末尾自动打印的flash/write_flash建议。** 原V2工程与生产候选源码保持不变。

## 差量与来源

基于`smart_pen_continuous_target_benchmark_20261029`的安全/完整性框架，新增V3 core、1536B seed workspace、9幅固定图、refine统计及只读诊断插桩。`DELTA_FROM_V2.json`列出改变/新增/复用文件；不复制旧build、旧审查历史或大仓库。普通源码目录可独立重建，源绑定见`SOURCE_BINDINGS.json`。

V3 core、codec及所有PGM逐项匹配已独审冻结的 `V3_SNAPSHOT.json` SHA256 `1636084759c3ebfc358574f669ea5292b11ae4421145401e7c2ccaed12664ccf`，选自该候选明确的delivery allowlist。冻结原core仍是旧函数体，仅链接入口改名隔离。`fixtures/manifest.json`是返回后oracle，不向C传坐标、方向、pitch、角度、crop或transform答案；输入只有原灰度图、200×200尺寸、纸张边界/section和工作区。

## 同图冷启动对照

9幅完整200px原始像素：5/6/7mm phase0，45°恢复，5.1mm恢复，无完整窗口，深边墨迹，9mm超密度压力（范围外），实际65seed溢出。冻结原core与V3 wrapper都读同图。正常V3成功5幅、拒绝4幅；拒绝分别为NO_GRID(-3)、DETECTION(-2)、DETECTION(-2)、AMBIGUOUS(-4)。旧core在本组9幅均拒绝。

65seed图保持生产64上限，**不改编译阈值造溢出**：统计期望coarse864、seeds65、iterations0、models0；result所有字节保留。预处理提前拒绝的墨迹/密度图没有进入refiner，统计应全0、trace_calls0，不伪报执行搜索。

这些是理想合成上游0.3mm连续纸张/独立负例，不是打印或相机照片。V3恢复了此前诊断的19尺度及16旋转有完整窗口例，但20无完整窗口例仍不得补点；此小型9图不是整套覆盖统计的替代品，也没有物理笔尖、相机、倾斜/投影或实时保证。

## 计时与插桩契约

- 仅cold，原core为NULL prior，wrapper无prior。不虚构warm或cache-flush。
- 整个V3 wrapper调用计时包含ROI复制/边缘处理、粗搜、refit、严格解码与变换，以及诊断捕获的少量开销；夹具解压、分配、输出在计时外。
- V3失败保持result，不能从失败result读seed统计。因此benchmark专用`--wrap` shim只复制下层**返回的**diagnostics，不改输入、结果、阈值或核心源码。header明确`instrumented=true`、scope为continuous_v3_only；每条V3数据instrumented=true，旧core=false。**两者插桩不同，不能把绝对时差全归因于算法；不是未插桩生产性能。**
- 实际Xtensa反汇编必须验证wrapper调用确实到`__wrap`再到real；不以host mock替代。目标记录调用次数；与fixture的返回后期望不符，或搜索状态却无coarse统计时fatal并终止，不输出complete。成功result统计与trace统计、失败统计及硬上限均由parser核对。

## RAM与格式安全

真实目标static_assert：core21888B +64×24B seeds +9216B crop = **32640B**，单个internal heap工作区，两个decoder串行复用core部分，不分配第二工作区。原图另40000B，合计**72640B**，不含RTOS/主栈/printf/静态夹具。主任务栈16KiB，workspace不放栈。

纯RAM镜像的只读夹具也占internal DRAM。为避免9图过大，采用**无损palette-RLE**：最多32色，uint16低5位索引、高11位为1..2047长度，host验证逐字节恢复及SHA256；目标验证palette/长度/边界。原始PGM未改，解压不计入decode时延。

有效配置关闭nano，源码#error阻止开启；实际full libc printf/dtoa/snprintf链接证据保留。启动用snprintf检查超32位整数和double，失败fatal；parser还要求format_probe。目标自检尚未运行，host模拟不代替目标libc。新库printf动态heap/stack开销未知；link fit不等于实际72640B分配成功，任何分配失败fatal，不能用部分结果统计通过。详见verification/RESULTS.md和RAM_ACCOUNTING.md。

## 不变的实物安全门

默认benchmark disabled，纯RAM不初始化Flash/PSRAM，无相机、LED、压力、电池、Wi-Fi/BLE、NVS、OTA、非易失写/eFuse/密钥操作。禁用task watchdog只为实验冷搜，不是产品固件设置。UART0 115200及secondary USB控制台会输出，相关焊盘不是静止；物理外设先断开并核板图。

N16R8标记不是已核实的Flash/PSRAM容量、模式或分区；不假设现有digital_pen为空。RAM执行仍需ROM下载/复位，会中断旧程序、改变易失状态。**先照片/板型/USB口/系统识别，用户同意中断，再只读识别、整片实际容量私密备份及同板恢复计划，最后才制定手动RAM步骤。** 不无条件擦除、刷写或force绕过安全限制；Flash加密/安全启动设备不能假设备份可恢复。备份可能含凭据/笔迹/密钥，保存在本机非仓库私密位置，不上传GitHub/Library或发送助手。这里不附设备执行脚本。

## 无设备复现

```sh
. /verified/path/to/esp-idf/export.sh  # 使用ESP-IDF v5.4
python tools/embed_fixtures.py
python tools/check_host.py > verification/host-functional.json
python tools/check_geometry.py
python tools/test_serial_parser.py
./tools/build_only.sh disabled
./tools/build_only.sh enabled
```

profile独立config，已有SDKCONFIG不被defaults覆盖。正常检查只依赖本目录；`prepare_independent_geometry.py`是一次性源证据提取器，需要已冻结候选，不是正常构建步骤。`check_static.py`需先在本机生成有效config、map、nm、image_info及反汇编摘录。

后续获准实机日志才能运行`python tools/summarize_serial.py PRIVATE_LOG`。schema3绑定fixture/source/scope，严格完整顺序、18种fixture×decoder组合、repeat、crop/方向/矩阵、refine及内存/格式探针；每组默认3次共54调用。错误/缺失/fatal拒绝整体统计；功能错误exit1，功能一致仍exit2和`identity_verified=false, overall_pass=null`：日志头不是物理身份认证。不输出S3 FPS或整链路速度承诺。

官方参考：[v5.4 RAM/nano配置](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/kconfig.html)、[esptool RAM限制](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/advanced-commands.html)、[只读识别/整片备份](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/basic-commands.html)。
