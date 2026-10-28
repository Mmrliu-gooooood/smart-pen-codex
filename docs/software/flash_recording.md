# 2026-10-28 Flash持久记录 / 断电恢复 / 确认补传

本次在`6c119ec65cdebed8a320af2e988fc896223b0f55`基础上增加真实可调用C模块，不是相机固件完工声明。未接硬件、未烧录、未测实体Flash掉电、未证实24h容量；默认编译和运行开关均关闭。

## 实际代码与接口
- `firmware/storage/store.c`在现有`pen_log`64字节槽之上增加持久ACK、跨启动补传、唯一启动会话检查、全确认回收和擦除意图恢复。
- `storage_idf.c`调用官方`esp_partition_read/write/erase_range`及`nvs_get/set/commit`。只接受显式名为`pen_records`的数据分区；检查4KiB边界、大小和非加密属性，先读验证NOR1→0，写后读回比较。不会自动格式化未知分区，不会因NVS失败擦除配对信息。
- `pen_storage_idf_begin_boot`先将单调boot_epoch写入NVS并commit成功，再允许seq0开始。seq只在记录成功后递增，失败锁错；重新打开时扫描已提交记录，拒绝重复/不连续序号和坏CRC。已提交旧会话可补传，不能重新使用。
- `firmware/runtime/recorder.c`实际串联接触状态机输出→Flash记录：保留捕获时间，统一分配device/session/seq；去抖批次中途满盘只保留已成功前缀，锁错并禁止睡眠。剩余点不冒充成功，需要上层明确报错/重启恢复。输入时间戳/格式验证错误同样锁住recording，禁止下一有效点以连续seq跨过丢失区。

## 64字节槽不改变原48字节SP传输协议
|偏移|内容|
|---:|---|
|0..47|原SP v1数据包及CRC|
|48..51|ACK标识`PAK1`|
|52..55|原数据包前44B CRC32，绑定ACK与原记录（不能覆盖自带CRC字段）|
|56..59|ACK提交标识`ACK!`|
|60..63|原记录提交标识`DONE`|

数据仍先写body并sync，再写DONE并sync；只有已提交且通过CRC的记录可补传。ACK先写8B标识/CRC并sync，再写4B提交并sync。任一ACK字节写入中断后不视作已确认，同一记录重发和重写相同ACK位模式安全。默认未写过ACK的旧日志仍能读取为未确认。

## 补传与认证边界
`pen_store_offer`保持同一条不可变已提交记录，直到精确匹配会话/序号的授权ACK持久化；不会发送尚在RAM的候选点。重连/重启从第一条未确认记录恢复，之后按物理记录顺序补传多个启动会话。`pen_storage_idf_fragments`沿用3×20B通知，`pen_storage_idf_ack`沿用20B AK格式，并要求实际连接同时encrypted/authenticated/bonded/approved四项成立。布尔值须由BLE连接状态提供，不能信任网络请求中的自报权限。

此组件提供实际分片/ACK入口，**尚未把生产相机或真实GPIO接入BLE事件循环**。现有bench仍为无VALID、无CONTACT的合成输运测试；不会把合成数据写成笔迹。上层必须使用一个任务/互斥锁串行调用store/recorder/ACK，不能从ISR直接写Flash。运行时GPIO仍以硬件合同配置，不在此硬编码。

Host修复：若主机保存前沿比设备重放的旧包更高，ACK取`min(durable_frontier, offered_seq)`，既只确认持久数据，也满足设备精确stop-and-wait匹配。原始数据库前沿不倒退。对此有实际客户端mock回归测试。

## 回收与断电
只在记录已停止、调用者safe_idle安全门成立、无正在offer且所有已提交记录均持久ACK时允许整分区回收。先NVS commit`erase_pending=1`，再擦除整分区，最后commit清除意图。任何擦除中断，下一次open必须完成该意图再开放记录。意图元数据与分区地址/大小绑定，布局更换被拒绝，不能拿旧意图擦新布局。

不是循环覆盖：任一未确认记录都会阻止回收；满盘返回−2，不覆盖。若介质坏CRC，锁故障，不能自动“修复”成坐标或绕过数据保护。断电时未完成提交的记录不作为成功记录恢复；重启采用新会话分隔，避免跨丢失区连接笔画。无自动后台回收/擦写均衡，整分区erase可能阻塞；实际供电保持时间、看门狗、磨损和调度需上板验证。

## 限制必须保留
- 为避免现有4B提交写与加密块对齐冲突，当前adapter明确拒绝加密分区。数据是明文笔迹；不能称为生产Flash加密实现。启用加密需要新原子槽格式、迁移与验证。
- 最多保留32个不同启动会话，达到后拒绝新会话，需在全部确认后安全回收；不是无限离线启动次数。
- 不自动生成或套用最终分区表，不假定芯片Flash容量。记录区与OTA双槽、NVS、引导布局必须由整机配置共同批准。
- boot_epoch依赖NVS持久性。禁止擦除/恢复旧NVS并沿用相同device identity，否则可能复用主机已有会话；工厂重置必须另行安全换身份/协议世代。代码不会烧eFuse。
- 64B×100Hz×24h=552.96MB；即使4MiB数据区也仅约10.9分钟连续100Hz。24h离线仍需实际写字占空比/压缩/更大存储选择，不以本模块冒充已达标。

## 已执行测试
`python -m unittest discover -s tests -p 'test_storage*.py' -v`和`test_recorder.py`：
1. 严格C11编译实际模块：52个数据写入截断、12个ACK截断、跨记录ACK移植拒绝、512个模拟擦除截断，重启、满盘、坏CRC、认证/会话/未来ACK拒绝。
2. 实际ESP-IDF adapter源码配mock API：默认关闭零写入、显式开关、拒绝加密/错误标签、NVS失败不擦除、epoch commit失败不开放记录、读回/分片/四项授权/确认回收。
3. 实际contact→recorder→store链路：原始沿缓冲时间、持久seq、立即释放、精确补传确认、中途满盘锁错。
这些是host故障注入，不等价于实体Flash掉电。真实SDK编译结果见`sdk_build_20261028.md`，不得将编译通过表述为硬件通过。

官方API依据：[ESP-IDF v5.4分区API](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/storage/partition.html)、[NVS API](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/storage/nvs_flash.html)。SDK写调用为同步返回；本适配另做读回，但这仍不能替代真实电压/掉电测试。
