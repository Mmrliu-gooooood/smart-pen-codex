# 会话开放、READY 与落笔活动：独立状态侧车候选 R2

2026-11-07。**NOT ADOPTED / HOST ONLY / NOFAB / NOPOWER。** 只新增两个可选 C 源/头文件及测试，不改冻结工程、R3布尔加固包、旧结构体/回调 ABI、协议、默认关闭开关或 CMake。不安装、不删除、不推送、不刷写、不上电。

## 结论

R2修复了R1的**输出别名缺陷**。此前先清空out，再与watch.previous比较；调用 `pen_app_poll_activity(&app,&watch,&watch.previous,&changes)` 会把旧基线清掉，未变状态也报告STATE和DURABLE。错误路径还会破坏watch。此前26项测试没有覆盖这组合法类型别名，不能据其通过声称别名安全。

现实现先检查应用生命周期与重叠，再执行任何写入。watch、out、changes彼此，以及它们与app/store的写入重叠都明确拒绝，返回-1且所有对象保持不变。**别名错误不能同时保证清输出和保留watch，因此合同明确选择完全不写。** 非NULL app的initialized!=1也完全不写，不访问可能未初始化或保留旧值的store指针，避免失败重初始化后的store别名漏检。其他普通、互不重叠的错误仍清空out/changes并保持watch不变。调用者须先检查返回值，非0不能继续消费旧输出。旧ABI与结构体布局不变。

可以先安全地补齐**纯软件状态查询与变化检测**，不用把旧 `recording` 改成另一种含义，也不用给所有现存 provider 追加一个不兼容的回调字段。

候选增加 `pen_app_get_activity_status` 与 `pen_app_poll_activity`，读取真实 pipeline/contact/store 内存状态，不读时钟、不读写 Flash、不消耗 ACK offer/ticket、不调用硬件。旧 `pen_app_status` 被原样保留在扩展快照中。正常帧/定时器与真正状态变化分开，可供后续指示灯或已有上位机消费。

**这一步没有把自动通知接入生产 actor 或 UI。** 真实 `app_main` 的测试插桩重新证明：准备、READY、接触及释放期间，旧 `report_status` 仍只有启动通知；随后故意让 poll 失败，才有第二次故障通知。新侧车在测试中能观察这些变化，不表示真实 provider 已开始上报。最终 CMake 仍链接返回 NULL 的 absent provider。

## 1. 解决的语义混淆

- **recording**：日志会话开放。启动、预热、READY、确认前暂存以及逻辑休眠请求后都可能为1，不等于正在出墨或当前观察已持久化。
- **pipeline_ready**：CP 就绪门满足。不要求已经收到纸面帧；不代表相机 GPIO 已核验、纸面可解码、笔尖位置有效或首笔零丢失。
- **CONFIRMING**：原始接触已进入确认窗口，可能只有 RAM 中的有效候选点。`tip_accepted=1` 也可能尚未写入一条记录。
- **CONTACT_GAP**：接触已经确认，但没有可继续的有效坐标链。确认接触不等于有效笔迹。
- **TRACKING**：软件已确认接触，CP 为 READY，且最近有效观察链未被标记丢失。新鲜的无帧定时事件可以保持该状态且本次写入数为0，因此不能翻译成“本次新点已保存”，更不能当成实体出墨传感器。
- **READY，已抬笔**：释放不等下一帧，原确认与连续链立即结束；会话可以继续开放，短抬笔不必冷启动。
- **LOGICAL_ASLEEP**：只读出 CP 枚举，不声称 CPU 已睡或相机已断电。不能由此判断 actor 已 quiesce，或最终 USB/唤醒源检查完成。
- **REPLAY_ONLY / SLEEP_PREPARED / BLOCKED / FAULT**：分别表达已有应用模式。容量满时 recorder 也会锁存 `faulted`，但可回放的容量事件不误报成 I/O 损坏；真正存储/CP故障优先。

`last_event_us`、`last_raw_contact`、`last_contact_confirmed` 明确为**最后处理的 CP 事件信息**，不是当前 GPIO。进入 replay-only 后 CP 不再处理真实事件，旧接触字段可能保留1；模式与 `pipeline_ready=0` 阻止消费者把这个历史值当成正在记录。

