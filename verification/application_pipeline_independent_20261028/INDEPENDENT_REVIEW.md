# 应用协调器独立审查（最终软件候选复验）

审查对象：`smart_pen_app_pipeline_20261028`。不涉及设备刷写、eFuse、密钥、采购或 GitHub 写入。审查者不修改作者源；修复由作者完成。

## 结论边界

这是将既有 Gray8 解码、接触状态机、耐久日志和重放模块接起来的应用候选，**不是完整可运行点阵笔固件，更不是硬件验收**。图像测试使用实际灰度像素数组和真实 C 解码路径，但像素由测试生成，物理笔尖映射由显式 test double 提供；不能称为真实摄像头采集验证。

真实 SC035HGS DVP/寄存器初始化、GPIO/低功耗唤醒实现、BLE 安全连接与 ACK 接收适配器、物理姿态/标定映射、通知指示器均未实现。供应器默认 NULL；执行默认关闭。不能以打开 Kconfig 为由认为摄像头电平、引脚、IR、Flash 型号或电池已被批准。

## 审查发现及修复闭环

1. `next_ack()` fatal 原来只退出内层 ACK 循环；已改为停止 actor、关闭持久层。
2. 接触状态机故障原来可能返回成功但被 actor 忽略；现在 camera/contact/IRQ/clock fault 都停止记录并 safe_stop。
3. 仅查询 backlog 原来会调用真实 store.offer，间接授予 ACK 权限；现在影子 store 只读查询，应用额外要求成功提交包的 session/seq/connection_epoch ticket。busy 首发不能授权 ACK。
4. ACK 同时验证接收时可信链路状态和当前状态；每条 ACK 重查链路，发送携带 expected epoch，适配器须原子验证连接。payload 不能提供认证依据。真实 BLE 适配器尚缺，原子性仍是必须实现的合同。
5. 已耐久但未 ACK 的 backlog 原来永久阻止休眠；现在只以真正未提交事务阻止睡眠，sync 屏障后撤销 ticket/offer 并停止会话，未 ACK 记录保留。重启新 session 后重放。
6. quiet/sync 回调晚于 deadline 却返回成功原来可继续睡；独立负例曾实际复现。现在回调后及维护 guard 后复查时限。同步操作不能被此检查抢占，实板仍须限定最大耗时。
7. 全日志/32 会话原来缺乏应用维护路径；现在停止采集进入只读补传。仅全量耐久 ACK、无事务、传输静默、当前压力/IRQ/队列安全 guard 后回收；先持久 erase intent，再擦除，再清 intent。新 epoch 经持久分配后才重新记录。未 ACK 不可覆盖。正常抬笔不做整区擦除。
8. 异步静默等待中的 USB 睡眠许可撤销、dirty 状态变化曾绕过取消/累计超时；现在取消并 resume，CP 回到 READY 可再次申请；维护等待期间 dirty 变化仍受累计时限约束。

## 独立追加测试

三个脚本读取明确指定源并生成独立 C 测试，不改作者文件；真实运行原模块。

- `run_additional_pipeline.py`：额外 x/y 范围、pose_valid=2 拒绝；直接底层 store.offer 不可冒充已发送 ACK 权限。包含作者原 Gray8/模拟输入/标定与时间/接触/重放负例。
- `run_additional_actor.py`：编译真实 app_main，补 fatal poll、apply、storage open、begin_boot、迟到 quiet、迟到 maintenance guard。包括作者的默认关闭/缺供应器、fatal ACK、四类接触故障、离线睡眠、容量与 USB/dirty 竞态用例。FreeRTOS、时钟、Flash 绑定为窄测试替身。
- `run_additional_maintenance.py`：补负 pending/quiet、非法 pressure/IRQ 状态、log/contact fault、记录仍进行中、sync 失败均不能擦除，replay sleep sync 失败不能睡；包含32会话、全 ACK/未 ACK、partial erase intent 恢复与旧 ACK 拒绝。

各脚本 normal、NDEBUG、ASAN+UBSAN。ASAN 设置 detect_leaks=0（没有将泄漏检查计为验证）。测试不能证明目标芯片实时性、无线并发原子性或实物掉电行为。

## 可复现

```sh
export PEN_REVIEW_SOURCE=/absolute/path/to/repository
export PEN_REVIEW_OUTPUT=/tmp/pen-independent-tests
python run_additional_pipeline.py
python run_additional_actor.py
python run_additional_maintenance.py
# 完整仓库门限须在源仓库执行，使用安装好测试依赖的 Python：
python software/verify_host.py --upstream-pc-src /path/to/digital_pen_ov5640/pc/src
```

