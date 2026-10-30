# 当前整合候选：主板 016d → 电源单点供电 Rev B（NOFAB）

此目录是**新版本**，不覆盖 `../mainboard_integration_harness_v3`。当前后续整合优先采用已独立复核的 `power14_single_feed_revB`，不是直接装配/通电许可。

|对象|实际 PCB SHA256|地位|
|---|---|---|
|主板 selected 016d|016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e|当前79封装、四接口未实现的六层条件候选|
|power14_single_feed_revB|94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc|当前线束后续整合目标；单点供电几何修复通过，仍NOFAB|
|原 power_integrated_layout_14x45|5c5764e7576c9461464c12da3531410e63ef4db32a28a67a5fa6125ef0b92014|历史v3映射单独成立，不是RevB板身份|
|旧 power_core_layout_candidate 四pin J5|详见JSON明确hash|不是当前接口，禁止替代|

本候选明确 pin1 USB_EN1→/core/USB_EN1、pin2 USB_EN2→/core/USB_EN2、pin3 GND→GND。两端分别是 J107 与 J5，三线 1:1 正确。但**网络身份相同不意味着板版本相同**：验证器要求精确 Rev B 原生PCB/source哈希，拒绝用原14×45三pin板冒充RevB，也拒绝旧四pin板。原14×45只有在旧v3合同下可作历史逻辑证据。

旧四pin J5 的 pin3 为 /CE_PERMISSION_EXTERNAL、pin4 才是 /GND；不能套用当前 pin3 接地。当前三线没有 CE 许可，不关闭 commissioning JP1。线束采用明确 EN1/EN2/GND 信号标记和针号，不凭翻面照片猜左右；防反接实体、应力释放、线径、接地先后与装配姿态/RF避让尚未验证。

依据：`docs/verification/power14_single_feed_revB_review_20261028/README.md`，对应电源48项 `SINGLE_FEED_REVB_MANIFEST.json` SHA `0caac8aeec8578a8b7cce467ae67f3d487bca992521c7fe3e53d35922dbe3637`。该独立审查通过的是几何、真实连通及C1外额外主干入口消除；不代表复杂温控动态、NTC/电池资格、Kelvin返回、0.15mm支路温升/EMI或充电安全全部合格。

普通/`-O` 8个案例通过。主板与电源所有native sheets和PCB/XML逐项锁定；仍不授权采购、生产、连接未知相机或充电。完整实物线束/电源动态/电池验证、四个未实现主板接口及整机BOM价格仍开放。
