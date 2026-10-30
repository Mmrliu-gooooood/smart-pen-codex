# 验证结果（本地候选，2026-10-29）

## 已执行

1. **45项标准库unittest，全通过，0跳过（当前Linux）**。`unit_tests.log`；以真实SQLite、临时私有目录、子进程崩溃、mock Bleak执行。不是45台设备、不是无线互通。
2. `python -m compileall -q pen_receiver tests tools`通过。
3. `tools/crosswire.py`编译真实冻结`pen.c`与`pen_ble_core.c`：C生成的48B/三片与Python逐字节一致；真实Python重组成功；Python生成20B精确ACK被完整offer之后的C core接受，完整offer之前拒绝。`crosswire.log`。
4. 实际SQLite读回：journal_mode=`delete`，synchronous=`3`（EXTRA），fullfsync=`1`；最后一项在Linux只证明设置，**不证明F_FULLFSYNC硬件行为**。模式测试在45项中。
5. 可选依赖读取安装元数据：Bleak3.0.2/MIT、dbus-fast5.2.0/MIT；未导入/实例化真实BleakClient，未启动radio。`DEPENDENCY_EVIDENCE.json`。

## 覆盖矩阵

| 范围 | 测试证据 |
|---|---|
| framing | 长度/CRC/header/reserved/session/flags/confidence/page、丢片、乱序、重复片、过期、时间倒退、片0重开、seq16不匹配 |
| exact ACK | 当前连接三片齐全后才ACK；seq16碰撞/不同session/乱序record不合并，不累计ACK缺号 |
| 接收可靠性 | ACK丢失后重连去重；已有行+不完整重放仍无ACK；旧client晚callback不污染新client |
| 并发/取消 | 提交worker期间断连/取消：等待worker结束、保存可恢复、无ACK；有界notification overflow停止 |
| durable journal | 原始bytes同key去重；冲突锁停；初始化失败/空库/坏库/外来schema/坏row不自动重建 |
| 存储错误 | 真实SQLite `max_page_count`触发SQLITE_FULL；COMMIT前异常/已实际COMMIT后异常；子进程os._exit发生在COMMIT前/后 |
| 本地路径 | POSIX uid/mode、缺权限、文件权限过宽、软/硬链接拒绝；独占第二owner拒绝 |
| GATT/security | 属性缺失、INFO合成/未知拒绝；本地确认否拒绝；初始认证拒绝不当授权、确认后fresh INFO |
| UI防误用 | 原VALID仍诊断；UI_allowed=false、coordinate/window=null；u64十进制字符串；BEGIN/END仅派生边界 |
| 默认静默 | 无参数只帮助，未授权connect拒绝且未创建client；默认无需Bleak |

## 未执行/不能推出

- 无真实扫描、连接、配对、OS Bluetooth权限、手机、Windows/macOS平台运行、设备Flash或真实磁盘断电。
- Windows msvcrt锁/本地输入代码存在，**不是已验证Windows可用性**；DACL确认是人工声明。
- SQLite模拟错误/进程崩溃不等于存储介质突然掉电，无法证明OS/VFS/硬件确实兑现sync。
- 未做iPad/Android原生App、现有网页端到端、camera/provider/物理mapper、准确率/帧率/吞吐/功耗测试。
- 无安装/网络下载、仓库发布/上传、用户蓝牙身份/密钥读取。

## 冻结基线保护记录

最初重跑冻结BLE `tools/test_host.py`通过31场景三种编译模式；脚本会重写其3份host日志。
发现后立即逐文件核对源tar.gz：**整树archive_mismatches=[]，31个最终代码manifest项全部匹配，3日志逐字节相同**。
没有恢复/修改旧manifest来掩盖差异。证据`FROZEN_BASELINE_CHECK.json`及本目录重跑日志副本。
此后仅只读旧源码，编译输出在临时目录。原repo保持pinned commit，不修改。

此结果尚需后续独立代码审查；本文件不是独审结论或实机放行。

## v2独审负例闭环（作者重跑，非替代独审）

`review_regressions/`绑定独审复现脚本SHA。队列时间与导出身份脚本仅将import路径改到v2：
第二条callback跨度约2.1秒，现仅第一条ACK；两目标导出不再相同，VALID仍全部阻断。
Schema脚本保留攻击SQL，增加启动异常捕获及空client计数：现在JournalError、client_count=0、ACK_writes=0、durable_rows=0。
45项中另覆盖其他schema变形、写时新trigger/TEMP影子、多行、受影响行数、noop COMMIT、post-COMMIT IO/空readback、clone和合流冲突；不只屏蔽单条触发器名称。
