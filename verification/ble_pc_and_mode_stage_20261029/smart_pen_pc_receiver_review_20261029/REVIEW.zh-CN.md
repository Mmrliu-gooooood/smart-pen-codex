# PC BLE 接收器 v1→v2 独立审查

结论：v1 存在可导致笔端删除未在 PC 保存记录的 ACK 缺陷，不能作为接收候选。独立 v2 已关闭本次三个实际复现及反向时钟问题，可作为**离线验证的候选代码**备份；不是实机安全认证或消费级成品验收。

## 精确绑定

- v1 `verification/MANIFEST.json` SHA256：`34e3d6e0f923a28eded99483ea57d79e42bf990c2618e12cf268eda690ff4b26`，31 项全匹配。
- v2 同文件：`2c0222aad3e8df4b2ed6cac861d62bf3de01ad792e37617a119482bcb4991ad6`，37 项全匹配。
- BLE C 协议 `verification/source_manifest.json`：`be8f57bc024ff7d466ea6d71544aa27ef067a9d551be20e2217940e84fec5d18`，41 项全匹配。
- 测试在独立副本进行；原冻结树未修改，详见 `frozen_check.json`。Linux Python 3.12.14 / SQLite 3.53.1；未扫描/连接蓝牙。

## 实际失败与修订回归

| 原失败 | v1 独立证据 | v2 独立证据 |
|---|---|---|
| `BEFORE INSERT … RAISE(IGNORE)` 静默丢记录 | `schema_ack_before_fix.json`: ACK 1，耐久记录 0 | `schema_ack_after_fix.json`: schema 拒绝、client 0、ACK 0，数据库原字节保留 |
| 同标签、不同 target 导出身份碰撞 | `export_identity_before_fix.json`: 两组导出完全相同 | `export_identity_after_fix.json`: 持久 source_namespace 不同，UI 始终禁止 |
| 消费时赋时掩盖片超时 | `queue_time_before_fix.json`: 慢提交期间跨 2 秒片仍 ACK 两条 | `queue_time_after_fix.json`: 真实 asyncio mock callback 跨 2.102 秒，只 ACK 第一条 |

v2 时间是**本机 BLE callback 采样时刻**，不是不可观测的 RF 到达时刻。回调记录单调时刻、连接 generation、复制 bytes 入队。时钟非有限/回退（含片 0/reset）、队列过载锁停；消费时不重置时间。提交在线程 worker 执行，不阻塞事件循环 callback。

## 独立测试

- 作者 45 unittest 在隔离副本 `-W error` 全通过，另 `-O -W error` 45 全通过；不合计成 90 个独立场景。
- 独立新增 9 unittest 全过：启动前及打开后 trigger；实际 COMMIT 后行消失/读回异常不 ACK；重复取消等待 worker 完成再关库；提交时队列溢出不 ACK、已存数据可重放；两目标导出；片中反向时钟；reset 后回退/NaN/±Inf。
- `run_wire_fuzz.py`: 实际冻结 C 与 Python 500 组确定种子随机 record/3 分片/精确 ACK 交叉匹配；48 个逐字节 record 损坏、20 个逐字节 ACK 损坏均拒绝。不是概率安全证明。
- 代码复核：48 字节记录、3×20 字节片、20 字节 exact session/seq ACK 一致；不支持累计确认。same-key 不同 bytes 锁停；不从旧库猜测缺片。
- SQLite 完整结构、额外对象、PK/UNIQUE/index、字段/SQL、完整性与既有数据校验；BEGIN IMMEDIATE 内重验，插入影响行数、提交前唯一精确行、COMMIT 完成和提交后精确行均检查。不确定结果无 ACK，无自动清库或 v1 迁移。
- 新连接独立 client/queue/closure；断连/取消/溢出/时钟异常发生在提交期间时，保留耐久记录但不发新 ACK。已开始的 GATT 写可能结果不确定，须依靠设备精确 ACK/epoch 门和重放去重，不能声称撤回无线写。
- source_namespace 绑定完整本地 binding，避免同名两笔自动合流；是命名空间，不是加密设备认证。NO_SENSOR 即使 wire VALID 也只导出诊断，coordinate=None、UI_allowed=false。

## 可复现命令

设置 `PC_SOURCE` 指向 v2 源副本，`BLE_SOURCE` 指向冻结 BLE 源；以下脚本仅使用临时 SQLite 和 MockClient，不使用无线：

```sh
python -W error test_independent_v2.py
python reproduce_schema_v2.py
python reproduce_export_identity.py
python reproduce_queue_time.py
python run_wire_fuzz.py
(cd "$PC_SOURCE" && python -W error -m unittest discover -s tests -v)
(cd "$PC_SOURCE" && python -O -W error -m unittest discover -s tests)
```

保留 v1 原失败脚本和证据，`PC_SOURCE` 改指 v1 可复现原问题。`check_frozen.py` 按工作目录同级源目录复核所有清单。

## 未通过、未测或不能证明的事项

没有真实 Windows/macOS BLE、配对/重连、硬件断电、磁盘控制器耐久性、长时满盘或实笔联调证据。Windows msvcrt/DACL 分支未实机测；人工确认私有目录不等于程序验证 DACL。DELETE+EXTRA/完整读回只能建立 SQLite/OS 契约，不证明硬件突然断电零丢失。模拟故障测试不替代电源故障实测。

默认不建无线连接；只有显式授权和指定目标才导入 Bleak/连接（字符串目标可能触发 Bleak 内部扫描）。pair=True、INFO 与人工确认均不能 attest SC-MITM，输出保持 host_security_attested=false。namespace/record SHA 不提供远端认证。受控私有本地目录是前提，不承诺抵抗同 UID 恶意进程在最终读回之后删改数据库。

此包不含隔离源副本/数据库/编译二进制，仅包含审查证据、复现程序和哈希；源由上述 v2 manifest 单独交付。
