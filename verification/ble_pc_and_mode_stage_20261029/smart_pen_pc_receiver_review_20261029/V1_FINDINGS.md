# PC接收器 V1 独立阻断复现（2026-10-29）

对象源清单SHA256：`34e3d6e0f923a28eded99483ea57d79e42bf990c2618e12cf268eda690ff4b26`。未修改冻结PC/BLE树；首先复制PC到隔离`source`，只用本地临时SQLite及MockClient，没有扫描/连接/配对无线。

## 1. 明确数据丢失阻断：数据库吞INSERT仍ACK

合法库关闭后增加`BEFORE INSERT ... SELECT RAISE(IGNORE)`触发器，再执行真实receive。启动校验只看表名、metadata、已有记录，不拒绝额外trigger；accept不检查写入影响行数或精确读回。结果：**ACK_writes=1，durable_rows=0**。

复现`reproduce_schema_ack.py`，结果`schema_ack_before_fix.json`。这不是要求防同uid恶意进程的完整隔离证明，而是外来/异常schema不能被误判为本应用规范库，更不能授予“持久成功”。需完整schema/PK/unique/index/objects校验、事务内重验、精确写入/提交后读回；COMMIT不确定仍无ACK，不自动修复/擦库。

## 2. 不同笔导出身份碰撞

两个独立journal绑定不同target，但相同本地label、device/session/seq，真实record_events产生完全相同的3个事件。数据库保留了target，但导出丢弃，仅label/device不足以在后续合流中区分两笔。

复现`reproduce_export_identity.py`，结果`export_identity_before_fix.json`。需绑定元数据的稳定source namespace，所有导出/接收事件携带，不把它称硬件认证。NO_SENSOR/UI_allowed=false门在此测试仍正确，未被payload VALID升级。

## 3. 慢commit使片时限变为消费时间

第一条提交worker阻塞时，下一条片0与片1/2的实际callback观察跨度2.103秒，超出2秒上限；队列仅保bytes，消费者稍后迅速处理时仍组装并发第2个ACK。

复现`reproduce_queue_time.py`，结果`queue_time_before_fix.json`。应在callback捕获单调观察时刻入队并用它重组；不能把消费时钟冒充到达时钟。该时刻也不是空口硬件时间，Bleak/OS调度延迟仍存在。

## 其余已有证据不覆盖这些缺陷

在隔离副本独立重跑作者31项测试通过、真实冻结C crosswire通过；另500个随机C/Python记录/分片/ACK对照、48处record字节破坏、20处ACK字节破坏均通过。由此不能推导接收端持久性/导出身份/队列时限正确。

后续V2需独立冻结再复验；V1保留为历史失败证据，不能直接当可执行交付。复现脚本可设置`PC_SOURCE`指向V1源；脚本禁止写pyc，DB/编译输出使用临时目录。这里没有实机安全、Windows DACL/锁、SC-MITM、物理断电或性能结论。
