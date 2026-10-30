# BLE候选最终软件验证（2026-10-29）

## 通过的不同层次

| 层 | 实际结果 | 不代表 |
|---|---|---|
| 冻结应用完整host gate | 83 tests、0 skipped、PASS；`baseline_host.log` | 真实摄像头、物理mapper、无线或Flash实物 |
| 作者portable/actor C | 31场景，normal / NDEBUG / ASAN+UBSAN均PASS，另Python独立分片/CRC核对 | MCU时序/实际RTOS实时性 |
| 独立额外复验 | 47 core + 12 actor/grant + 11 IDF mock组及4初始化故障子进程，各normal / NDEBUG / ASAN+UBSAN PASS；详见独立review | BLE协议栈硬件互通 |
| 官方IDF真实编译链接 | ESP-IDF v5.4、S3、default OFF和enabled compile均PASS，无编译warning/error；10个入口符号真实保留 | 已启动host、广播、配对或已刷机 |

以上数量是各套不同测试/场景/组，不相加成“总独立测试数”。ASAN关闭leak detector，没有把泄漏检查计入验证。

独立IDF测试编译**真实`src/pen_ble_idf.c`**，外部API用窄stubs替身；8个pthread RPC调用者验证序列化，
覆盖timeout后释放调用者缓冲再处理late event、mbuf失败所有权、连接/安全/MTU、配对期限、NVS失败/首启IRK、
legacy/弱bond、quiet错误、reentry拒绝。不是运行真实NimBLE控制器或FreeRTOS硬件调度。

## 实构建绑定

`verification/build_report.json`为机器可读权威记录，包含精确源manifest hash、SDK commit、关键Kconfig、ELF/BIN/分区hash。
最终SDK项目BIN：
- OFF：208,352 B，SHA256 `fdfe155a247a82e49f29f71aba626d0a516aafb39e10b63c09346c0b0666a705`
- enabled compile：531,840 B，SHA256 `fb8b9ef597bd031ebab71df06dc656cc5fb7ea211b410d220bc3adbd71b8ba92`

最终build tree在兄弟目录`smart_pen_ble_build_20261029/{disabled,enabled}`；不包含于精简源码包。
这两个镜像的入口均不启动NVS/radio；默认版还核无`ble_gap_adv_start`链接符号。
仅enabled编译配置链接真实BLE实现，不等于运行授权。

SDK pin `67c1de1eebe095d554d281952fde63c16ee2dca0`；工具Xtensa GCC14.2.0/esp-14.2.0_20241119，
SDK Python环境CMake3.31.10/Ninja1.13.0。本轮不下载新依赖。旧tag部署前仍需安全补丁审查。

`frozen_unchanged.json`复核冻结应用原39文件manifest与最小依赖副本均未变化。
源码hash用`python tools/report.py`再生；不同绝对路径/时间可能改变ELF/BIN hash，不影响固定来源审计。

## 独立审查发现已修复

- 不用分别RPC的安全快照冒充最终ACK当前态：采用显式单次grant授权线性化，不在host线程执行Flash。
- quiet不能忽略停广告错误；断连/换epoch清订阅与MTU。
- 首次LOCAL_IRK是官方启动路径，不能被“尚未pairing”门误拒；真实写失败仍锁存。
- callout stop不保证移除已排队event：独立测试曾复现“已批准会话被迟到timer撤销”；现在按当前deadline/approved判定。
- 检查callout初始化失败、部分start一次性锁存；host_task指针用atomic消除首次RPC发布竞态。
- old legacy/弱/缺LTK的已有bond不能因SC-only新配置获得权限；write回调失败不能被bonded位掩盖。

## 明确未执行/未完成

没有设备连接/刷写、radio运行、真实配对、账号或实际密钥生成、NVS擦除、GitHub推送。
没有原生iPad/Android App、iOS Web Bluetooth实现或手机互通结果。
没有吞吐/电流/续航/热/真实掉电/实物Flash延迟/整笔有效书写测量。
USB可见显示+本地确认UI、量产无屏配对、真实camera/mapper及最终actor板级接线仍是门禁。
新grant契约与接线要求见`docs/INTEGRATION.zh-CN.md`，不能仅打开Kconfig后声称冻结actor可直接安全使用。

## 从空配置再现

另用全新`smart_pen_ble_build_fresh_20261029`和全新SDKCONFIG，直接读取发布的两份defaults，
OFF及enabled再次全部compile/link PASS。记录在`fresh_build_report.json`与`idf-fresh-*.log`，
关键安全Kconfig与原最终构建一致，BIN长度相同；因构建路径/时间变化hash不同，不混称为同一二进制。
打包后的独立review源码也已通过`tools/test_review.sh`重定位复跑，见`packaged_review_reproduction.log`。
