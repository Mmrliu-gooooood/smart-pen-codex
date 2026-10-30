# 官方来源、依赖与平台边界

核对日期2026-10-29；网页stable页自标3.0.1，本机已安装包是3.0.2。实现同时核对本机3.0.2公开API源码和METADATA，不把文档页标签误写为本机版本。

## 本机依赖

- Python 3.12.14，SQLite 3.53.1（离线核心只用标准库；候选要求Python≥3.10）。
- 可选radio直接依赖 `bleak==3.0.2`；安装元数据License-Expression MIT。安装位置是既有 `smart_pen_host_venv_20261028`，本轮没有pip安装/下载。
- Linux现有间接依赖 `dbus-fast==5.2.0`（安装METADATA许可MIT）。Windows依赖WinRT系列，macOS依赖PyObjC系列；未在本环境安装/测试这些平台依赖，**requirements-radio.txt不是跨平台完整hash锁文件**。
- 不分发Bleak源或二进制；`THIRD_PARTY_NOTICES.md`说明依赖许可，清单记录本地METADATA/LICENSE/API文件hash。本目录没有重新许可原工程或copy整套历史。

## 官方能力与实际证据

[Bleak backend官方文档](https://bleak.readthedocs.io/en/stable/backends/index.html)列出Windows 10 16299+、Linux BlueZ≥5.55、macOS≥10.15的后端支持。这是库的平台范围，**不是本候选在这些OS上的互通/安全验收**。

[BleakClient官方API](https://bleak.readthedocs.io/en/stable/api/client.html)支持异步context、notify callback、GATT读和显式`response=True`写。用地址/UUID字符串构造client会触发隐式发现；本候选没有默认扫描，但显式connect可发生这个库行为。pair=True不是SC/MITM/键长证明。

[macOS官方Bleak后端说明](https://bleak.readthedocs.io/en/stable/backends/macos.html)：目标为本机CoreBluetooth UUID，不是跨机器稳定MAC；pair=True被忽略，受保护特征访问触发OS配对提示，需系统蓝牙许可。本候选先probe INFO以触发该路径，再在本地批准后重新读；未实机验证。iOS/iPad/Android native不在此次范围。

[Python msvcrt官方文档](https://docs.python.org/3/library/msvcrt.html)是Windows非阻塞文件区锁与本地键盘API依据。代码有Windows分支，但当前证据仅Linux mock/子进程测试；Windows DACL人工确认不是自动证明，不据此声称可正式使用。

[SQLite synchronous官方说明](https://www.sqlite.org/pragma.html#pragma_synchronous)：DELETE模式使用EXTRA以在rollback journal删除后额外同步目录，避免只用FULL时部分文件系统最后事务可能丢失；[atomic commit说明](https://www.sqlite.org/atomiccommit.html)描述其对锁/同步/硬件的假设。[fullfsync说明](https://www.sqlite.org/pragma.html#pragma_fullfsync)仅macOS对应F_FULLFSYNC。设置和测试不是物理断电、磁盘诚实性或硬件耐久证明。

## 本地冻结依据

- `smart_pen_ble_transport_candidate_20261029/docs/{INTEGRATION,DEVICE_GATES}.zh-CN.md`
- 同目录 `src/pen_ble_core.c`、`src/pen_ble_idf.c`、`frozen/portable/pen.{c,h}`及独立review。
- `smart_pen_app_pipeline_20261028`原48B/ACK/session/完整发送票据与contact control逻辑。
- 原上层repo上述固定commit，仅引用坐标/笔画入口，不执行摄像头/UI。

逐文件绑定见`verification/DEPENDENCY_EVIDENCE.json`和`verification/MANIFEST.json`。清单不是数字签名；CRC也不是身份认证。
