# BLE transport 候选独立审查

## 结论

可作为**默认关闭、未启用无线的软件候选**保存。独立测试所覆盖范围内未发现尚未修复的阻断逻辑；不等于可直接烧录整笔、BLE互通、移动端接入或消费品安全验收。审查期间未修改作者源码或冻结源，未访问设备、刷机、运行radio、生成真实密钥或推送仓库。

作者源：`smart_pen_ble_transport_candidate_20261029`。冻结应用依赖：`smart_pen_app_pipeline_20261028`。最终代码/config/冻结依赖清单SHA256：`43cc36a257463bdefd24358f6330538b835eeb2f17d019b58b6b4b01ae52352e`。逐文件SHA在 `FINAL_CODE_TESTED_MANIFEST.json`，独立测试自身与stub来源在 `REVIEW_ARTIFACT_MANIFEST.json`。

## Spec 轴

- **ACK授权保留且加固**：查询pending不授权；三片全被通知API接受才有mirror ticket。接收时先拒绝未来/未发送ACK，最终授权再比对receipt/current nonzero epoch、完整发送ticket与actor ticket。
- **明确授权线性化**：最终方案不是把Flash写入host线程，也不是逐回调拿快照后盲写。host在单event内授不可由BLE payload生成的内部grant；actor校验并一次消费后写既有store。授权点之前断连不写；之后断连允许完成已认证ACK。这是新transport适配契约，不能直接把新backend塞进冻结board_provider回调假装端到端接通。
- **真实安全状态**：栈当前加密/认证/bond/16B键、持久OUR_SEC中SC/authenticated/16B LTK、逐连接本地批准和无持久故障均必要。SC-only/level4/no-debug/one-connection编译门关闭legacy复用漏洞。
- **开发配对边界**：本地60s一次广告窗口、随机passkey在实际本地USB显示、手机输入、同epoch本地再次批准；不需要手机MAC，不把Just Works视MITM。生产无屏/无可见灯的onboarding仍未实现。provider仍NULL，编译main不调用start。
- **持久化边界**：连接epoch为启动前NVS提交高32位+RAM连接低32位；不在每次连接中写epoch。SDK首次runtime启动可能生成持久本机IRK，配对可存bond/CCCD；本轮只编译/mock，没有真实凭据写入。无自动NVS擦除。手工擦除/回滚NVS不在跨重启唯一性证明范围。

## Standards 轴

- 固定大小请求、packet副本及RPC event，不把调用者栈指针存入异步队列；超时永久锁存，late event不能拿到外部grant或访问已释放payload。
- 单host owner串行transport状态；多调用者用mutex串行RPC；host callback重入RPC被拒绝。NOTIFY_TX同步重入不触发递归发送/票据。
- 通知mbuf按官方“所有返回路径均consume”处理；失败不二次释放。Flash日志仍在caller/actor任务，SDK自身bond NVS操作是另一持久边界。
- 安全失败/存储失败锁存，不能靠resume恢复。默认或enabled-compile均不启动radio。
- 此轮并发测试是pthread+窄FreeRTOS/NimBLE替身，不能证明真实SDK调度时延、硬件IRQ与无线空口顺序。

## 发现与修复闭环

1. 设计期分别current/ACK RPC的TOCTOU → 改为内部一次性授权grant，固定线性化点，actor持久提交。
2. 未来ACK预入队可借后续ticket → 接收时也要求完整发送mirror ticket。
3. 跨连接继承CCCD/MTU → epoch变化清subscription、MTU回23、清ACK/ticket。
4. quiet忽略广告停止失败 → 只接受stop成功/已停且adv_active为false，断连完成才quiet=0。
5. SDK启动本机IRK写早于pairing → 允许显式runtime-start授权的LOCAL_IRK；peer安全记录仍受窗口/有效期限/强键检查。
6. SDK可能bonded=1但NVS写失败 → 包装store callback锁故障，禁止round-robin自动删除bond。
7. 已入队pairing timer在批准后迟到会误断 → 独立实复现失败后加deadline/approved/pending检查；批准与持久写也核实真实期限。`late_pairing_timer_before_fix.log`保留原负例。
8. 部分start失败允许再入/计时器分配未检查 → start_attempted锁定生命周期、检查callout_init错误。
9. 新SC-only编译不能证明旧NVS bond安全 → 恢复时检查OUR_SEC.sc及强键属性，弱SEC写入直接拒绝。
10. 启动时host_task跨任务首次读写 → 原子TaskHandle发布（最终代码清单绑定）。

## 实际独立验证

| 检查 | 结果与含义 |
|---|---|
| portable core额外负例 | 47场景，normal/NDEBUG/ASAN+UBSAN PASS；片1/2/3背压、断连、换epoch、撤销、quiet、fatal、未来ACK、坏CRC、MTU22/517、键长、时间倒退等 |
| actor/grant额外负例 | 12场景，三模式PASS；授权点前/后断连、grant nonce/app/flag篡改、票据变化、重复授权、重入、sync失败无重试、nonce溢出、sleep |
| 真实IDF adapter源+窄stub | 11组+4独立失败用例，三模式PASS；8个pthread RPC调用者、late event、mbuf消耗、GATT解析/安全门、startup IRK、弱恢复bond、迟到/过期timer、初始化/NVS失败、弱/过期持久写 |
| 官方SDK构建独立复核 | 两目录ninja复核PASS；真实Espressif ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`，ESP32-S3；默认/启用编译BIN分别208352/531840字节，构建配置与ELF/BIN/分区hash见 `SDK_ARTIFACTS_CHECKED.json` |

ASAN设置`detect_leaks=0`，没有宣称泄漏检查通过；未运行TSAN。Mock内存日志不是实物Flash掉电测试。各模式重复执行同一组场景，不能把三倍次数冒充三倍独立覆盖。

## 再现

默认在同一父目录保留作者候选与本review目录。默认直接使用候选内逐字复制的 `frozen/` 依赖，不需要完整旧仓库；亦可显式指定：

```sh
export PEN_BLE_REVIEW_SOURCE=/absolute/path/to/smart_pen_ble_transport_candidate_20261029
export PEN_BLE_FROZEN_SOURCE="$PEN_BLE_REVIEW_SOURCE/frozen"
export PEN_BLE_REVIEW_OUTPUT=/tmp/pen-ble-independent-review
python smart_pen_ble_transport_review_20261029/run_extra.py
python smart_pen_ble_transport_review_20261029/run_actor_extra.py
python smart_pen_ble_transport_review_20261029/run_idf_extra.py
```

真实SDK构建命令在作者 `tools/build_idf.sh`。编译日志自动打印的flash命令没有执行。

## 实机下一门

1. 实际USB本地显示/物理批准链路、设备与Flash几何、NVS生命周期、SDK受支持安全补丁先独立批准；禁止将此编译夹具当固件刷入现有笔。
2. 真实central完成SC passkey配对、16B键与bond恢复、未批准拒绝、错误passkey/旧legacy/bond-full/超时/重连；先开发板低风险环境。
3. MTU23与较大MTU、每片/ACK掉包、重连、存储失败/断电、grant授权前后断连和idle静默实测。用日志证明先持久接收再ACK，不用模拟VALID代替真实采集。
4. 实测吞吐、队列峰值、host/actor最坏延迟、功耗和电流。没有iOS WebBluetooth或已做native App的声称；iPad/Android接入仍需平台客户端与真实配对验证。
5. 摄像头、真实笔尖mapper、硬件低功耗与其他provider回调仍缺；本候选不重做评分UI，不自动将窗口原点转为VALID。
