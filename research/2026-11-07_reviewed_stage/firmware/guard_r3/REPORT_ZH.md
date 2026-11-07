# 输入、维护与 ACK 安全实参：独立纯 C 候选 R3

2026-11-07。**NOT ADOPTED / HOST ONLY / NOFAB / NOPOWER。** 冻结工程、默认关闭开关、CMake 和 absent board provider 均未修改。没有安装、删除、推送、刷写或上电。源码位于独立 candidate/，所有补丁均未应用到冻结工程。

## R3 结论：确有持久误确认及后续回收风险

先读 R2 独立复核，再用实际 C 代码建立执行负例，确认两个公开低层 ACK 入口会把非法安全实参当真：

- pen_store_ack(..., authenticated_peer=2) 接受当前 offer 的正确 session/seq，写入持久 ACK。
- pen_storage_idf_ack(..., encrypted=2, 其余安全实参=1) 接受格式、CRC 和当前身份正确的 ACK 包，也写入持久 ACK。

原版实际宿主输出分别为：

`authenticated=2 accepted; after reopen offer=1; legitimate-idle reclaim=0 erases=1`

`field=0 fact=2 accepted; reopen fragments=1; legitimate-idle reclaim=0 erases=1`

这里 offer/fragments 返回 **1 表示已无待回放记录**，reclaim 返回 0 表示回收成功。因果链是：原本待确认的记录 → 非法安全实参被当作授权 → ACK 标记持久化 → 重开后不再回放 → 后续单独的合法 idle 回收擦除模拟记录。**ACK 函数本身不直接擦除。**

触发前提是调用者把非法非零整数作为真实链路安全事实传入，且 offer 身份/包内容正确。这些安全实参不是从 ACK 载荷解析出来的字段。没有证明远端攻击者可以直接控制它们，也没有证明实际设备发生数据丢失。

**当前主应用 pen_app_ack 原本已严格要求 current/receipt 的四个字段==1，并检查非零匹配 epoch 和已接受发送票据。本轮确认该路径拒绝非法事实；不能把低层 API 缺口写成现主 actor 已被绕过。**

## R3 修复范围

相对 R2 仅再改 **2 行（+2/-2）**：

1. store.c：authenticated_peer 必须恰好为 1，否则返回既有 -3。
2. storage_idf.c：encrypted/authenticated/bonded/approved_peer 四项都必须恰好为 1，否则返回既有 -3。

只有修改 store 不够：旧 IDF ACK 入口校验后向 store 传的是常量 1，因此也必须在该入口拒绝非法事实。拒绝发生在 ACK 写入、sync、offer/cursor 消费之前；不锁死合法待确认记录，后续真实许可=1仍可重试。

20 字节 AK v1 包、保留字节、CRC、session/seq 绑定、ACK body/commit 格式、两个同步点、错误返回和已有故障锁存均未改动。没有新传输协议或凭据持久化。

完整候选相对冻结原件共 **5 个源文件、+21/-6 行**。结构体、函数签名与默认关闭状态保持。

## R1、R2 保留的修复

- CP 的8个 uint8_t 输入、pipeline 的5个输入严格限定0/1；非法输入不产生本次动作、消费帧或继续录制。CP本身不新增永久故障锁存，recorder负责停录。
- actor在接收 poll=0 新事件时先校验，覆盖录制与回放，且早于 pending_transactions 覆盖字段。非法事件通过 report_status 的独立 **actor_error 参数**报告 -110，不表示 status.last_error 被写为 -110。poll=1 的 scratch output 仍被忽略。
- replay-only 维护 guard 只允许1；0保留屏障前取消/resume，负值或大于1终止。正常 sleep-prepared 分支原本已要求1，未改其不能恢复旧session的语义。
- pen_store_reclaim 的 safe_idle 只接受1；仍要求停止录制、无offer/fault、必要回调齐全、所有提交已ACK。
- 通用 pen_store_open 恢复 intent 只允许0/1。0不擦；1完成已有持久授权的恢复并清intent；非法值失败、保留介质。真实 storage_idf 的 NVS getter原本已校验，本候选没有把它当作原始漏洞。

MAINTENANCE_ENTRY_MATRIX.json、ACK_ENTRY_MATRIX.json 分别列明各入口的合法、取消、非法、故障行为。R2的维护负例从全ACK夹具开始；R3新增的是**此前ACK授权实参错误导致记录被错误标记**的另一条因果链，不是R2回归。

## 最终本轮验证

现有 GCC 14.2.0、Python 3.12.14，无安装。复现命令：

`python3 -B firmware_boolean_guard_candidate_20261107/run_host.py`