## 2. 持久记录参考的刻意边界

字段名是 `durable_reference_known/session/seq`，不是“物理最后落盘点”或全局最大序号。它取当前 store 的 session 表最后一项及该会话已知序号：

- 普通 writer 顺序日志中，该参考随成功提交更新，包含释放和 GAP 记录，不仅是有效点。
- 若最终 sync 返回失败，槽中可能已有 DONE，而 session 元数据尚未前进。快照保持此前的已知参考，不把 `slots_used` 当成已提交点数；重开成功后才能反映恢复所得事实。
- 新会话开放但还未提交时，参考可以仍属于旧会话；必须同时使用 session/seq，不能只显示一个序号。
- 合法回收清空当前日志后，参考回到 unknown；不是跨回收保留的历史水位。
- 当前 `pen_store_open` 还会接受合成的 A0、B0、A1 交错日志。session 表最后项为B，因此参考为B0，而物理最后槽为A1。测试锁定这个边界，**不冒充已找到物理最后记录**。正常现有 begin/append 不生成这样的交错序列。

若后续产品必须上报全恢复场景下精确物理最后记录，应在 append/open 时增加经过验证的元数据，或明确单独读盘查询的失败语义；本候选不为了状态显示加入隐性 Flash I/O。

## 3. 向后兼容与接入约束

新增文件：

- `candidate/firmware/application/activity_status.h`
- `candidate/firmware/application/activity_status.c`

`activity_status.patch` 只新增这两个文件。旧 `pen_app`、`pen_app_status`、`pen_board_provider`、签名、48字节 SP 与20字节 ACK 格式均未改。新接口不是线协议，不能直接 memcpy 到 BLE/USB。

调用者须与原 pipeline 同一 actor 串行运行。每个 app 生命周期将 watch 清零，之后在每个有序 step、取消/准备睡眠、回放与故障边界采样，才能观察相邻状态；跳过中间采样会合并中间变化。状态变化掩码忽略时间戳、暂存计数、槽位计数和提交参考，避免每帧刷新状态灯。提交参考变化另有掩码，不保证所有恢复格式下逐提交通知。

**被动快照不会自行过期。** 没有新的CP step时，即使时间已过去很久，重复查询仍可得到旧READY/TRACKING及旧last_event_us。UI必须根据event_known、同一boot内的单调时钟、事件时刻和自己的合格超时/看门狗策略判断时效；不能因为重新查询/收到同一快照就刷新来源时效。last_event_us表示CP事件而非最新图像的时间。如果跨端只转发状态变化，还需另行设计事件健康/保活机制，否则静止状态既可能正常也可能来源停滞。本候选不选择新的超时时长，不实现该UI或保活机制。

R2的重叠检查采用uintptr_t地址差值，避免计算区间末地址溢出及对无关C对象指针做关系比较/减法；依赖宿主及拟用ESP-IDF平台的平坦地址表示。目标编译和平台资格仍未做。所有非NULL实参仍须为声明类型的有效对象，范围检查不是任意坏指针探测器。

**actor/provider错误仍须保留独立 `actor_error` 通道。** poll/apply/quiesce等错误未必写入 pen_app；侧车可能只见 BLOCKED，屏障后也可能仍见 SLEEP_PREPARED。侧车 FAULT 只代表其读取到的应用/CP/store故障，不能吞掉旧回调错误码。sleep_pending也是actor局部变量，本接口不伪造它。

下一步最小工作是另做默认关闭的actor接入候选：明确可选通知入口、actor_error与sleep_pending关联、同次事件顺序、回调时限/丢弃策略及UI标签，再验证。这不要求现在启用硬件或让用户补材料。

## 4. 本轮实际测试

复现：`python3 -B firmware_activity_status_candidate_20261107/run_host.py`

R2最终完整运行 **35次：32通过、3个R1负例按预期失败，0个非预期失败**。在冻结核心及独立R3布尔加固覆盖两种组合上分别运行，使用现有 GCC 与 Python，无安装。新测试采用显式 CHECK，`-DNDEBUG` 不会取消断言；含 UBSan，未报告未定义行为。

