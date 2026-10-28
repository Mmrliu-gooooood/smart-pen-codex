# 智能笔持久记录 / 接触时序 / OTA 独立审查

审查时间：2026-10-28 08:58 UTC。目录：`smart_pen_firmware_next_20261028`，基线 `6c119ec`。仅只读审查作者源码及运行其host单元测试；未烧录、联网部署或执行SDK下载代码。

## 结论先行

在接口合同（单任务串行、真实BLE权限、可靠NVS提交、已批准分区布局）成立时，**本次未发现新的已确认阻断性运行缺陷**。可作为默认关闭的可复用软件模块继续集成；不是整笔完成或量产放行。

**审查中曾发现，现已关闭：构建证据过期。** `firmware/runtime_idf/compile_report.json.source_sha256`与当前`firmware/storage/store.c`、`firmware/runtime/recorder.c`、`recorder.h`不匹配；`docs/software/ota_recovery.md`底部二进制大小/hash也与报告不同。已通知作者及主审，需最终源码重编译后刷新证据。这是可复现的验收证据问题，不是已证实运行安全漏洞。

## 实现核验

- `store.c:53–60`：仅授权且精确匹配当前offer的session/seq才能持久ACK；先写ACK内容、同步，再写提交标记、同步。当前绑定CRC覆盖前44B，已修复作者发现的“对含自身CRC的48B计算得到固定residue”问题；跨记录ACK移植回归实际通过。
- `store.c:62–67`：停止录制、无offer、全部已提交记录ACK后才允许整区回收；NVS erase intent先commit，擦除后再清除；`open`先恢复intent才开放记录。不是覆盖式环形日志，未确认数据阻止回收。
- `storage_idf.c`：epoch先持久化再begin；不自动擦NVS；分区地址/大小绑定；显式标签/对齐/非加密校验；ACK四项真实连接安全状态与长度/CRC校验。权限布尔值须来自受信BLE状态而非报文自报。
- `contact_power.c:38–63`：按原始down沿时间缓冲，确认后按捕获时间吐出；release立即输出contact-off；短tap/溢出明确GAP，不虚构首笔坐标。无图像、未校准、未就绪不产生VALID。录制满盘保留成功前缀后锁错。审查期间作者增加的非法输入锁错也已阅读。
- `update_idf.c:7–13,35–79,82–97`：默认OFF，要求signed-on-update与rollback，拒绝硬件anti-rollback配置；仅非活动槽；hash、SDK验签、签名描述符project/version依次检查，硬件名与签名project等值绑定；软件版本floor先commit再mark-valid；没有直接eFuse写入或隐式重启安装。
- `windows_ble.py`：持久SQLite提交后对重放旧包使用`min(frontier, offered_seq)`，匹配设备精确ACK而不降低数据库frontier；缺失前缀仍不能假确认未来数据。

## 独立执行证据

执行作者的严格C11编译及host测试：storage 2、update 3、contact 1、recorder 1、Windows BLE 3，共10项通过。涵盖52数据写截断、12 ACK截断、512擦除截断、NVS/SDK错误、精确ACK、满盘、缓冲首沿/释放、禁用与不安全OTA配置。未重新执行真实SDK构建；报告源码hash核对结果如上。

## 非漏洞但必须保留的边界

- 32个会话上限、全确认后整区回收、无磨损均衡；不能宣称无限离线或24h存储。
- `DONE`不匹配被视为未提交：仅能支撑约定写入/断电模型，不保证任意介质位翻转下不丢记录；如要覆盖提交标记腐败，应另加格式冗余/故障分类测试（防御增强，非当前模型下确认漏洞）。
- 实际NVS/Flash掉电、供电保持、BLE认证身份、真实签名镜像验签、相机/GPIO/传感器驱动与首笔测量仍未验收。mock签名只是调用顺序证据。
- 编译harness的`app_main`仅打印并返回，不能把两个构建通过表述为已连接真实笔、已升级或已运行录制。

### 08:59 UTC 作者回应
作者确认上述hash差异是两项安全修复后的中间态，正在执行最终双SDK重编译并刷新21项sourceSHA与binarySHA；OTA文档已移除重复hash表，改为引用单一compile_report。故“文档重复值”已采取修复，“最终构建绑定”仍待新报告核验，不应把中间态称为最终交付失败。最新recorder回归已再次独立重跑通过。


### 发布前复核（2026-10-28 09:04 UTC）

最终compile_report已刷新。发布检查逐一计算21项构建源码与41项主机测试源码SHA-256，全部匹配最终报告；再次实际运行完整主机gate为54 tests PASS、0 skips。OTA文档已改为引用单一构建报告。上述中间态证据问题已关闭；此处仅确认源码/报告绑定和主机测试，实际Flash、签名镜像升级、GPIO及相机仍未测试。
