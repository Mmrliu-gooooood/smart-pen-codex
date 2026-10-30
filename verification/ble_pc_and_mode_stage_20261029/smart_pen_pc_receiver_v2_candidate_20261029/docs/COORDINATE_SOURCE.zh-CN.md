# 给现有网页的窄坐标数据源合同

固定原repo：`smart_pen_original_20261028` commit `0f8b569176c77dad34aaf83bb008eb118c9f1208`，只读研究了 `digital_pen_ov5640/pc/src/digital_pen/engine/session.py`。
其 `WritingSession.add(times, points)`接收秒和纸面毫米，纸面+x向右、+y向上；既有server/service/UI可继续复用。本次不调用它、不创建Engine、不重写评分或AI。

`python -m pen_receiver replay --state-dir ... --session ...`按选定journal的device/session和seq顺序导出NDJSON。schema为`pen-coordinate-source/2`：

| 类别 | 当前含义 | 可给正式评分？ |
|---|---|---|
| `BEGIN`/`END` | 从CONTACT、GAP、seq/session/page/时间边界派生的诊断边界；`boundary_derived=true` | 否，不含坐标 |
| `DIAGNOSTIC invalid_or_control` | 原flags无VALID；可能是BEGIN/END控制、失效观察或GAP，原协议无独立BEGIN/END枚举 | 否 |
| `DIAGNOSTIC wire_valid_unqualified` | payload声称VALID，但冻结INFO为NO_SENSOR，物理资格未成立 | 否 |
| `window` | 固件解码窗口仅内部诊断，48B协议不传窗口；因此当前为null | 绝不能当笔尖 |
| calibrated physical-tip VALID | 需要真实camera资格、标定/姿态mapper及部署身份链，当前没有 | 当前不产生 |

所有当前事件 `UI_allowed=false`、`coordinate=null`、`calibrated_physical_tip_VALID=false`；保留 `flags`/`wire_VALID`/`contact`/`gap`/原始x_um,y_um/confidence，只能给独立诊断视图。
session与timestamp_us输出十进制字符串，避免JavaScript超过53bit精度丢失。device/seq/page uint32可保持JSON整数。缺seq、GAP、page/session变化、时间不递增均断边界；不插值、不把断笔连接，不把(0,0)控制记录画成实际落笔。

**不要把当前NDJSON直接接入旧的 `upstream_web.py` point/stroke路径**，旧候选基于不同的synthetic/qualification前提，不能只看flags&VALID便渲染正式评分。
将来单独批准的源适配应在真实资格门后生成 `POINT`：按page分流、`x_mm=x_um/1000`、`y_mm=y_um/1000`、时间转秒（先减同笔画基准避免浮点精度损失）、按原UI显式变换画布轴；BEGIN/END只控制笔画，不当点。
质量阈值/最大采样间隔须用实测项目参数，并断开无效、低置信、重复/缺号、跨页和超时。重放迟到记录须重新投影，不能直接在已有实时墨迹中插入而跨断点连线。当前未实现这一步，也未声称旧web功能端到端验收。

## v2来源与合流身份（必需）

每个事件（BEGIN/END/DIAGNOSTIC及接收状态事件）携带持久`source_namespace`。
它是带域分隔的规范JSON `(profile, peer_scope, exact target, expected device)` 的SHA256，初始化存入meta，重开/导出前复算比对；**不是随机密钥、长期token或硬件认证**。
相同标签/device但不同target必定使用不同命名空间；相同绑定clone/reopen保持同namespace，所以同来源副本能按record key去重。
不输出原始MAC/平台UUID；但确定性hash不承诺匿名性或抵抗已知目标枚举，仍属本地私有数据。

每条记录及其派生边界另含`record_sha256`（原48B的SHA256）。消费者合流身份必须为
`(source_namespace, device, session, seq)`，不能只用显示标签。选定导出集合可先用
`pen_receiver.identity.EventIdentityGuard.accept(record_event)`：只接受DIAGNOSTIC/DURABLE_RECORD；
相同key/相同摘要返回False（重复），相同key/不同摘要抛错停止，缺namespace拒绝。
该guard是内存预检，不赋予ACK/认证/评分资格；边界事件不直接合成墨迹，重复导出/迟到记录要重新投影。
当前所有v2事件仍UI_allowed=false，namespace不会把NO_SENSOR升级成正式点。