- 3个R1负例实跑：稳定状态out=&watch.previous原返回0并报变化掩码6；无效app的同一别名原错误路径修改watch；changes指向out.legacy.contact_faults原返回0并把变化掩码4写成了虚假故障字段。它们编译R1原代码，不是人造旧算法。
- R2对应拒绝不写；真实新记录/状态变化没有被拒绝调用吞掉，随后独立输出调用报告正确变化，再次调用报告0。补watch内changes、app/store内changes、与app/store重叠的对齐union、无效app/NULL参数/非法watch初始化、真实失败重初始化保留store指针后的别名与独立缓冲错误路径，逐项检查字节保留。两种核心组合分别以O2、NDEBUG、NDEBUG+UBSan跑完。
- 新鲜度反例：只推进合成UI时钟、不调用CP step，重复查询128次，TRACKING和last_event_us保持原值；真正送入晚到的定时step之后才按原核心规则进入接触超时故障。这不使用真实等待或虚构实物延迟测量。

- 新状态测试：每个冻结核心版本50个快照检查点，R3组合51个；分别以O2、NDEBUG、NDEBUG+UBSan重跑。这是夹具内检查点数，不是独立实物场景数。
- READY但从未有帧；预热；确认前有效点仅暂存在RAM；确认后有序提交；TRACKING定时事件零提交；新有效帧仅改变提交参考；姿态拒绝/帧陈旧产生GAP；恢复首点含GAP；无帧立即释放；短触不升级暂存点。
- 有接触且已确认但没有有效坐标；相机就绪撤回与超时；时钟倒退；确认buffer溢出；部分flush成功后满库只回放；屏障前取消及屏障后不能复用旧会话。
- 真实模拟存储的read、ACK program、正常与回放sleep sync失败；FAULT覆盖容量回放；两处append sync失败。最后sync失败夹具中DONE可已存在，结果不确定边界没有被抹掉。
- 当前/旧session身份，UINT32_MAX元数据边界，合法ACK后回收清空参考，新生命周期清零watch，成功reopen接受的交错session日志。
- 普通NULL/已初始化应用错误清空独立输出，watch不被推进；重叠或应用生命周期无效则完全不写。覆盖CP非法枚举/布尔字段、超限buffer/session表、空指针与非法watch初始化状态。
- 每个正常快照前后比较完整app、store与模拟介质；确认读取/写入/sync回调计数均不增加，不改变ACK/重放状态。
- 测试专用插桩直接运行真实 `app_main`，在O2和NDEBUG下确认新状态可观察，旧通知缺口仍存在。插桩并非生产hook。
- 原pipeline、maintenance及actor启用/禁用测试原样重跑，两种核心组合均通过。旧消费者与新模块同编译/链接，旧头文件SHA不变。

R1源码、补丁、旧26次结果、旧测试与报告保留在 `r1_evidence/`，包含现已知别名缺陷，不应选作采用版本。先前执行不混入R2最终35次统计。最终结果绑定当前候选源码、测试、runner、负例所用R1源码SHA以及冻结与R3来源，见 `RESULTS.json`、`HOST_TESTS.log`。包清单见 `PACKAGE_MANIFEST.json`。

最终执行前后42个冻结源码/头/夹具与5个R3覆盖文件SHA一致；上游合同25份绑定来源另行重查匹配。`patch --dry-run --batch -p1` 对冻结工程成功校验新增文件补丁，仅检查，没有应用。

## 5. 没有完成的验证与功能

没有完整host aggregate（现有入口所需cv2、bleak不可用）、ESP-IDF目标编译、真实GPIO/相机/Flash/NVS/BLE/USB/深睡/功耗/笔迹精度验证。Gray8像素和姿态mapper是明确的合成测试夹具，标签设为SENSOR仅用于执行资格门的宿主测试路径，不能作为硬件资格。

没有选择真实press/idle时长，没有实现新board provider、事件队列/generation、硬件ready证明、最终睡眠事务、实际灯/UI或跨端状态协议。宿主通过只能证明这份可选软件查询候选及所列回归；整体工程仍未完成，也不能据此放行制造或上电。
