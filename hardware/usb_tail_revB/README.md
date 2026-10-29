# USB 尾板 Rev B — 孔距几何候选，装配未资格化，NO FAB

2026-10-28。此目录是冻结 Rev A 的独立工程变体。为保留 native hierarchy/UUID 及可比对性，内部 KiCad basename 仍为 `usb_tail_revA`；以目录 Rev B 和本文区分版本，不能覆盖 A。

## 本版实际改动
仅 J101 四个逻辑地 pad（两块实际铜，A1/B12 和 A12/B1）靠定位孔一端退让 **0.08 mm**。宽 0.60 不变、长 1.15→1.07，中心朝远离孔方向移 0.04；远端边保持不变，圆角半径仍 0.15，同位编号/网络保持。新的自有封装名称 `USB4105_GroundHeelTrim80um_AssemblyUnqualified` 明示未批准装配，不冒充 GCT 官方 landpattern。

所有电气 pin/net、孔径/孔位置、其他铜 pad、信号布线和项目设计规则保持。这里“保持”指人工定义的 pad、track、via、zone 设置与规则，并不表示生成后的全部铜多边形逐字节不变：B 重新填铜后，B.Cu filled_polygon 在多处改变，独立审查发现部分过孔/走线周围间隙比 A 缩小约 0.05 mm。A/B 项目规则逐字节一致、zone local clearance 均为 0.15 mm，未降低设计规则；新填铜结果纳入 B 的实际 DRC，但不能称除焊盘外全部铜相同。原 0.25 mm 孔到铜规则没有降低，没有 DRC exclusions。理论孔铜净距 0.272329 mm。包围矩形面积减少 6.9565%；计入 R0.15 圆角的实际铜面积减少约 7.16%。

新运行 ERC 0 / DRC 0 / 未连接 0 / native schematic parity 0。`delta_checks.json` 独立比较所有 pad 的网络、孔径、铜层、位置、尺寸，以及完整原理图 pin/net map；只允许上述四 pad 差异，项目规则逐字节相同。**DRC 通过只证明此候选几何/连接规则，不证明焊接覆盖或可生产。**

## 未关闭的最小门槛
GCT 官方 B4 图给出了推荐 0.60×1.15 焊盘及 ±0.05 mm 布局公差、16×0.20 尾脚宽、侧视/底视 0.38 等尺寸，但没有足够的完整金属焊接接触长度及相对焊盘位置公差链，不能由图片比例证明删去 0.08 mm 后的最坏 heel 焊缝覆盖。推荐图的 ±0.05 是尺寸公差，不是任意更改名义焊盘尺寸的许可；本版 1.07 明确超出原长尺寸下限 1.10。

释放本版前需要：实际 USB4105-GF-A-120 尾脚/定位柱尺寸检查及装配 DFM，确认跟部/趾部/侧部焊接覆盖、钢网和贴装偏差；若不接受此候选，回到 A 并取得支持 0.1944 mm 孔铜距的明确工艺确认，或换已核实新连接器封装。不能把本版标成原厂认可。仍需 USB 线束、阻抗/ESD、0.8 mm 板机械承载及整笔安装检查。无 Gerber 放行。

## 重建
`/usr/bin/python3 tools/build_variant.py` 从同级冻结 A 重建 B 并运行真实 KiCad ERC / DRC / parity；随后 `/usr/bin/python3 tools/verify_delta.py`。两脚本固定可写 XDG 配置。不需下载私有文件。

详见 `../usb_tail_dfm_study/README.md` 的孔距、公差和工艺证据。
