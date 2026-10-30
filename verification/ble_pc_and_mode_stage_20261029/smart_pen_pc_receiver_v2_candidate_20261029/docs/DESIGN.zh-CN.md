# 设计与故障边界

## 范围和身份

独立目录，不改冻结固件、应用管线或 pinned 原网页repo。每个journal固定绑定用户本地选择的 `(peer_scope, exact OS target, expected uint32 device)`；同名广播、INFO字符串、CRC均不能认证身份。不自动根据名称合并笔、不读取全部配对列表。地址轮换、换电脑导致macOS UUID改变、bond恢复/设备迁移都必须停下来另行核实；本候选没有迁移/重绑API，不靠改payload/device绕过。

固件负责可信栈 SC/MITM/128bit/持久bond/本地批准epoch。Bleak统一接口在本候选使用的API中未给出可独立验证这些事实的证明，故始终 `host_security_attested=false`。INFO可读不是SC证明，`pair=True`也不是SC/MITM证明。本地同一电脑的其他进程/应用、管理员、被攻陷OS不在隔离证明范围；没有应用级身份/端到端认证。

## 一条记录的时序

1. 限定授权的单连接，检查唯一服务及TX notify/ACK write/INFO read属性，固定INFO完全匹配。
2. callback只拷贝20B值进有界队列（96片）；唯一消费者重组。片0永远重开；要求0→1→2、同seq低16位、callback观察时刻跨度两秒内、长度20、B1头。时间在callback捕获并随数据排队，不用dequeue时间；这不是空口硬件时间。任何错序/丢片/CRC失败重置且不ACK；等待设备从片0重传。
3. 重组48B后校验SP/版本/reserved/CRC、nonzero uint64 session、完整uint32 seq与seq16一致、flags/confidence/page约束；再比显式device。
4. journal线程在单事务按 `(device,session,seq)`查原始48B。同key不同内容立即锁故障；相同内容只作为已耐久重复。事务内复验完整schema，新记录INSERT必须影响恰好一行；提交前和COMMIT后均读回唯一精确BLOB，任何异常都不返回ACK授权。没有累计frontier ACK；冻结固件只允许当前完整offer的精确ACK。不同session、seq16碰撞、接收顺序改变不会合并；缺号保留为缺号，不能ACK未收到的记录。
5. 回到事件循环，先检查断连/overflow/连接状态，再 `write_gatt_char(ACK, exact20B, response=True)`。GATT响应只表设备接受请求，不证明设备ACK标记耐久；设备掉电可重传，本机再去重。

每次调用独占新client、closure/generation、queue、reassembler。旧callback只持旧闭包，断连即失活；不向新连接写旧ACK。已有journal行也必须在**当前连接完整接收三片**后才可再ACK。radio write开始后断连的结果可能不确定，但同client不会自动重连，笔端还需当前安全epoch/ticket门。协议栈接收notify从未当成PC收到/保存。

SQLite提交在单worker，不阻塞BLE事件循环。取消必须等已开始的worker完结后关闭DB；取消/断连期间可留下耐久行但不ACK。提交异常锁存，本进程不重试写、不复用结果。ACK丢失结束连接，再次显式连接完整重放即可。

## 耐久与路径

SQLite DELETE rollback + `synchronous=EXTRA(3)`，请求 `fullfsync=ON`（只在macOS对应F_FULLFSYNC）。选择EXTRA是因为SQLite官方明确指出DELETE+FULL在部分文件系统掉电后最后一笔可能回滚。新DB及目录使用显式sync；**仍依赖OS/VFS/文件系统/磁盘正确兑现sync，没有物理断电保证**。

目录必须预存在本机私有磁盘。POSIX：当前uid、目录0700/文件0600等价无group/other权限、拒绝软链接路径/非普通文件/硬链接；不自动chmod。Windows：`msvcrt.LK_NBLCK`独占锁已实现但未实测，DACL需要人工配置/确认，不能从mode位推导保密性。路径检查不是防同uid恶意进程的完整TOCTOU沙箱；Windows reparse点/磁盘ACL需实机安全复核。不要用网络盘、云同步盘、他人可写路径或可被替换的状态目录。

打开时独占receiver.lock，验证完整integrity_check、schema对象/列/PK/唯一索引、绑定元数据及每条记录CRC/身份。缺库（非首次显式create）、零字节旧库、坏库、外来表/版本、权限不足均停止；没有创建新空库替代故障库或自动修复/擦除的逻辑。SQLite自身hot-journal rollback是事务恢复，不是清除已提交轨迹；不要手删 `-journal`、lock或DB绕过恢复。

空间满/IO/COMMIT失败不ACK，保留全部文件并结束。最后COMMIT返回异常但实际上落盘属于“不确定”：重开后读取真实库，只有重新完整收到同记录且一致才ACK。没有靠内存认为“反正已经写了”而ACK的路径。

日志含敏感书写数据，**未加密**；本地文件权限不等同端到端加密。关闭进程后按审查后的备份流程保存，不在有连接时搬动/删除数据库。本轮不实现自动清理、VACUUM、wipe、日志回收、云服务或长期token。

## 已知未闭合

- Windows/macOS OS栈、蓝牙权限、配对、断连时序、DACL/锁、真实磁盘故障未测试。
- 接收端不证明camera/provider/标定、物理笔尖坐标准确、BLE吞吐/延迟/功耗、原网页评分效果。
- 固件实际USB交互/SC/bond持久/epoch/完整offer→ACK退休必须实板获准验证。
- 需要接正式坐标源时，必须新增经过审查的固件版本/来源资格合同；不能放宽INFO或加一个“允许VALID”CLI开关。

## v2 schema与回执的额外约束

只接受user_version=2及精确建表SQL/全部sqlite_master对象。拒绝任何trigger/view/额外index/表、TEMP对象，
核对table_xinfo的类型/NOT NULL/PK/隐藏列、index_list唯一且非partial、index_xinfo列序/BINARY排序规则及外键为空。
启动用完整integrity_check并检测同key多行，不靠quick_check和表名推断UNIQUE语义。
每条接收在BEGIN IMMEDIATE写事务内重新验证schema/metadata，阻止检查与INSERT间其他writer加trigger。
INSERT必须rowcount=changes()=total_changes差量=1，提交前后都必须实际读到唯一精确BLOB。
COMMIT返回但仍in_transaction或提交后readback失败/丢行/冲突全部锁停，无ACK；已提交行保留，重开并重新三片接收后再确认。
这不是对同uid恶意进程/任意篡改SQLite驱动的隔离证明；但不再把成功COMMIT等同必有目标记录。
旧v1库没有来源namespace、schema保障不完整；本版本拒绝而不自动迁移/擦除，迁移需单独受审方案。

callback时刻非有限值或倒退会锁存本连接clock_fault，停止接收且无新ACK。
最高观察时刻不会因片0/传输reset被清除；重组器本身亦拒绝中途时间倒退。该门只检查应用观察序列，不证明RF真实到达时间。
