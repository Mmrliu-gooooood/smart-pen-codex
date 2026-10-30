# v2本地软件验证结果 — 2026-10-29

**结论：v2修复v1真实reset链的表边界遗漏，已通过新的完整启动链/错误回归与隔离SDK双编译；尚待独立正确性复查。无相机/板卡/物理图像证据。未授权运行，profile=0、默认OFF。**

v1原包保留不改，不再作为可运行驱动候选；根因和修复范围见`docs/V2_CORRECTNESS_FIX.zh-CN.md`。原独审流程中断，没有可宣称的完整通过报告。以下是本v2实现者重新运行的结果。

## 已通过

|验证|结果/范围|
|---|---|
|便携采集core+冻结app ABI|251个assertion PASS：禁用/未知profile、ID/时钟/引脚参数门、精确帧大小、短长帧、错误stride/格式、过期/未来/重复帧、借用/二次归还/错误token、三次超时、失效清理/锁死、显式ROI边界/原点|
|真实SC031GS补丁源+SCCB mock|PASS：正确/错误型号、ID任一字节读取失败、枚举越界、模式表首/第二次写失败、窗口读失败、VGA窗口写值|
|真实sccb-ng checked-read源+I²C mock|PASS：缺handle、NULL输出、即使I²C错误回填0x31仍拒绝；成功返回原字节|
|真实有界table writer|12119检查PASS：reset+两组mode表、缺失/提前/错误终止项写前拒绝、每个表写失败立即停止（不资格化200模式）|
|真实esp_camera→probe→reset链|7940检查PASS：109个逐写失败、6个逐读失败均清理且不继续写；错误型号、ID读失败零初始化写；正常init/deinit、SCCB/HAL错误、bounded API|
|真实HAL+ll_cam/OS替身|634检查PASS：8类分配失败、任务/ISR失败清理、tick回绕、超时/GDMA reset上限、单fb归还、HAL软件时戳调用顺序。tracked mock分配归零不是所有SDK泄漏验证|
|真实IDF backend+硬件替身|74检查PASS：内存/power/ID与窗口各读失败/时钟/时戳/stop-held/timeout/单boot退役|
|扩展portable|79353检查PASS（含原251，不能当不重复计数相加）：两轴95..257 exhaustive ROI边界、旧lease、timeout/cleanup|
|主机编译|GCC C11，候选代码Wall/Wextra/Werror/Wconversion/Wshadow；ASan+UBSan通过。第三方测试对原源未用参数/变量关闭对应warning；真实HAL主机夹具另明确关闭原代码sign-compare及32/64位指针转换warning，不修改候选core严格warning门|
|实际IDF disabled|ESP-IDF v5.4、ESP32-S3，编译/链接/镜像大小检查PASS|
|实际IDF enabled-compile|同上PASS；真实esp_camera_init、SC031GS detect、checked-read、帧读取/ROI等符号在ELF，非host stub链接|

首次LSan因执行环境ptrace限制失败；测试脚本显式`detect_leaks=0`重跑后ASan/UBSan通过，**不能称为LSan/泄漏验证通过**。没有隐藏该边界。`host-tests.log`、`idf-*.log`、`linked-symbols.txt`、`size-*.json/txt`与`stack-usage-enabled.txt`保留证据。

## 实际静态构建大小

|项目|disabled|enabled-compile|
|---|---:|---:|
|.bin字节|218016|259792|
|IDF total image size（未含padding）|217876|259652|
|static IRAM|16383|16383|
|static D/IRAM|58783|61683|
|Flash非RAM代码/常量等|147166|186170|

IDF报告此16KiB IRAM区域只余1B，同时D/IRAM显示280077B remain（enabled）。这是链接分区统计，不是开机空闲heap、内存碎片、PSRAM容量或整笔加入BLE/decoder后的余量保证。运行时峰值未测。

## 动态内存边界（由固定源静态推导，不是测量）

- 单一Gray8 VGA fb=640×480=307200B，配置放PSRAM。无第二帧/复制整图缓冲；软件ROI仅借用原始buffer。
- PSRAM DMA关闭时，固定HAL算法在32768B DMA上限下算出node3840B、half15360B、DMA buffer30720B、8个descriptor、20次copy/帧。descriptor占`8*sizeof(lldesc_t)`；另有cam对象、frame对象、队列、I²C/GDMA/ISR元数据及allocator开销，**未合并冒充精确峰值**。
- camera task配置4096B栈。候选编译器单函数stack记录最大`hw_open=176B`，profile_validate112B、ROI96B、get80B；不是调用链/ISR/SDK峰值测量。应用decoder工作区不包含在本图像适配器中。
- 启动前检查最大连续外RAM块至少307216B、内部DMA块至少32768B；仅是必要保守门，不是所有后续allocation成功保证。真实SDK分配仍逐层检查。
- 当前两套**编译夹具SPIRAM关闭**，app_main也不初始化PSRAM。真实运行必须审核具体PSRAM/引脚/启动配置；本包不提供此资格，也不分配帧。

## 修复与保留边界

第一次IDF构建暴露esp_camera.h隐含JPEG头依赖；通过明确Gray-only构建宏和最小真实源组件解决，而非加入假JPEG实现/下载未知库。v2在全新`smart_pen_camera_capture_v2_build_20261029`目录实际完成disabled/enabled双编译，最后源无warning/error。仅build，不flash。

默认/开启编译都不启动相机。host fake没有伪造物理sensor证据；实际backend没有已审核profile。真实backend一旦尝试初始化即退役到本boot结束，不自动重试/暖启动/power-cycle；这不是已完成实机错误恢复。无200×200传感器模式、无曝光资格、无真实FPS/PCLK/焦距/图像、无mapper/VALID、无压力actor队列、无完整整笔runtime。

HAL时戳只代表启动DMA/人工VSYNC之后的软件boot-time采样，**不是首DMA/曝光时间**；pressure/曝光与帧的关联仍未资格。

## 冻结与交接

源码清单与SHA256由`tools/manifest.py`生成。`frozen_headers.json`为原应用头文件逐字节副本hash；第三方补丁完整保留，不修改原SDK/冻结应用树。源码归档不包含.git对象、构建二进制或私有厂商文件。未来接入应先独立review本候选，并保持所有实机门关闭。
