# 当前主板工作版：a51a57 / 13未连

**NOFAB / NO POWER：不能投板或上电。**

首次下载仓库后先运行 `python hardware/mainboard_wip13_20261103/restore_board.py`，再打开 `candidate/mainboard_revD.kicad_pro` 与同级顶层 `.kicad_sch`。不要把 `candidate/schematic/mainboard_revD.kicad_sch` 历史核心子图当成完整顶层。

PCB SHA256：`a51a57bcb5fa50ffd885deb988b045eac39d5e02cd94547f1060e3ece926edad`。53个原生依赖直接保存，PCB以gzip/base64小分片传输，运行脚本后还原第54个原生文件，SHA逐字节验证，PRL缓存排除。103元件，238孔。独立复核后仅作为有限WIP接受，不代表制造资格。

[进度](../../docs/progress/2026-11-03.md) · [检查证据](../../verification/mainboard13_20261103/README.md)

SCL仅U204→R242接通，J202仍分离；剩余连接以DRC报告为准。已知孔周参考开口、去耦性能、SI、制程、实际相机/FPC和工具空间未验证。没有Gerber制造包。

## 发布兼容说明

单个1.44MB板文本上传未成功，本次使用标准库恢复脚本与小分片。仓库克隆后不能直接打开最新板，须先运行上面的脚本。它不下载网络内容，不修改其它工程，不覆盖不同内容的本地板。CI验证相同恢复哈希。不是以旧板替代最新板。