最终完整脚本执行 **65次：56次正常通过，9次冻结原版负例按预期失败，0次非预期失败。** 9个原版失败包括先前7项和新增两个ACK影响负例；它们不是候选失败。初步调查的3次运行另存 R3_INVESTIGATION.log，不混计为最终脚本执行数。

本轮重跑内容：

- 原版/候选的既有 contact、recorder、storage、maintenance、pipeline、actor enabled/disabled、storage_idf mock enabled/disabled。maintenance、pipeline、actor另跑NDEBUG。带assert的旧测试保持断言开启。
- R1的全非法uint8_t逐字段边界及合法组合、R2的维护和恢复整数边界，全部重新运行。未ACK保留、合法回收、intent恢复行为继续通过。
- 新 store ACK测试：非法 signed 值 -255..255（排除1），以及INT_MIN、INT_MAX、-65536、65536。确认拒绝不写、不sync、不消耗offer、不改变全部模拟介质；重开后仍回放且拒绝回收，随后合法ACK与回收成功。
- 新 IDF ACK测试：四个安全整数分别做同样边界测试；保留全介质和offer。另覆盖错误magic/version/reserved/CRC/session/seq、19/21字节长度、disabled context、重复ACK及合法重试。
- 主应用既有严格门：2040组 current/receipt 非法布尔字段，另测零epoch、旧receipt epoch和两侧已换新但发送票据仍旧的epoch，全部拒绝；原版也通过，不能宣称为本轮修复。
- 新纯C ACK/app测试使用显式CHECK，在NDEBUG和NDEBUG+UBSan两种配置通过。IDF补测复用含assert的宿主API替身，以断言开启的O2与UBSan运行。无UBSan报告。
- 既有 storage 的52个data、12个ACK字节中断、512个erase中断模型重新运行；新增ACK两次program/两次sync的4个故障点。

**最后一次ACK sync失败属于结果不确定。** 在本轮同步内存夹具中，完整ACK marker已经写入，重开会识别该合法ACK；前三个故障点则保留回放并可重试。没有把所有错误返回都声称成“ACK未发生”，也不将这种模型外推为真实Flash掉电保证。

首次R3完整执行曾因测试计数预期错误停止：测试把重开时 pen_log_open 的一次sync也计入了ACK总数，却仍预期总数为2。只修测试为“ACK入口前后的两次sync差值”，候选代码未为此改动；最终65次已完整重跑。说明与失败片段保存在 R3_TEST_ORACLE_CORRECTION.md。

## 来源与文件

最终65次运行所读 **46个冻结源、头、夹具**运行前后SHA-256一致。上游拿起/休眠合同25个固定来源重新核验匹配。证据为 RESULTS.json、HOST_TESTS.log、CONTRACT_SOURCE_RECHECK.json。各候选/测试文件最终哈希在 PACKAGE_MANIFEST.json。

已读独立R1/R2报告及错误恢复证据，来源绑定分别见 R2_REVIEW_BINDINGS.json、R3_REVIEW_BINDINGS.json。独立审查的场景数不冒充本轮运行结果。

- candidate/：5个完整源码覆盖。
- boolean_guard.patch：对冻结工程的完整R3补丁。
- ack_guard_r3.patch：对R2的两个ACK条件增量，不与完整补丁重复应用。
- maintenance_guard_r2.patch：历史R1→R2增量；R1、R2完成证据分别保存在r1_evidence/、r2_evidence/。
- test_ack_guard.c、test_idf_ack_guard.c：新增ACK负例与回归，其余测试继续保留。
- build/中的二进制是本机测试程序，frame.gray是合成夹具，均不是设备固件。
- 总新增（含保留历史证据）小于1MiB，不删除旧产物。最终大小以 PACKAGE_MANIFEST.json 清单为准。

## 未完成与适用边界

严格整数域只是输入约束，不是认证实现。调用者仍必须提供来自当前真实加密/认证/绑定/批准链路的事实；已经错误归一化或伪造为1的值不能被该门识别。旧低层API的安全来源、发送资格和epoch关联没有重新设计，当前主应用的更严格票据机制继续保留。

没有 full host aggregate（本机仍缺cv2、bleak等该入口依赖）、ESP-IDF目标编译、实际BLE/USB/GPIO/Flash/NVS/掉电或设备测试。真实provider、最终sleep竞态、原子idle hold、队列/generation、相机准备、可靠采样、功耗与状态UI仍未完成。safe_stop被调用不证明安全断电，recording仍是session开放而非正在出墨。

新候选应独立复核后再决定是否合入新的默认关闭版本；不得凭宿主通过启用硬件或宣布整机完成。
