# 比较证据，不是可制板候选

- raw_grid_NOT_FOR_USE.kicad_pcb.gz 是两条总线初次接通后的未简化原生备份，仅用于回退/比较。它早于顶部 via 远离 RF 及 MEMS pin4 左向逃线修正，不能替代最终 native。需要同 basename 项目时，仅在隔离目录解压并复制本包 native 源树，不覆盖冻结文件。
- rejected_top_via_down_drc.json：顶部 via 下移 0.45 mm 会撞 IRQ/STRAP/CAM_SDA，拒绝。
- pre_MEMS_escape_fix_drc.json：顶部 via 左移后电气 DRC 未新增，但后续全 body 筛仍发现 pin4 外圈穿入；最终已修正。DRC 不是同侧 body 合规证明。
