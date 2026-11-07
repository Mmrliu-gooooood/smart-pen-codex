# R3 ACK整数门：独立复核

2026-11-07。REVIEW PASS FOR SCOPED CANDIDATE / NOT ADOPTED / HOST ONLY / NOFAB / NOPOWER。

## 结论

**R3相对R2的两行加固可采纳为默认关闭候选，无阻塞性回归。** pen_store_ack的authenticated及旧pen_storage_idf_ack的四项安全实参必须恰好为1。非法实参在写ACK、sync或消费offer之前被拒绝；合法ACK、重复/错误包拒绝、持久恢复与重试保持。

实际输入类型均为int，`!=1`正确覆盖0、负值、大于1和INT边界。store.c自身严格校验不能替代IDF入口校验，因为IDF入口原先验证后向store传常量1。新条件没有修改函数签名、AK v1包、CRC、session/seq、ACK介质格式或默认开关。

## 复现范围，不能扩大

独立使用冻结原版执行新增负例，确认：

- authenticated_peer=2且offer身份正确，会写入ACK；重开offer=1表示该记录不再待回放；后续另一次合法safe_idle=1回收返回0、模拟erase计数1。
- IDF encrypted=2、其他事实为1，且包长、header/version/reserved/CRC/session/seq都正确，同样产生上述后果。

这是调用者传入非法安全事实时的条件风险。安全实参不从ACK包中解析；未证明远程攻击者可控制实参，未证明真实设备丢数据。ACK本身不擦除，擦除是后续独立合法维护动作。送审R3报告正确保留了这些前提。

当前pen_app_ack/secure原本已经要求current和receipt四个uint8_t事实==1、非零相符epoch以及已发送票据。独立复跑原版该入口的2040个错误事实及epoch负例通过；不能称R3修复了现主actor绕过。

## 本轮实际独立执行

运行：`python3 -B firmware_ack_r3_independent_20261107/run_review.py`

为节省空间，直接读取已冻结候选/测试，记录运行前后SHA并确认无变化，只保留一个复用测试二进制。编译使用-Os、严格警告、函数段裁剪；按测试类型运行NDEBUG或保留assert，并另做UBSan。

共11次程序执行：9次正常通过，2个冻结原版负例按预期失败，无非预期失败。

1. 原版store/IDF两个持久误ACK影响负例。
2. 原版主app既有严格门。
3. 候选store/app/IDF各一次优化构建、各一次UBSan构建。
4. 候选store下的既有test_storage.c：52个data字节、12个ACK字节、512个erase中断模型，保持断言并通过UBSan。
5. 独立新test_same_offer_retry.c：对INT_MIN、-65536、-255、-1、0、2、255、65536、INT_MAX在同一offer上连续拒绝两次，确认整个store状态、全部介质及回调计数不变；不重启立即合法ACK成功且只产生两次program/两次sync；重复合法ACK不新增写入，重开不再回放，合法回收成功。已有fault不会因非法或合法ACK被清除。

候选作者65次完整矩阵是作者的执行证据，本轮没有重复整套65次，不能混计为独立重跑。已审查其65次结果、测试源码和断言配置；本轮独立11次覆盖本次两行变化及相关存储行为。

## 持久化与错误结果

新增store ACK测试覆盖两次program、两次sync的4个失败点。前三个失败点在同步内存模型中仍可回放并合法重试。最后sync报错时ACK marker可能已完整写入，重开可能识别为已ACK；代码锁存故障，但不能将返回-1解释成“ACK一定未发生”。送审报告与测试对此说明正确。

上述结果来自可控宿主内存/NVS API替身，不是实际Flash掉电、SDK目标或BLE安全证明。合法持久ACK重开后不再回放是预期语义，不应为了统一错误结果而清除已提交ACK。

## 来源核对与边界

最终送审manifest SHA-256：55719be7a6a70c3fc620c0f02a4de4b1bec6eb72867beaee9f563198c8ed73f1。

47个包内文件大小/哈希、46个冻结编译来源全部匹配；完整补丁与5个源码逐字一致（+21/-6），相对R2增量精确为两行替换。证据：EVIDENCE_RECHECK.json、RESULTS.json、REVIEW_TESTS.log。作者首次sync测试计数错误已改为ACK调用前后差值，未修改固件迎合测试。

这只是数据域约束，不是新的认证实现。已被错误归一化或伪造为1的事实仍需真实调用方拒绝；旧低层API的epoch、安全来源和offer资格不因本补丁而获得主应用的票据保障。建议以后在头文件明确安全实参只能0/1，属于文档改进而非本次阻塞。

未修改冻结工程或送审包，未安装、删除、推送、刷写或上电。没有完整host aggregate、ESP-IDF目标编译、真实Flash/NVS/BLE或设备验证。原有provider缺失、sleep竞态、原子idle hold及硬件资格仍未关闭。
