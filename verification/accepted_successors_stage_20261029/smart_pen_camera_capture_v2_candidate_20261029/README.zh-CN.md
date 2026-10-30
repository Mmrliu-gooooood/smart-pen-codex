# 点阵笔 ESP32-S3 / SC031GS 采集候选 v2（2026-10-29）

**独立软件候选，默认 OFF，已审核板级 profile 数量为 0。不是用户已购 SC035HGS 的驱动，不是可直接烧录/接线的固件。**

## v2重要更正

v1真实reset链遗漏了公共表终止项，独审确认表末尾越界；v1不得作为可运行驱动候选。
v2新增显式数组长度、全表终止策略先校验及完整启动链/逐读写失败回归。
详见 [v2修复和证据边界](docs/V2_CORRECTNESS_FIX.zh-CN.md)。独立复查尚待进行。

## 已做

- 固定官方 `esp32-camera@f37e65608f709bd94846dee01d947f02ae07c0b0`，真实 ESP-IDF v5.4 / ESP32-S3 编译链接。
- 仅 SC031GS、Gray8、640×480、10 MHz XCLK 路径；官方表标注约25fps，**并未测得25fps/PCLK/图像**。
- 严格 ID 读取状态、board allowlist、时钟量化/寄存器回读、尺寸/stride/长度、时戳、帧所有权与连续超时门。
- 官方源局部安全补丁：SCCB checked-read、模式表错误传播/枚举边界、像素格式错误传播、任务创建错误、有界取帧。没有移植 SC035HGS 寄存器，没有猜测曝光/PLL。
- 单帧借用零拷贝；显式软件ROI子视图保留640stride、全帧尺寸和左上偏移，不缩放、不等同传感器200×200模式。
- 按原应用 `pipeline.h` 的逐字节冻结头文件构造 Gray8 输入。**没有提供 actor/provider、pressure队列、mapper、标定或 VALID 记录**。生产profile为空；主机像素仅SYNTHETIC。

## 再现（只测试/构建）

```sh
python tools/test_host.py
tools/build_idf.sh
python tools/manifest.py --check
```

依赖本地 `../smart_pen_sdk_20261028` 官方SDK，可用 `PEN_SDK_ROOT` 指定路径；外部构建目录用 `PEN_CAMERA_BUILD_ROOT`。
组件管理器关闭，构建不下载依赖；只编译采集所需公共源，不编译/伪造JPEG转换库。
默认和enabled-compile的 `app_main` 都只报告禁用并返回，不初始化相机/PSRAM、不写NVS、不启动BLE。
两份配置均关闭PSRAM启动初始化能力；未来必须按实际芯片/板号审核PSRAM后另立运行配置，不能拿本镜像直接采图。
SDK日志自带的刷机提示不是本项目操作步骤；本轮未连接设备/刷机/上电/采购/上传。

- [窄设计与公开源码证据](docs/DESIGN_AND_EVIDENCE.zh-CN.md)
- [帧、错误、ROI与应用接入合同](docs/FRAME_CONTRACT.zh-CN.md)
- [安全接线与实机门](docs/SAFETY_GATES.zh-CN.md)
- [实编与测试结果、内存边界](verification/RESULTS.zh-CN.md)

未碰原冻结应用树。源码文件清单与SHA256见 `verification/source_manifest.json`；官方差异见 `verification/esp32-camera.patch`。
