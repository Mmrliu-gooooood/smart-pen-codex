# BLE transport 狭窄设计独立审查

对象：独立目录 `smart_pen_ble_transport_candidate_20261029`；冻结源 `smart_pen_app_pipeline_20261028` 不修改。最终设计收敛记录；实测代码结果与SHA绑定见 INDEPENDENT_REVIEW.md。

## Spec 轴：必须验证的安全不变量

1. 分别同步 RPC 取得 `next_ack/current_security` 不足。最终采用授权/持久化拆分：host串行核receipt、当前安全态、完整发送mirror ticket与actor ticket，产生仅进程内一次性grant；这是授权线性化点。actor独占app，校验app地址/nonce/session/seq/epoch后先消费grant再执行既有耐久ACK。授权点前断连拒绝；授权点后断连允许完成已经认证的ACK。没有把Flash日志操作放进host事件。此契约为明确新adapter接口，不冒充冻结pen_app_ack逐回调直接接线。
2. ACK 在 **接收时** 已对应同一非零 epoch 完整提交发送的 session/seq。仅后续应用时检查 ticket 不足：不能预排队未来 ACK，等待未来发送后借新 ticket 删除。
3. 三个 20B 通知均被栈接受，且 epoch/安全态未变，才返回 send=0。第一/第二片忙无新票据；已有完整同包票据的重发忙不能伪造另一包权限。
4. 断连、权限撤销、quiet、reset 均清除在途票据和ACK；旧连接 receipt 不能借新连接当前态删除。
5. 未加密、Just Works、非16B键、未bond、未逐连接批准均拒绝坐标/ACK。默认整个运行入口 OFF；生产无屏配对不属于本候选已解决范围。
6. 不接 camera/mapper、不制造 VALID、不擦NVS、不调用旧底层 storage ACK旁路、不启动radio或设备刷写。

## Standards 轴：实现边界

- portable core只管有限状态、固定线协议与有界队列；SDK-specific persistence/NimBLE所有权隔离。
- 禁止从host回调同步RPC回同host形成死锁；callback对同步 NOTIFY_TX重入应仅忽略/计数。
- RPC超时不能把仍在队列中的栈指针/栈event释放；要么生命周期持久且取消协议严格，要么等待直到确认完成并诚实说明实时性限制。
- 通知 mbuf所有权：`ble_gatts_notify_custom()` 无论返回成功失败都consume；不得失败后二次free。
- 默认编译夹具不自动开始广播；`pen_get_board_provider()`仍NULL。真正actor接线须明确最小补丁与未接部分。

## 官方本地证据（ESP-IDF v5.4）

SDK commit：`67c1de1eebe095d554d281952fde63c16ee2dca0`。
路径相对 `smart_pen_sdk_20261028/esp-idf`：

- `components/bt/host/nimble/nimble/nimble/host/include/host/ble_gatt.h:835-852`：通知函数consume mbuf，无客户端耐久接收保证。
- `.../host/src/ble_gattc.c:4411-4474`：notify调用同步产生 `BLE_GAP_EVENT_NOTIFY_TX`。
- `.../host/src/ble_gap.c:7770-7790`：NOTIFY_TX同步调用连接event callback。
- `.../host/include/host/ble_gap.h:208-225`：sec_state字段包含 encrypted/authenticated/bonded/key_size，无可直接读取的SC标志。
- `.../host/src/ble_sm.c:443-463`：authenticated/bonded只置位，不等同当前仍加密。
- `.../host/src/ble_sm.c:528-627`：persist_keys未检查our/peer store write返回；不能只依赖bonded位声称NVS成功。
- `.../host/src/ble_store.c:45-77`：write callback在host lock内调用；错误包装不可在里面再次调用获取同锁API。
- `.../host/store/config/src/ble_store_config.c:1037-1055`：init覆盖read/write/delete callbacks。
- `.../host/store/config/src/ble_store_nvs.c:335-365`：官方持久写走nvs_set_blob+nvs_commit。
- `components/bt/host/nimble/Kconfig.in:160,184-205`：NVS持久、legacy、SC、debug keys是独立配置；sm_sc=1不等同SC-only，debug keys不可启用。
- `examples/bluetooth/nimble/bleprph/main/main.c:335-361`：示例为便利删除旧bond且固定passkey，明确不能照搬为安全策略。

网络 primary references 已读：
- https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/bluetooth/nimble/index.html
- https://mynewt.apache.org/latest/network/ble_hs/ble_gap.html
- https://mynewt.apache.org/latest/network/ble_hs/ble_gatts.html

未声称无线互通、吞吐、电流或NVS实物断电已经验证。上述设计问题已回传作者并在最终代码复验。恢复旧bond还增加读取SDK OUR_SEC记录的sc/authenticated/16B LTK检查，避免把新编译SC-only误当旧bond证明。
