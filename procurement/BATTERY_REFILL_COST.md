# 电池、笔芯与两支成本边界

**状态：没有已验证兼容的电池包或IR笔芯，不给虚构总价。** 下列是可复核的候选/价格线索，2026-10-27查询；未下单。全部外币保留原币种，不使用未核实汇率伪装人民币报价。新购两支成本上限合计760元；已有物件“无需新增现金”与成品BOM成本是不同口径，不能把已有相机按零元证明整笔≤380元。

## 电池候选：容量不是唯一条件

|型号/来源|尺寸与负载证据|价格/可购证据|判断|
|---|---|---|---|
|[ASOL10180](https://asolbattery.com/product/asol-10180-cylindrical-lithium-ion-battery/)|120mAh，10±0.1×18±0.2mm；连续30mA、脉冲60mA；PCM选配|OEM询价，无2件价|通常不足以直接支持相机+主控峰值，不能按120mAh容量选用|
|[LiPol LP10180](https://www.lipobatteries.net/lipo-batteries-li-ion-battery-18650/)|厂商表80mAh、5C、Ø10.25×17.50mm|无2件价，完整规格/保护包图未知|可询价负载候选；5C表述须确认持续/脉冲条件及温度，不等于安全批准|
|[Blue Taiyang10180](https://bluetaiyang.com/products/cylindrical-rechargeable-lithium-ion-battery/377.html)|80mAh，10.15×18.1mm，表述带PCM、最大放电1C；规格表存在不同名义电压/尺寸写法|无2件价|最大约80mA不足的风险明显；矛盾先澄清，不采用|
|[OnlyBatteries SKU27009](https://onlybatteries.com/3-7v-10180-80mah-li-ion-battery/)|80mAh，3.7V，flat-top；未提供可设计用的放电/保护证据|页面$7.95/个，最少2个，实际库存待确认|只是零售成本参考，不是可批准电池|

10180只描述大致体型，不规定包络、电流或保护。笔内必须给壳体绝缘、引线弯折及保护板空间；与笔芯并排能否放下由机械截面确定。对峰值负载需用电池端功率而非把不同电压轨的电流直接相加：I_batt≈Σ(V_i I_i)/(V_batt η)，再加主控无线及LED峰值。续航近似t≈可用Wh/平均W；没有整机实测与容量测试不能承诺小时数。禁止电芯直焊；需要供应商焊片/受保护成品包和匹配充电限流。

## 笔芯候选

[SCHMIDT官方目录](https://www.schmidttechnology.de/wp-content/uploads/2023/04/Schmidt-Writing-Instruments-Technology-Catalog.pdf)确认S635是D型金属笔芯，提供不同颜色/笔画规格。[美国经销商Yafa](https://yafabrands.com/collections/all/products/schmidt%C2%AE-635-mini-d1-ballpoint-refill-medium-point-4pk)标4支$11，约67×2.3mm；若只装两支但必须买4支，首批现金分摊是$5.50/成品，不是简单按$2.75/支忽略剩余采购。[ARTEX的S635M销售页](https://www.artexpen.com/en/products/%E5%BE%B7%E5%9C%8Bschmidt%E6%96%BD%E5%AF%86%E7%89%B9%E6%B2%B9%E6%80%A7%E5%8E%9F%E5%AD%90%E7%AD%86%E8%8A%AF_%E8%BF%B7%E4%BD%A0d1%E5%9E%8B%E9%BB%91%E8%89%B2-635m)标TWD120/支、67mm、管径2.35mm。公差图和实际批次须核验，不强塞2.3mm孔。

**仅建议D1作为小尺寸几何试样，不声称该墨水在IR透明或不遮点。** 蓝/黑色都需与实际码纸同测。不要切割满墨笔芯来适配；更换笔芯后重新检查外参和偏摆。

## 全成本关闭规则

逐项有真实两支采购数量/含税金额：相机与镜头/滤镜/镜座、主控/无线、传感器、电源/保护/充电、LED及驱动、PCB、FPC和连接器、被动件、焊接装配、结构加工/打印、紧固/胶水/镜窗、笔芯、测试耗材和一次性打样费。运输单独列出而不是混入或漏报。税、损耗、MOQ余料和NRE不能悄悄排除。

当前仅IADIY有清晰单件公开相机价$38；Hampo价区间未证明适用2件；其余多数关键项未知。因此**预算是否能≤380元/支=未证实**。使用采购账本CSV填入报价后才求和；空白不是0。下一步最低现金支出应是复用已有SC035HGS台架，不是盲买三种相机。
