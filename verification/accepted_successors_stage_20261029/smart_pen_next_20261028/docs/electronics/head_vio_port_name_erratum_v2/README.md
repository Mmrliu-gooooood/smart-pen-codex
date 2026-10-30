# SENS_VIO 供电端名称勘误（2026-10-29 07:08 UTC）

绑定 `hardware/j202_low_speed_reference_candidate` 的冻结 PCB `9a033544…40c038` / manifest `b7e8ecbf…99a5d18`。不修改该包，不变更任何线路、实体、源或接口。

其 README 第 14 行将负载概称为“AXC/TCA VCCA”不准确；协调消息和旧恢复索引也沿用了此简称。实际原生源和引脚网络为：

| 器件 | 相机参考域引脚 | 原生 pin 名 |
|---|---|---|
| U201 AXC8 | 23、24 | VCCB |
| U202/U203 AXC4 | 16 | VCCB |
| U204 TCA9517 | 1 | VCCA |

它们均接 `SENS_VIO_1V8`。A/B 域命名在不同器件不一致，不可互换读取数据表方向与传播延迟。AXC 数据方向仍按既有 DVP 时序预算的相机 B → 主控 A（输出时钟/控制按其实际相反方向）；本次没有证明额外时序资格。

该行“外部已资格化紧凑头提供”应明确读作 **未来外部头部电源必须先经资格化，才能供给此参考输入**，不是现在已有通过资格的头板。本轮没有设计、批准或验证外部 1.8 V 电源；禁止据此接未知定制模组。输入合同、JP OPEN、NOFAB 和所有电压顺序/动态/回灌门均不改变。

`check.py` 从冻结 XML 的 libpart pin 名和 net 两处逐项核对，normal / -O 输出相同。仅修正文档/沟通措辞，不冒称新的电路测试。

## 合同字段同一勘误

`interface_reference_contract.json` SHA **65eca5fea27c4aca954e7a3438e52ac3cc6300b87fd4d6b5686e3f5071c58e23** 中 `VIO_direction` 的 translator A domain 与 `VIO_load_boundary` 的 AXC/TCA VCCA 同样采用上述逐器件更正：AXC 为 B 域 VCCB，TCA 为 A 域 VCCA。外部 head 经资格化仍是前置要求而非既成事实。自动脚本也绑定该确切合同 SHA。

本 v2 是对同日 v1 的增补，额外绑定合同字段；v1 原文/manifest 保留，不覆盖历史。后继审核/发布应同时携带本 v2，不让旧措辞单独成为系统接线依据。
