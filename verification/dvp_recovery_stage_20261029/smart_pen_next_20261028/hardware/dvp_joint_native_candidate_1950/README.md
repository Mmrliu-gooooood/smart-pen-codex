# 12 条 translator↔J202 链的原生研究候选，NOFAB

原生PCB SHA256：184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81。

此候选只是解析拓扑的精确原生化，**不是正式9a03的电气后继，不得制板、上电或连接未知相机**。输入7d197未选布局已主动删除全部旧铜及平面填铜，0/274/0并非功能接近完成；本候选60条线+16个贯穿孔只闭合12个translator到J202的链，真实完整CLI结果为 **0违规 / 262未连 / 0原理图一致性问题**。JP301保持源定义，不合上commissioning链接。

## 原生化与独立核验

- 精确使用 `docs/electronics/dvp_joint_feasibility_1942/result.json` 的76对象以及6项位姿变化，无坐标修补、规则放宽或新增排除。所有实体、net/layer均从真实原生模型检索。
- 从输入移动R225/R226/R227/R206/J105/J107六实体；相对正式9a03累计29实体位姿变化，不能简单27+6=33。`all_placement_changes_from_9a03.json`记录准确旧新位姿。J103/J106仍与9a03相同。
- 独立加载保存后的PCB，核同102 ref/value/footprint/pad-net，原理图/库/规则/project字节不变（个人界面状态.prl不带入），76对象几何/宽度/孔径/net/layer与解析模型逐项相等。
- 自建跨层精确端点图分别从真实translator引脚中心到真实J202引脚中心，12链全通过；逐链删一条必要段的12个负例均失败。仅链连接，不宣称100k偏置支路等整个同名网全连。
- normal和-O结果相同。原生完整DRC使用 `kicad-cli pcb drc --all-track-errors --format json --schematic-parity -o drc.json native/mainboard_revD.kicad_pcb`，真实结果0/262/0。
- `materialize.py --replay-dir <全新目录>`可从冻结输入重建；用记录的实际UUID规范化再原生加载/保存，精确重放同PCB SHA。初次UUID日志误用str(KIID)记录SWIG代理字符串，已明确更正在materialization.json；原始materialize.log保留。该错误只涉及重放元数据，原生PCB从未改变。
- `native_layers.png`从保存后的原生铜和真实pad读取生成，已实际查看。灰pad以bounding box示意，不是制造图；native DRC为实际形状依据。

## 当前严格边界

1. 全部MCU侧、供电地、去耦、偏置stub、压力/诊断/状态接口及平面返回尚未恢复。262未连不会因本局部0违规而被豁免。
2. 未填铜，16贯穿孔的电源面反焊盘、返回颈、地via、RF/PI/EMI及旧关键供应链连通不能继承。12路径90°角/时序/阻抗未资格。
3. 本研究仅SC035/SC031相机研究接口链的物理可布置部分；实际用户30针模组仍未知，不接电，不等同传感器驱动或光学验证。
4. **机械审核已报告候选存在条件包络碰撞**：R206 B(9,47)旧1.45mm包络对现有四上下文夹持壳相交0.181032mm³，最近障碍距B面约0.464793mm；J107.2 B(1.5,83.9)的2mm焊线预算对ACCESS壳相交0.019815mm³，最近障碍约0.414793mm。实际料号/焊接高度未知，不将其填零，也不承诺低矮器件可解决。RevD台架R222另有顶圈碰撞。以独立机械报告为细节依据；尚未解决。
5. 本候选不提升正式接受基线。后续必须先解决机械包络与全系统拓扑，不能直接在该0/262/0上声称交付成品。

## 复核环境

KiCad CLI /usr/bin/kicad-cli，9.0.2。使用/tmp/pen-native1950-{config,cache,data}作为可写XDG目录。验证脚本使用系统/usr/bin/python3的pcbnew；图使用matplotlib。无采购、上电、刷写或远端推送动作。
