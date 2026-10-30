# 点阵笔 PC BLE 接收/耐久重放适配候选

**仅本地软件候选，默认没有无线动作；不是已验证可连接的完整产品。**
本轮没有扫描、连接、配对、刷机、访问用户蓝牙身份、上传或生成长期凭据。没有实现 iPad/Android 原生接收器，没有 iOS Web Bluetooth 声称。

## 已交付

- 冻结真实 GATT UUID、48B SP v1、3×20B 分片、20B 精确 ACK 的 Python 接收入口。
- `BleakClient` 实际 API 路径：明确目标、OS 配对、本地批准提示、INFO、订阅、`response=True` ACK；mock 运行**同一份**接收逻辑。
- 本机 SQLite `DELETE + synchronous=EXTRA`（比 FULL 多一道 rollback journal 删除后的目录同步）；成功提交原始48B后才 ACK。
- 持久去重、冲突停止、断连/取消/队列溢出隔离，显式 session 的 NDJSON 诊断重放。
- 旧网页/评分/AI不重写也不启动。当前冻结 INFO 为 `NO_SENSOR`，所有导出均 `UI_allowed=false`，没有正式笔尖 POINT。

## 安全的离线再现（Python 3.10+；本次实测3.12/Linux）

```sh
cd smart_pen_pc_receiver_candidate_20261029
python -m pen_receiver                         # 仅帮助，不导入 Bleak、不接触 radio
python -m unittest discover -s tests -v         # 标准库+mock，无设备
python -m compileall -q pen_receiver tests tools
python tools/crosswire.py                      # 需要cc与同级冻结BLE候选；只读它，输出在tmp
```

无需安装包即可运行离线测试。实际连接唯一第三方直接依赖为已存在的 `bleak==3.0.2`，MIT；测试没有下载软件。
当前环境可用 `../smart_pen_host_venv_20261028/bin/python`。不要把 Linux 测试结果称为 Windows 实测。

`python -m pen_receiver init-state --state-dir /本机私有目录/pen-one` 只创建最后一级目录，不创建任意父目录、不改现有权限。
`replay` 不接触蓝牙，但 SQLite 可能执行正常 hot-journal 恢复且需要独占锁；不是取证只读工具：

```sh
python -m pen_receiver replay --state-dir /本机私有目录/pen-one --session 42 > diagnostics.ndjson
```

本轮未创建真实用户journal。测试用临时合成records，均不是实际书写/光学证据。

## 将来明确批准的连接入口（本轮没有执行）

先完成冻结固件 `DEVICE_GATES`：真实USB可见随机passkey、SC+MITM+128bit key+耐久bond、当前连接epoch的笔端本地批准、板型/分区/SDK安全版本核验。冻结固件 `app_main` 仍不启动radio且provider为NULL，不能直接拿本接收器宣称整笔点亮。

Windows 命令示例（**占位目标不能照抄执行**；需要官方 Bleak 依赖和OS蓝牙权限）：

```powershell
python -m pen_receiver connect --state-dir "C:\Users\YOU\PrivatePen\pen-one" --target "AA:BB:CC:DD:EE:FF" --peer-scope "my-pen-one" --device 42 --enable-radio --authorize-os-pairing --create-journal --windows-private-dir-confirmed
```

- `--target` 是用户在本机明确选定的地址/平台UUID，不是广播名。`--device` 来自对该笔本地核验的固件ID；`peer-scope` 是本机稳定标签，不是身份认证。
- 首次需要 `--create-journal`；已有库不覆盖。重连再次显式运行同目标、scope、device，不能复用旧partial/ACK队列。
- `BleakClient(字符串目标)`可能**隐式扫描**；只可能发生在此显式 `connect` 授权之内，不声称“connect不扫描”。没有自动发现或自动重连命令。
- Windows 的确认开关只是用户对目录DACL的声明，**代码没有独立验证Windows ACL**。请预先通过Windows安全设置把目录限制到本人，不用网络盘/同步盘。Windows `msvcrt` 锁与键盘分支未在Windows实测，故不是Windows开箱即用承诺。
- 配对输入随机passkey只在OS对话框；本CLI不收集/记录passkey。笔端本地核实并批准**当前epoch**后，在CLI输入 `READY`。CLI输入只证明操作者声明，不授予固件权限。
- 初始受保护INFO读取可能触发macOS系统配对；只有特定认证/授权拒绝可进入本地确认，确认后重新读取INFO。未知/合成/新版本INFO均拒绝，无降级。
- `Ctrl+C`、取消、断连、写失败均结束本次连接；不删除bond、不擦库、不自动重新连接。确认超时可取消，不遗留阻塞stdin worker。

详见 [设计/故障边界](docs/DESIGN.zh-CN.md)、[坐标接入合同](docs/COORDINATE_SOURCE.zh-CN.md)、[平台/依赖证据](docs/SOURCES_AND_PLATFORMS.zh-CN.md)、[验证范围](verification/RESULTS.zh-CN.md)。
