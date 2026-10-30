# 8 MiB Flash 候选分区与只读启动门

这是显式选择的候选 profile，不是未知实物的烧录许可，也不是完整点阵笔固件。默认应用仍不提供相机、姿态、GPIO、BLE 或板级提供者。改变分区表可能破坏已有程序、NVS 或记录；本次没有对实物执行擦除、烧录、密钥或 eFuse 操作。

## 适用范围与默认行为

- 未选择 `PEN_APP_FLASH8_PROFILE` 时，分区门直接返回 `ESP_ERR_NOT_SUPPORTED`，不查询 Flash。应用默认无 provider，不能因此开始写记录。
- 显式 profile 的 SDK 镜像逻辑容量和 Flash 物理检测容量都必须恰为 **8,388,608 字节**；未知、4 MiB、16 MiB 或读取失败均拒绝。
- 这刻意不自动兼容 16 MiB DevKit；不能把 N16R8 当成 N8R8。即使容量通过，也不证明板型、PSRAM、接线或电池合格，板级 provider 仍需独立验证。
- 必须在应用 `pen_storage_idf_open` / NVS 初始化前调用 `pen_application_partition_guard()`，失败不能落入后续存储路径。最终 actor 调用和全应用测试由整合报告证明。
- 当前标准默认应用分区没有 `pen_records`，日志容量为 **0**；这里提供的是明确选择后才生效的自定义分区，不把规划容量写成默认已可用容量。

## 精确分区

| 标签 | 类型/子类型 | 起始地址 | 字节数 |
|---|---|---:|---:|
| nvs | data/nvs | 0x9000 | 0x6000（24 KiB） |
| otadata | data/ota | 0xF000 | 0x2000（8 KiB） |
| phy_init | data/phy | 0x11000 | 0x1000（4 KiB） |
| ota_0 | app/ota_0 | 0x20000 | 0x200000（2 MiB） |
| ota_1 | app/ota_1 | 0x220000 | 0x200000（2 MiB） |
| pen_records | data/0x40 | 0x420000 | 0x3E0000（3,968 KiB） |

分区表自身偏移为 0x8000。两个应用槽按 64 KiB 对齐；最后一个数据字节位于 8 MiB 边界以内。完整表、精确标签/类型/子类型/地址/大小、只读/加密标志都受校验，不能偷偷缩日志、增加未知分区或把同名分区换到另一个位置。

运行时还要求所有分区属于默认 Flash、擦除粒度为 4 KiB，当前应用确在表中 `ota_0` 或 `ota_1`。回收仍由既有存储层的耐久 ACK、擦除意图与应用维护状态控制；本只读门不擦除任何分区，不自动修复或重置 NVS。

## 物理检测与配置大小不是一回事

本次固定 ESP-IDF 5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`。官方 `esp_flash.h` 明确：`esp_flash_get_size()` 返回镜像头所表示的逻辑大小；真正检测的容量应使用 `esp_flash_get_physical_size()`。本实现分别检查两者。

物理 API 依据芯片 ID 常见容量编码，官方也说明特殊厂商编码可能识别错误；这不是对任意 Flash 品牌的电气认证，更不是板型身份证明。

来源：[官方固定版本 Flash API 头文件](https://github.com/espressif/esp-idf/blob/67c1de1eebe095d554d281952fde63c16ee2dca0/components/spi_flash/include/esp_flash.h)、[官方分区工具](https://github.com/espressif/esp-idf/blob/67c1de1eebe095d554d281952fde63c16ee2dca0/components/partition_table/gen_esp32part.py)。本轮直接核对了本地官方 SDK 源，并使用其工具，不依赖记忆猜 API。

## 日志容量：分钟级上界，不是 4 小时

`pen_records` 共 **4,063,232 字节**。每个记录槽 **64 字节**，含 48 字节数据包和 16 字节 ACK/提交元数据；最多 **63,488 个槽**。会话计数及擦除意图在 NVS，未虚构额外的日志头容量。

- 恰为每秒 60 条、无额外事件记录/损坏槽时，上界 **1,058.133 秒，约17.64分钟**。
- 每秒 120 条时，上界 **529.067 秒，约8.82分钟**。
- 实际接触/GAP/状态记录、失败或撕裂写入会消耗槽；不能把上述上界当保证值。在持续故障下不存在正的保证时长，不给虚假的“保守保底分钟数”。
- 底层最多保留 **32 个有记录的会话**，它可能先于字节容量触顶。应用目前新增的维护/补传策略由应用本身测试证明：必须全部有效记录耐久 ACK 后才能安全回收；未 ACK 内容不得为了续写覆盖。这里没有另写一套回收逻辑。
- 所有记录已 ACK 不代表立刻每次抬笔都擦整区。实际维护触发、可见状态、只读补传、独立新 epoch 和掉电恢复以应用审查为准。
- 扩大分区会增加启动日志扫描工作量。当前存储层会扫描日志，尚无真机启动延迟/能耗/Flash 寿命数据；不能由“空间足够”推导“拿起立即可写”。

## 构建和复验

显式构建默认文件顺序：`sdkconfig.defaults;profiles/sdkconfig.flash8.defaults`。这保持 provider 执行关闭。若只为验证 actor 分支链接，可追加 `sdkconfig.enabled_compile.defaults`，但仓库 provider 仍返回 NULL；不能称硬件已运行。

`tools/validate_flash8_profile.py`：
- 真实 C 纯函数及 IDF 只读 adapter，各启/停 profile × normal/NDEBUG/ASAN+UBSAN，共6组合。
- 官方 CSV→binary→CSV 再喂给实际 C validator，交叉确认精确表一致。
- 重叠、应用非64KiB对齐、超8MiB表均由官方工具拒绝；还覆盖错误标签/类型/子类型/偏移/大小、重复/缺失/额外分区、加密/只读、其他Flash、未知/4/16MiB、读取失败和错误运行槽等负例。
- Python normal 与 `-O` 验证结果一致，不靠 assert 保证门控。LSan 因 ptrace 环境关闭，ASan/UBSan 仍启用，不把它称为泄漏审计。

完整独立证据在 `verification/profile8_20261028/`。本子任务的两次目标构建使用隔离的当时应用快照，只证明 profile/adapter 的实际目标编译链接和槽位尺寸检查。应用作者整合后的最终 disabled/enabled/8MiB 构建才是最新整合证据，不能拿本子任务旧 actor hash 代替最终版本。

双 OTA 槽只预留空间，并启用 SDK 回滚支持。没有提供可执行 OTA 请求/provider，没有生成签名密钥，没有修改 eFuse。未来 OTA 安装及健康确认/签名策略仍须单独满足原安全门。此前未声明的 `PEN_SIGNED_OTA` 配置行不能被当作有效关闭开关，最终本 profile 不使用它。

**仍不可直接制作/烧录：实际 Flash、板型、相机、BLE、姿态映射、启动扫描时延、电源与整机安全均需实物确认。**
