# BLE 接线、安全与授权线性化合同

## 1. 范围及线程

`pen_ble_core.c`由唯一NimBLE host事件线程拥有；GAP、GATT、发送、验权在同一事件队列串行。
`pen_ble_actor`由唯一应用任务拥有，它独占同一个`pen_app`，任何`step`、offer、sleep、reclaim、
reinit都不得并发。`pen_ble_actor_turn()`返回后才继续其它应用动作。两个actor不得共享app或backend。
core不是锁；不能从ISR或另一线程直接调用它。

start只允许单一初始化owner调用；成功返回后再发布backend给其它任务，失败须明确重启，不能并发或重复初始化。
跨任务RPC用一份静态请求、mutex和完成semaphore，至多一个请求在途。载荷/票据全部复制到静态请求；
绝不排队调用方栈指针。等待1秒失败会永久poison该通道，晚到事件没有可返回给应用的grant；
调用方停止actor，记录仍待传。该时限不是MCU实时性保证。host回调调用任何RPC会立即拒绝，
不允许USB显示回调反向等待host、Flash或应用任务。实际栈同步产生NOTIFY_TX回调；此分支不推进票据。

记录扫描、Flash写/sync、回收均在应用任务；没有将全分区scan/erase或ACK写搬进NimBLE host。
官方SDK自身的bond存储回调仍可能同步写NVS；这不是本桥可消除的延迟，须实测看门狗/连接行为。

## 2. 发送、MTU、背压与接收

UUID保持冻结协议：service `7c3f0001-7ad1-4d6f-963a-72b30000beef`；TX/ACK/INFO最后服务段分别0002/0003/0004。
TX notify；ACK特征宣告WRITE，客户端协议要求write-with-response，并要求加密/认证/16B键；INFO只在完整安全门后读。
SDK可能把恶意write-without-response也路由到同一access回调，不能靠properties声称绝对拒收；两种入口都要经过相同安全/票据门。
ATT write response只表示格式/入队被接受，不表示设备端耐久ACK已写完；设备掉电后可重放，客户端须持久去重。
订阅本身不是授权，不能因写CCCD而获取坐标。

每条48B原始packet拆成三个20B ATT value：`B1,index(0..2),seq低16位LE,16B原数据`。
要求ATT MTU≥23，MTU更大仍固定三片，兼容冻结重组器；不把MTU交换成功当吞吐证明。
ACK固定20B：`AK,version=1,reserved=0,session:u64LE,seq:u32LE,CRC32(前16B)`。
CRC只检测损坏，不是身份认证。载荷没有安全状态、epoch或批准字段可让对端自授权限。

只有三片均被`ble_gatts_notify_custom`接受且始终同安全epoch，才return0并建立mirror和应用offered票据。
**接受到协议栈不等于手机已收到，更不等于手机已持久保存。** 片1/2/3的busy/部分发送不新授ACK。
失败后从片0重试，重组器遇到片0应重新开始。相同记录最多每250ms重新提交一次三片；
期间已有完整offer返回0不重复通知，未完整offer返回busy。没有无界发送队列或heap逐帧缓存。
mbuf由notify_custom在成功/失败两种情况下都消费，不二次free。

收到ACK立即用可信栈当前安全态/非零epoch及`esp_timer`接收时间，匹配已完整提交的mirror ticket；
peek、未来记录、过期epoch、未完整发送、坏头/长度/CRC均拒绝。队列容量8、重复精确ACK去重；
当前stop-and-wait实际上只允许同一条记录。断连、取消订阅、key不足、安全降级、quiesce清队列/票据。

## 3. 新的 ACK 线性化契约（冻结actor不会自动获得此语义）

旧冻结`pen_app_ack(current,receipt,session,seq)`在调用时检查当前状态；分别RPC取得快照再调用它存在TOCTOU。
本候选**不改旧函数/旧actor源**，新增`pen_ble_actor_turn()`替换集成时原transport段：

1. 应用任务单owner冻结当前`sent_pending/session/seq/epoch`，生成递增nonzero nonce与app地址绑定的本地ticket。
2. 同步RPC在host单事件内重查真实链路、安全、持久SC bond和receipt；精确比对mirror ticket。
3. 匹配时生成一次性、仅存在内部静态RPC mailbox与调用方栈的grant，同时消费接收队列/mirror。这是**授权线性化点**。
4. RPC返回后应用任务核对app地址、nonce、record、epoch、sent票据、sleep状态均未变，**写入前消费grant和应用票据**，
   调用原`pen_store_ack`固定两次小写/两次sync。原store精确offering合同再次校验；没有任意ACK/erase旁路。
5. grant不经过BLE、不持久化、不对UI暴露、无外部提交API。未授权、二次grant、跨app/record/epoch/nonce均不可用。
   结构体不是防恶意进程的密码学能力；这里信任固件C内存和编译进来的backend，不能让不可信插件替换backend。

**事件顺序**：授权之前发生的断连、revoke、key降级、quiet必须拒绝；授权之后才发生的断连不撤销已认证ACK，
应用任务可完成这一次耐久提交。这是显式新合同，不声称与旧“调用瞬间状态”完全相同。
未完成的手机保存不得ACK；手机误发ACK或恶意已批准对端谎报持久化不在协议可证明范围。
批准的是BLE对端设备，不是手机上的某个独占App；Android官方文档提示同设备其它App可能访问BLE数据。
此候选没有App级身份认证/端到端协议，若要保护敏感轨迹或防同手机恶意App ACK，还需独立安全设计，不能宣称已解决。

