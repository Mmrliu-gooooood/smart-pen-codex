# r27 Schmitt 相机隔离实验：NOFAB / NOPOWER

0745 PCB 3276f044 替换被动 Q201 为 U205 SN74LVC1G14DCKR，新增 C209，R202 改 10k。真实静态 0/96/0，仍有 96 未连；AON41/41、GND71/103、SENS12/12。仅稳定 3.0–3.6 V AON 与受控 USB-JTAG 模式实验，不证明自主上电、掉电、复位、最坏负载或动态时序合格。JP201/202/301 OPEN，provider NULL，未知相机、电芯、充电和制造门仍未关闭。

研究 BOM 的源 MPN_candidate 字段有值，但导出 MPN 列空，不可直接下单。官方定制 DCK 焊盘不是通用 SC70 替代，封装、装配和整笔结构仍待验证。继承的 EP 23.8μm、8 个 in-pad 孔、短段、参考面边缘损失等 DFM/SI 风险未消除。

本包仅四份冻结 manifest 的项目自有文件及精确历史依赖，排除厂家 PDF/cache 与 ELF。独审 mirror 含这些缓存的原 manifest 保留，不伪装成全包。0130/plan.json 活目录曾发生随机 UUID 漂移；隔离重建强制复用 r17 冻结 SHA f367c1346f4bff0cdc2359a7dbd6c9b9aad071ea36f5c6d19375c8657065946f，不修改历史活目录。remaining plan 是只读清点，不是新增布线。移动 GND 工作排除。

独立归档，不改正在上传的 r13–r25 checkout / 计划 / 状态；r26 保持不变，无远端操作。实际复现输出和透明适配边界见 reproduced 文件。

## 精简与独立复现边界
独审 mirror 中 0130/plan.json 为 c68d3178…，仅现场证据、非权威输入；主工程使用 r17 的 f367c134…，实际六个依赖不含 plan。
原 review 清点2581项包含 scratch；发布时按作者 manifest 排除1027个可再生/临时镜像路径别名和5个厂家PDF。原 manifest 不改。隔离 finalizer 透明改为168 native＋78 source冻结文件哈希门，不宣称未发布 scratch 完整；真实 CLI、14负例、正向重放和逆向补丁回退照跑。第一轮完整现场副本复验与最终精简包新一轮复验分开记录，不用缓存结果冒充新检验。
