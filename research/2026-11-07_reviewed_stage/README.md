# 2026-11-07 精选研究阶段

**HOLD / NOFAB / NOPOWER。设计持续进行，commission OPEN。** 本目录保存尚未采纳的研究源、可复跑宿主测试和有限审查结果，不是可生产、可通电或可刷写的整机版本。它不覆盖仓库默认固件或旧原生PCB入口。

比较基线为公开 main 提交 `31c92f7df8628904bbf4f5e7b04d01000a44f710`。新源文件和测试位于隔离目录；没有改动默认CMake、板级provider、GPIO、协议、BOM或安全开关。

## 1. 固件布尔、维护与ACK安全门 R3

`firmware/guard_r3/candidate/firmware/` 包含5个项目源码覆盖；`boolean_guard.patch` 是同一完整改动的补丁，二者不能重复应用。原基线每个文件的SHA256及Git blob身份见 `BASE_DEPENDENCIES.json`。

仅严格化安全输入的合法整数范围，防止把非法非零值当作允许。低层ACK问题以“调用者传入非法安全事实且offer身份正确”为前提；没有证明远程攻击者可控制这些实参，也没有证明实际设备丢失数据。原有主应用ACK票据门本已严格，不能把低层API缺口写成主应用被绕过。

冻结作者记录：65次宿主执行，56通过、9个预期原版失败、0意外失败。独立ACK复核为另11次，9通过、2个预期原版失败。相加不是新的独立样本数；本次公开入口复跑结果另见 `PUBLICATION_VALIDATION.json`。

最后一次ACK sync返回失败时，完整ACK可能已经持久化；错误返回不能一律解释为“未发生”。本结果来自宿主内存/NVS替身，不是实际Flash掉电、无线认证或目标设备保证。

## 2. 活动状态侧车 R2

`firmware/activity_r2/candidate/firmware/application/` 的两个新增源/头文件提供可选只读快照，不修改旧ABI或默认生产actor。拒绝输出与watch/app/store重叠，拒绝失败初始化对象；调用失败时不能继续消费旧输出。

`recording` 仍表示日志会话开放，不等于正在出墨。READY不等于相机已合格，TRACKING不等于本次新点已落盘，LOGICAL_ASLEEP不等于CPU实际睡眠。范围检测依赖目标平台平坦地址表示，调用仍须串行。

冻结作者35次：32通过、3个预期R1失败。独立最终42次：39通过、3个预期R1失败；其中包含完整35次重跑，不应重复累加。R1源码只作为明确标记的负控保留。

## 3. C201仅两段走线差分

`hardware/c201/ADDED_SEGMENTS.sexpr` 只包含冻结候选新增的两段自制铜线；`EXACT_DELTA.json` 绑定前后整板SHA和边界。没有公开整块PCB、厂家模型、封装库、CAD或276项外部原路径依赖。本差分不能从仓库现有旧板独立恢复C201工程，不提供制造输出。

冻结研究记录：369→368未连、Logic GND 44→45，Power GND 46仍另岛；8旧warning和2旧parity未解决。C201.1/U201.VCCA仍是分离单点，所有返回源切断后仅剩两个电容的浮地岛。新增连线不证明有效供电或去耦。

`FROZEN_REVIEW_SUMMARY_ZH.md` 是原冻结包说明的节选来源文件，提到的作者/独审全套文件没有随本精选目录全部发布。它不是本目录的完整文件清单或复现承诺。

## 4. P5KS触点与供回路合同

`hardware/p5ks/FROZEN_CONTRACT_SUMMARY_ZH.md` 保留项目自制分析。20对匿名位置的坐标对应不是采用的针号/网表或实物导通验收；实际40焊盘仍空编号/net0，不能按推测分配电源。Logic与Power参考地、端子落座、ground-first、部分供电和反向馈电仍未完成。

本轮不再复制厂家图纸。官方P5KS端子编号说明：
https://ac-faq.industrial.panasonic.com/migration/ja-jp/knowledge/control/connector/connector/base-fpc/conn-header-socket-pin-num

## 运行宿主研究检查

使用包含基线文件的完整仓库，Python 3标准库和支持C11的GCC/Clang；UBSan模式需要编译器运行库。无需安装ESP-IDF，也不访问硬件。以下`/path/to/checkout`是仓库路径，输出目录必须不存在且位于源码/仓库外：

```
python3 -B research/2026-11-07_reviewed_stage/firmware/guard_r3/run_host.py --repo /path/to/checkout --out /tmp/pen-guard-review-new
python3 -B research/2026-11-07_reviewed_stage/firmware/activity_r2/run_host.py --repo /path/to/checkout --out /tmp/pen-activity-review-new
python3 -B research/2026-11-07_reviewed_stage/run_supplemental.py --repo /path/to/checkout --out /tmp/pen-supplemental-review-new
```

入口先核51个公开基线依赖的SHA，再生成独立宿主测试程序和合成图像；任何不同的源码应停止并重新审核，不自动改写基线。输出仅写指定新目录，不改冻结证据。两个主要入口是为发布新增的路径/输出包装，测试正文保持原研究逻辑；包装差异见公开来源说明。

补测入口另执行8次：same-offer重试和恢复故障各1次UBSan，状态侧车范围/生命周期分别在原基线及R3覆盖上做O2、UBSan、ASan+UBSan共6次。它使用随目录提供的自制依赖，不能冒称重跑了原独审全部历史场景；ASan关闭泄漏检测，未运行MemorySanitizer。

`RESULTS.json` 是历史作者执行记录，不是每次运行时覆盖的文件。少量宿主绝对路径已替换为占位符，来源原SHA与修改类别在 `PUBLICATION_MANIFEST.json` 明确记录。独立复核报告保留原范围；没有把它们冒称成本次执行。

## 明确未完成

未运行完整宿主aggregate、ESP-IDF目标构建、真实provider联调、刷机、相机/Flash/BLE/USB/GPIO/电源/热/装配/制造测试。源PCB、全电源供回路、OE默认禁用、1.8V来源、相机兼容和电池安全仍未完成。`qualification`、`current_rating_A`、`effective_C`继续为null。

厂家原件、用户原始附件、私人邮件/报价/照片、密钥、二进制/缓存、临时备份及活动未冻结后继均不在本精选目录。项目历史和完整私有恢复链仍需保留；这个目录不能替代它们。
