# r12 — BLE / PC V2 与 CAM_ON / J107 冻结本地复现包

**本地备份，NOFAB；无外部写、无线连接、设备操作、采购或制造。** 原软件/硬件只保留字节完全一致的冻结源，未替换应用固件或既有 r4–r11。

## 精确范围

- BLE 的 121,382 字节原 tar SHA256 `22cf08c99bc35a095d5831577f31f14a747c56ac05f6f9b1ebc87e46fd3d60b3` 已逐个检查路径/成员/hash，与现有源核同：**123 个文本成员**（含 review/历史构建证据和 DELIVERY_MANIFEST；source_manifest为41项，独审REVIEW_ARTIFACT_MANIFEST为63项，不是123项源码）。只归档解包文本，不重复收 tar，不收 SDK/build/BIN/ELF。冻结的 `review/run_output` **仅清单列明文本日志/JSON**，不是执行产物。
- PC V2 原 MANIFEST 的37项+清单；独审23顶层项+清单。不拷独审目录的 `source` / `source_v2` 副本。
- V1 仅保留三缺陷最小复现需要的五个模块、一个 MockClient 测试模块、原 README/第三方说明及原完整 manifest，共9项。**V1 有真实失败，是历史反例，不是推荐入口**。原 manifest 的其他成员有意未附；原 `check_frozen.py` 要完整V1，故本精简包不运行它，不称V1全包。新适配器核对所有选中hash。
- 五个硬件包的完整成员及各自manifest：CAM_ON作者103、独审91；J107作者110、独审111；当前RevB逻辑线束8。原报告写作时的“审查待完成”等时间状态不追改，后续独审另存。
- **622件原始文本**；新说明/适配/结果单列出处。`SOURCE_SUBSET_SHA256.json`、包外 `source_path_map.json` 给出精确映射。凭 manifest 选取，没有收移动 IRQ/MEMS、相机独审或新壳树、厂商私密PDF/INI/照片。

## 离线复现

仅需已有 Python 标准库可跑快速hash/存档门检查，无 SDK、Bleak、联网或设备：

```sh
python3 portable_check.py
```

软件复验需已有主机 C 编译器及 ASAN/UBSAN 支持，SQLite 属 Python 标准库；所有源码在临时目录运行，生成二进制、SQLite和日志随临时目录删除。**不要运行 `pen_receiver receive` 或安装 radio 依赖作为本次复现步骤**。

```sh
python3 portable_check.py --software
```

这会跑 BLE 作者 normal/NDEBUG/ASAN+UBSAN、独审 core/actor/IDF-API **stub** 三模式；PC V2 作者45测试和独立9测试各 normal/-O，真实C/Python500条交叉与48记录字节/20 ACK字节破坏负例，以及三项 V1→V2 缺陷原始复现器。队列测试约2.1秒的实际调度时间允许自然波动，只验证超2秒和正确ACK结果，不与旧计时值逐字等同。

原生静态复验另需已安装 **KiCad 9.0.2 / Python pcbnew**。`DEPENDENCY_LINKS.json` 精确复用已有并集493项（16,599,267字节）：r10/r11五个完整旧包、当前/历史线束锁定文件和旧映射JSON/manifest。旧文件没有再次作为r12 payload拷贝。它们仅在临时复现布局按原相邻项目名物化。

```sh
# 保持 pen_publication 下各批相邻时自动解析
/usr/bin/python3 portable_check.py --native
# 或独立给出本地批次共同父目录
/usr/bin/python3 portable_check.py --native --publication-root /path/to/pen_publication
# 将并集真正装配到仓库后的布局
/usr/bin/python3 portable_check.py --native --repo-root /path/to/smart-pen-codex
```

无需原 workspace 绝对路径：旧日志的绝对路径是出处，不是用户安装路径。适配器只临时物化原相对布局；比较时归一化日志路径与`checked_utc`，两个源/库文件枚举列表按名字排序（原rglob顺序依赖文件系统），不改任何冻结源码。缺依赖时明确失败，不联网补齐。当前审核/逻辑合同可复验，不宣称全部历史builder从零可重建。

## 软件状态，禁止扩大结论

- BLE 默认OFF，板级provider返回空指针；默认/开启配置的 app_main 都是编译夹具。两套真实IDF配置构建/链接和独审是**原冻结证据**，本r12主机复验不重建SDK，更未烧录、启动radio、连接PC或测吞吐/电流。
- V1 的schema触发器导致 **1 ACK / 0 durable rows**、不同target导出身份碰撞、队列延迟抹掉回调时间三个失败保留；V2对应拒绝/身份域/回调时钟复验不删旧史。SQLite提交是条件于OS/文件系统/存储遵守同步的边界，不是假称真实断电恢复已测。
- Windows、真实USB本地确认、SC/MITM/持久bond互通、真实设备配对/广播、掉电耐久、手机互通均未验。无屏量产配对尚未闭合。`NO_SENSOR` 的 `UI_allowed=false` 与空coordinate始终保留；wire VALID不是笔尖坐标/画画/评分授权。
- 未接相机、未把continuous解码器接应用record链；不产生实机FPS/RAM余量、安全或整体产品通过的结论。

## 硬件状态，NOFAB

CAM_ON限制维护从44→9段，全部3过孔、0.15mm线宽与真实T分支保留；是**实际铜路线改变**而非等几何共线合并。五zone-layer填充序列对508e不变；全DRC仍28/41/0。CAM_ON短于0.1mm段28→0，但此前全批微线段669→641，不是整板全部平滑/资格通过。

J107进一步到 **17违规 / 38未连 / parity0，DRC exit5**，完整finding multiset恰删11、新增0；J103真短路等仍在。GPIO18/21分别连接EN1/EN2，J107.3接已有0.50mm地桥；GND pad分量12→11不是全板接地完成。删除旧地尾的反事实不靠新增桥救回旧回流。新的信号via **确实改变平面避空**，不能继承CAM_ON阶段的“平面不变”。局部通道内缩不退化不等于全局最小颈、载流、EMI、回流电感或动态PI资格；两个纯In2 AON→IMU路径原本不通，不能将前后均不通当通过。

当前RevB电源板 `94ced2bd…dcdbc` 的 J5三针 EN1/EN2/GND 与本次J107 **1:1正确**，旧四针J5的pin3是CE_PERMISSION_EXTERNAL，必须按板版本拒绝。该合同只验证逻辑/原生pad身份，不是实际线束、线径、防错、插装、受力、启动/棕断默认或掉电域回灌资格。

**JP301 OPEN/DNP、既有充电commissioning开路、未知相机不接**；TPS22918不是过流/充电保护。保留所有动态供电/CT/QOD/负载/机械/制造/材料门。此包不改r11有限平头探针碰板负例，不给新壳或台架夹持力学放行。
