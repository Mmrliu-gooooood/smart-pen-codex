# 下一轮实机门（尚未执行，不是刷机授权）

1. **板型和供电**：确认具体ESP32-S3模组、Flash容量、USB电源及电池保护。此2MiB SDK默认分区仅编译夹具，
   没有`pen_records`，不能烧到最终N8R8/N16R8并宣称离线功能完成。冻结8MiB profile同样须物理容量/分区核验。
2. **安全版本与本地交互**：审核官方SDK当前支持补丁/安全公告；实现并审查USB可见passkey、窗口开关、
   当前epoch批准、超时/取消状态。不得从BLE载荷、网络控制或隐形日志自动批准。无屏量产方案另定。
3. **BLE基础互通**：受控开发板先不接摄像头/补光/电池充电；有用户在场完成SC+MITM配对。
   iPad/iOS走CoreBluetooth原生接收端或受支持测试客户端；不是Web Bluetooth。Android原生GATT同理。
   本候选未写原生App，用户此前“不重做评分UI/独立App”要求未改变；现有上层桥接选择须另确认。
4. **接收器**：检查INFO真实标记、UUID、三片重组、CRC、设备identity/session/seq。记录先耐久提交，再写20B精确ACK。
   旧Windows synthetic-only接收器会拒绝本INFO，不能为了兼容谎标SYNTHETIC；需窄真实BLE数据源接线后另测。
5. **事件矩阵**：ATT MTU23/更大、CCCD关/开、片0/1/2丢包、ACK丢失/重复/乱序/提前、发送忙、远端断连、
   同handle复用、新epoch、配对失败/JustWorks/弱键/旧legacy bond、未批准、密码输入取消、静默中再落笔。
   授权线性化前断连不能写ACK；授权后断连可完成该次已认证ACK，重连不复用grant。
6. **持久/掉电**：分别在boot_epoch set/commit、官方bond write、ACK两次write/sync前后切电；证明失败不擦NVS、
   无新未经许可记录被退休、未ACK留存、恢复无epoch重复。日志容量/32session回收仍按冻结合同。
7. **性能与低功耗**：测通知/ACK真实吞吐、丢包、RTT、host/应用栈水位、NVS同步造成的最长停顿、看门狗、
   重连/后台App行为、电流与续航。固定3片记录共60B ATT值、ACK20B，未计ATT/L2CAP/空口开销；不能用纸面带宽推断帧率。
8. **整笔链路**：真实camera provider、物理笔尖mapper、低功耗唤醒/LED/状态指示和最终actor接线通过之前，
   不宣称可写字、光学精度、坐标VALID、离线时长、4小时续航或手机端功能已完成。

停止条件：任一未批准路径发坐标、早ACK导致耐久退休、epoch重复、quiet假成功、自动erase、崩溃/失控广播，
立即停止该测试并保留日志；不是把开关继续打开直到“看似成功”。每次设备操作须另有明确授权。
