# 离线笔迹回传：跨 C 存储与主机持久化的 ACK 验证

日期：2026-11-02。状态：**隔离验证成果，不是产品固件集成，不解除 NOFAB / NO POWER。**

## 本次完成了什么

采用 GitHub 已发布的 `d413b45684d18c744dcfe550ec80136d86856f75` 精确源码，编译真实 `firmware/storage/store.c` 与 `firmware/portable/pen.c`，用 Python ctypes 连接真实 `Journal`、SP 包编解码、BLE 分片/重组及 ACK 编解码。所有源文件字节与该提交的 Git blob SHA-1 一致；没有修改活动固件、主机接收器或仓库。

新增 12 个测试方法，Python 普通模式与 `-O` 均通过，包含：

- C 离线存储 → 48 字节包 → 三个 20 字节片段 → 重组 → SQLite FULL commit → 精确 ACK → C ACK 标记 → 安全回收的闭环。
- 主机保存后 ACK 丢失、主机实际子进程以 `os._exit(73)` 退出、笔端状态重启后的重放。已保存记录不会重复插入。
- 全部 12 个 ACK 字节中断位置，两个 ACK sync 失败位置；失败后不擅自擦除日志。
- SQLite 写入失败和在插入后注入 commit 异常，均不产生 ACK；后者确认回滚后记录和 frontier 都为空。
- 已存记录内容冲突、错误设备、错误会话、未经认证以及未 offer 的 ACK 被拒绝。
- 主机存在序列空洞时不给更高序列 ACK。
- 主机累计 frontier 高于当前笔端 offer 时，累计 ACK 被 C 正确拒绝；精确 ACK 使逐条回放完成。

另外重跑该提交已有 C storage 测试，通过原有 52 个数据写入中断、12 个 ACK 中断、512 个擦除中断及其他存储检查。这部分属于既有覆盖，不计作本次新增创新。

## 必须明确的接口合同

当前 `Journal.accept(raw)` 返回每设备/会话的**连续持久化最大序号**。当前 `pen_store_ack()` / `pen_app_ack()` 只接受**本次已 offer / 已发送的精确会话与序号**。

因此，面向产品的主机适配器不能直接把累计 frontier 当成本次 ACK 序号。测试中的提议合同如下：

1. 从实际包解析 device、session、seq，先验证批准的设备身份；同时由真实链路层执行认证、绑定及连接 epoch 检查。
2. `Journal.accept(raw)` 必须成功返回，且持久化 frontier 不小于当前包 seq。
3. 发送 `(当前包 session, 当前包 seq)` 的 ACK，而不是 `(session, frontier)`。
4. 插入/提交失败、同一设备会话序号内容冲突、身份不符、记录尚有前置缺口时，不发 ACK。
5. 笔端仍逐条校验当前 offer、实际发送授权、链路安全与连接 epoch，再落盘 ACK 标记；只有满足既有安全回收门才能擦除。

`exact_ack_after_commit()` 只是可执行测试合同，未接入产品。`software/windows_ble.py` 明确是 SYNTHETIC BENCH 接收器，不应以此测试宣称现有产品蓝牙已经集成或断言该 bench 接收器就是产品 bug。产品板级 provider 仍缺失，完整无线链路尚未实测。

累计 frontier 场景作为接口兼容性对抗输入：未来接收缓存、重复回放、另一客户端路径或恢复过程可能提供这种状态。本次没有声称当前严格串行 stop-and-wait 单一设备路径必然自然产生它。

## 模型与限制

- flash_fixture 是 16×64 字节的 NOR 风格模型；program 逐字节立即持久化，只允许 1→0；`sync` 可以返回错误，但不会撤销已经写入的字节。
- 因此第二次 ACK sync 失败时，完整 ACK 标记可能已经持久化。重启后不重发也是允许结果，因为主机记录已经 FULL commit。本测试不错误要求所有 sync 错误必定回滚。
- 不模拟真实 Flash 页编程、缓存、供电跌落、保持时间、磨损、ECC、驱动并发、NVS 元数据 torn write 或芯片擦除行为。不能据此保证实物掉电安全。
- SQLite FULL 的耐久性仍依赖 OS/文件系统/硬件兑现同步语义。子进程退出是软件进程中断，不是主机断电。
- 没有无线收发、吞吐率、手机/iPad 后台行为、真实笔尖坐标或 BLE 安全资格测试。本 fixture 直接使用存储认证标志，不代替应用层 connection epoch 的既有测试。
- 没有增加容量或改变布局；24 小时离线目标、32 会话上限、整区 ACK 后回收限制仍未解决。

## 复跑

在本目录执行：

```sh
python verify_sources.py
python test_crosswire_replay.py
python -O test_crosswire_replay.py
(cd source && python -m unittest discover -s tests -p test_storage.py -v)
```

需要 Python 3、SQLite 与 C11 编译器 cc。测试不访问网络、不连接蓝牙、不打开硬件、不改仓库。临时 SQLite 和编译产物位于 TemporaryDirectory，结束自动清理。

## 后续集成的准入条件

在真正实现产品 BLE provider/主机客户端时采用上述精确 ACK 合同，并对真实连接 epoch、断连队列、重复/迟到回调、身份切换补充集成测试。量产/投板/上电准入仍由项目硬件安全门决定，本报告不授权这些动作。