## 尚存产品边界

- 窗口坐标只能作为 mapper 输入，不能直接标 VALID；mapper 必须返回同帧/同时间、来源、标定版本、页与可信姿态，仍需实测姿态变化下的笔尖误差。
- 当前 paper/page 是固定配置；未完成自动多页识别。
- full-log 回收是保守整区维护，不是实时滚动日志或磨损均衡；容量上限和32会话门必须向用户可见。
- ACK 保证取决于可信适配器：连接 epoch 跨重连/重启不能复用；安全策略/接收队列事件须串行；不能旁路调用旧 storage_idf_ack。
- final sleep 的压力/IRQ 原子复核、唤醒源装配、迟到边沿保存由真实供应器负责；主机 mock 不能替代实板睡醒测试。
- Flash/NVS erase-intent 与新 epoch 的实际断电测试、BLE 配对/重连、功耗/温度、续航、光学/IR、电平与安全资格均未完成。

最终结果见下；通过仅限列明的软件候选检查，不代表实板或产品安全验收。

## 大容量维护不是实时无停顿写入

8MiB profile 的日志区是 `0x3e0000` 字节（3.875MiB），并不是整个芯片均可用于轨迹。每槽64字节，共63,488槽；若每秒60/120槽，理论上限约17.64/8.82分钟，还会被边沿/缺码等记录及32会话限制提前消耗（session/seq已含每槽，不重复扣除）。不能把它宣传为四小时离线轨迹容量。

全日志扫描和整区 Flash 擦除都是同步调用，当前 actor 不能在其内部抢占。维护 guard 只证明开始时无旧事件/事务，随后必须保持capture inhibited并保留新压力/IRQ边沿；维护期间无图像处理、无新轨迹写入，不能把未采样或未耐久写入的数据标为 VALID。重新拿起发生在维护中时，会有未量化停顿，不能声称“拿起即写”“无断笔”。

deadline 在回调返回后检查：若扫描/擦除很慢，能够受控停止后续动作，而不是中途停止擦除。成功擦除但超时后不得继续 begin_boot/记录；部分擦除失败保留 erase intent 并停机，下次开机恢复。同步调用永不返回/设备卡死不受该软件时限抢占保护，真实板级必须另行验证看门狗、掉电恢复与最坏耗时。不得以主机内存 mock 的时间代替实物 Flash 测量。

## 最终固定版本与结果（2026-10-28 22:18 UTC）

- 最终39文件源清单SHA256：`99ff5c16021f193bc3b3478d3ee73ccf73b336e7ebc3cac512c76a44caeb2e47`。测试时版本为`dbc04bd51c6d2de7782b07dc2c27fee8974f8724bc96b7737851e6768ebfe462`，最终仅一份容量说明文档修辞改变，实际代码/测试/构建配置逐项hash未变，见 `final_evidence/doc_only_update.json`。最终清单与所有实际依赖C/头文件/Python快照均已核对。
- 独立完整host gate：**83 tests，0 skipped，PASS**（21.852秒仅为本机测试总用时，不是MCU/Flash性能），见 `final_evidence/full_host.log`。
- 三组独立追加测试normal/NDEBUG/ASAN+UBSAN全通过。actor含7个额外故障/迟到边界；成功擦除但超时的负例证明safe_stop、无新begin_boot、无resume、无睡眠。见 `final_evidence/independent_extra.log`。
- 两处维护前已有明确`report(-109)`且recording=false；作者25个actor场景加入通知次数与erase次数一致性断言。通知是供应器回调，不是已实现的实体灯/手机UI。
- ESP-IDF固定`67c1de1eebe095d554d281952fde63c16ee2dca0`。作者三目标构建成功后，独立执行三目录ninja复核成功，并核实ELF/BIN/分区二进制SHA256匹配；见 `final_evidence/sdk_recheck.log` / `sdk_artifacts_checked.json`。
- 默认禁用/enabled-compile/8MiB完整actor编译应用BIN分别192704/214656/215424字节。三者均保留NULL供应器，不能运行实际笔。默认和普通enabled-compile使用SDK的2MiB默认表且无pen_records；只有明确8MiB profile具备候选日志区，运行时guard先于storage_open核查逻辑/物理容量与精确分区。profile关闭路径不调用Flash硬件API，guard失败不得open持久层。
- 应用未链接OTA安装/更新执行路径；OTA默认不运行。OTA双槽分区和bootloader rollback配置不等于OTA功能已完成。

**审核决定：可作为带边界文档和测试证据的软件候选备份；未发现本次已审范围内尚未修复的阻断逻辑。禁止标记为整笔完成、可直接刷机或消费级安全已验证。**