失败在grant返回前：保留记录，重放后重新取得票据；RPC超时永久停机，不接收晚到grant。
失败在写/sync期间：actor fault锁存，不复用grant、不重试写、不擦除日志。重启原store恢复只认可完整ACK提交标记；
缺标记的记录继续待传，新连接新epoch重新完整发送后才接受新ACK。若最后sync报告失败但标记实际已耐久，
重启可能识别为ACKed——这仍来自已授权ACK，不是未授权删除。掉电/Flash故障真实性须实板验证。

## 4. 最小应用集成（尚未做真实board provider）

- 保持相机/mapper资格门、分区门、storage gate、contact actor全部原样，不生成任何“测试有效轨迹”。
- 在获准开发入口初始化BLE并完成本地配对策略后，取得`pen_ble_transport_backend()`；
  已初始化的`pen_app`用`pen_ble_actor_init()`绑定一次。
- 原`replay_transport`中逐回调ACK/offer段，替换成独占应用任务调用`pen_ble_actor_turn()`。
  返回-1必须沿原safe_stop关闭持久层；-3是未授权/无链路，1是busy/idle。
- 此桥可在正常记录和`replay_only`重放使用；不能与旧`next_ack`或旧`pen_storage_idf_ack`并存。
- quiesce：停止广告、清票据/ACK、请求断连；必须直到确实不广播且无连接返回0。
  停广告失败不能报告quiet。resume只解除静默，**不会自动开广告窗口**。
- 全日志回收/睡眠仍由原actor判断pending transaction、压力/IRQ、最终guard和sync；BLE quiet不证明硬件可睡。
- app重新初始化/新存储session应重新创建桥；不要复制actor或重用其nonce生命周期。正常sleep前不允许在途turn。

本目录的`app_main`未实施这些接线，仍是NULL board provider编译夹具；有代码不等于完整笔已点亮。

## 5. 开发配对与持久安全状态

`PEN_BLE_TRANSPORT`、`PEN_BLE_DEV_PAIRING`默认均n。即使两项编译y，`app_main`也不调用start。
真正运行必须有人明确授权，提供非阻塞**实际USB可见显示**callback，调用`pen_ble_dev_start(...,1)`。
它初始化NVS、耐久预留epoch、初始化host；尚不广播。

本地`pen_ble_dev_advertise()`打开60秒、最多一连接的窗口。消费窗口后不会自动再广告/重连。
不需要预知iPad/Android的随机MAC；地址只用于本地诊断。恶意设备抢先连接最多让这轮失败，不能获得坐标。
连接后60秒内必须完成配对和本地批准；超时撤销门并断开，迟到timer事件不能误撤销后来已批准/更新的会话。

本机DisplayOnly：新配对生成均匀随机6位passkey，通过真实USB callback显示，由用户在目标手机输入；
不持久/硬编码passkey，不使用固定公私密钥或SC debug keys。只接受DISP动作一次；其余/重复动作立即撤销并断连。
SC-only编译（legacy关闭）、SM_LVL4、MITM、bond和128bit键全部要求。Just Works不计authenticated。
SDK没有通用“先问用户再收到SMP请求”的应用钩子，远端协议请求可能发生；上述本地窗口、显示码、
安全字段、弱bond拒写及数据门共同fail closed，而不是声称SDK不会收到请求。

手机配对后还必须本地查看`pen_ble_dev_peer()`并`pen_ble_dev_approve(exact_epoch)`，仅真正加密、认证、
已持久SC bond且未超时才批准。BLE载荷没有批准入口。正式产品无屏幕/可见灯布局尚未决定，本策略只是开发USB方案。

bonded位不单独可信：SDK有忽略持久回调返回值的路径，所以包装官方write回调，任何错误永久锁store_fault，
拒绝坐标/ACK；容量满不轮转删除老bond，重复配对不自动删除bond。恢复连接额外查OUR_SEC的SC/authenticated/16B LTK，
旧legacy/弱bond不能因新编译选项升级成安全bond。只核官方内部数据，不输出/记录密钥。

只有将来**明确启用并在设备运行**时，SDK可能写NVS、产生/保存本机IRK及用户配对bond/密钥；
首次LOCAL_IRK初始化是start本地许可范围，不能被“尚无连接”误拒绝。本轮仅编译/mock，未生成真实密钥。
本编译夹具没有启用NVS加密/Flash加密/硬件Secure Boot，也未烧eFuse；不宣称防物理提取/克隆，生产密钥保护与安全启动须单独评审和授权。
不自动擦NVS、删除bond、创建账号或导出凭据。NVS不足/版本错/写失败需人工评估，不是erase重试理由。

连接epoch为`boot_counter<<32 | connection_counter`：启动前NVS commit boot_counter（1..2^32−1），
每连接RAM递增counter（1..2^32−1）；boot预留失败不启动host，任一计数耗尽拒绝。
跨断电只要已提交NVS不回滚就不复用；人为擦除/还原/克隆NVS会破坏保证，禁止自动操作，须独立迁移流程和重新建信任。
