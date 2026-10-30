# 应用管线验证记录（候选，非硬件验收）

## 可复查来源

- 独立工作目录：`smart_pen_app_pipeline_20261028`。
- 本地基线：`84476fce1655b299147b2a47089a3f2d25f595de`；本次只交付新增应用/测试/文档，未修改旧 recorder/store/Flash ACK/erase-intent 核心。
- ESP-IDF：`67c1de1eebe095d554d281952fde63c16ee2dca0` (5.4)，使用官方本地源码/工具构建。
- 原仓像素生成验证：固定 `0f8b569176c77dad34aaf83bb008eb118c9f1208` 的 `digital_pen_ov5640/pc/src`。
- 精确源文件及 SHA256：`application_source_manifest.json`；最终构建/测试摘要在本文末尾追加。源变动后旧日志不代表新源通过。

## 最小独立审查集合

1. `firmware/application/pipeline.[ch]`。
2. `firmware/application_idf/main/{application_main.c,board_provider.h,board_provider_absent.c,CMakeLists.txt,Kconfig.projbuild}` 与项目/defaults。
3. `tests/test_application_{pipeline,actor,maintenance}.{c,py}` 及 `tests/test_application_stubs/`。
4. 基线依赖：`runtime/{recorder,contact_power}`、`storage/{store,storage_idf}`、`portable/pen`、`vision/roi_opt`、`codec/anoto`。
5. `docs/system/APPLICATION_PIPELINE_CANDIDATE.md`；可选分区profile另有独立验证说明。

## 覆盖层次

- **真实 C 管线**：提供Gray8像素→冷搜索有界解码→独立mapper合同→接触→持久记录→成功发送ticket→双安全快照ACK。映射器仅显式测试替身，绝无物理笔尖资格证明。
- **真实 app_main actor、窄SDK替身**：默认禁用/无provider不动存储；fatal ACK，camera/contact/IRQ/clock故障；离线睡眠/dirty/静默错误或超时/同步错误/迟到quiet和sync/落笔取消；满日志只读补传及安全维护、32会话、递增session；满且离线休眠；维护guard竞态、异步quiet、USB策略改变、等待期间dirty变化。
- **真实store维护语义**：未ACK不擦、ACK后32会话回收、擦除失败留下持久intent并open恢复、旧session ACK拒绝、睡醒未ACK记录重放。
- **SDK目标链接**：只证明官方SDK/目标ABI编译链接及分区容量，不证明设备跑通。默认及enabled-compile提供者均为NULL，未驱动相机/LED/无线；可选8MiB配置也没有真实provider。

## 再现

```sh
python software/verify_host.py --upstream-pc-src /path/to/pinned/digital_pen_ov5640/pc/src
python -m unittest discover -s tests -p 'test_application*.py' -v
PEN_APP_TEST_NDEBUG=1 python -O -m unittest discover -s tests -p 'test_application*.py'
ASAN_OPTIONS=detect_leaks=0 PEN_APP_TEST_SANITIZERS=1 python -m unittest discover -s tests -p 'test_application*.py'
# leak sanitizer仅因当前ptrace环境限制关闭；ASAN/UBSAN保留。
export IDF_TOOLS_PATH=/path/to/smart_pen_sdk_20261028/tools
. /path/to/smart_pen_sdk_20261028/esp-idf/export.sh
idf.py -C firmware/application_idf -B /outside/source/build-disabled \
 -D SDKCONFIG=/outside/source/disabled.config build
idf.py -C firmware/application_idf -B /outside/source/build-enabled \
 -D SDKCONFIG=/outside/source/enabled.config \
 -D 'SDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.enabled_compile.defaults' build
```

## 尚未完成 / 不应外推

没有真实SC035HGS时序/电平/镜头资格化、DMA/压力/电源/GPIO驱动、物理笔尖标定与姿态mapper、NimBLE服务及安全状态串行实现、最后睡眠/维护原子门、实测掉电/温升/续航/吞吐。固定纸页配置不支持自动换页。Flash是整区回收，不是无限滚动日志；满且未ACK必须拒绝新写入。同步Flash操作不能被actor强行抢占，deadline只在调用边界检测，提供者必须测得并保证单次操作有界。没有OTA执行适配器，未操作密钥、eFuse或设备。禁止把本次target build等同于整笔可用或批准刷机。

## 2026-10-28 最终合并验证

- **39个源码/测试/主说明文件**，`application_source_manifest.json` SHA256：`99ff5c16021f193bc3b3478d3ee73ccf73b336e7ebc3cac512c76a44caeb2e47`。
- 完整主机入口：**83测试，0跳过，全过**，21.653s；`application_host_gate_final.log`。
- 新应用3组测试正常、Python `-O`+C `-DNDEBUG`、ASAN+UBSAN均过；分别见主机门、`application_optimized_test.log`、`application_sanitizer_test.log`。实际actor含25个编号场景及无提供者/默认禁用分支。
- 8MiB profile另含6组合（profile开/关×normal/NDEBUG/ASAN+UBSAN）；官方分区CSV→bin→CSV与真实C运行合同一致；重叠/应用未64KiB对齐/越过8MiB均被官方工具拒绝。见 `application_flash8_merged_validation.json`。
- 官方SDK **disabled、enabled-compile、8MiB enabled-compile 三配置均链接成功**，源内provider仍NULL；未执行日志末尾由SDK自动打印的刷机命令。仅交付日志/hash，不交付可误刷设备的BIN/ELF。

| 配置 | app字节 | SHA256 |
|---|---:|---|
| default disabled |192704|`72cffdbf266da1e295fd94688219a43c6ad31e292d9d3762ad1d3807bc8743e7`|
| enabled-compile / default分区 |214656|`adfe0479ba6ef6c21cc9611083216fa9c5051bb91a3d6e161c668500abdb848e`|
| explicit 8MiB / enabled-compile |215424|`dc176616937e36b74a20d68bfe85d624fb694bd195373d261d668bd298340997`|

8MiB profile每OTA槽2,097,152字节，app可容纳。净日志4,063,232字节/63,488槽，60条/s理想上界1058.13s，120条/s上界529.07s；额外边沿/GAP记录减少可用时长；session/seq已含在64字节槽内，不另计额外session槽。默认分区无日志，容量0。真实8MiB与16MiB均须实物核对，本profile拒绝16MiB；这些数字不是4小时离线缓存或电池续航承诺。

完整二进制/分区hash、配置开关及编译器各函数静态stack usage在 `application_sdk_builds.json`，不是栈高水位或完整调用链测量。独立审查报告由另一审查目录生成，不冒充本作者自审。
