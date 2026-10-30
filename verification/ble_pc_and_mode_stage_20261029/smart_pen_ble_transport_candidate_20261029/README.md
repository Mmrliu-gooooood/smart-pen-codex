# 点阵笔 BLE 真实传输 provider 候选（2026-10-29）

**默认 OFF；编译夹具，不是可直接烧录的完整点阵笔。** 本目录独立于冻结的
`smart_pen_app_pipeline_20261028`，不修改它的83项主机基线、不改摄像头/笔尖mapper、
不产生假 VALID、不改评分/AI/画画 UI、不接云/QUIC。本轮没有连接/刷写设备、
启动无线、生成真实密钥/账号、擦除 NVS 或推送 GitHub。

## 实际交付

- 官方 ESP-IDF v5.4 / ESP32-S3 NimBLE GATT 适配器：48B耐久坐标记录、3×20B通知、
  20B精确ACK、订阅/MTU/忙重试/断连/安全态/静默处理。
- 启动前耐久预留非零 boot epoch 段；连接内递增 epoch；NVS故障或耗尽关闭，不自动擦除。
- **新的、明确授权与持久化分离的 actor 桥**：host线程只验权/发送，Flash操作仍在独占app任务。
  并非把旧`pen_app_ack()`的当前态检查偷换成陈旧快照。详见 [集成合同](docs/INTEGRATION.zh-CN.md)。
- 开发 USB 可见显示策略：本地60秒一次配对窗口，随机passkey，SC/MITM、128bit键、
  已持久bond，随后本地确认当前epoch才允许坐标/ACK。无Just Works降级、无固定passkey。
  **未提供/验证真实USB交互UI；无屏量产配对方案仍未闭合。**
- `frozen/` 是构建所需最小冻结源码的逐字节副本，来源hash见`verification/frozen_dependencies.json`。
  `pen_get_board_provider()`仍返回NULL。默认/开启编译配置的`app_main()`都只输出警告后返回。

## 再现（仅主机测试与构建）

```sh
python tools/test_host.py
tools/test_review.sh
PEN_SDK_ROOT=/absolute/path/smart_pen_sdk_20261028 tools/build_idf.sh
```

使用已在本机安装的官方SDK/工具，不下载新依赖。外部构建树由`PEN_BLE_BUILD_ROOT`指定；
改变defaults需用新的build/config路径，已有sdkconfig优先。SDK输出中的刷机建议命令**不是本项目操作步骤**。

最终实测软件结果及源绑定见 [验证报告](verification/RESULTS.zh-CN.md)。
主机模拟、实际SDK编译链接与真实 BLE互通/吞吐/电流是三种不同证据；最后一种尚无。

## 下一道实机门

先审真实USB本地确认实现与SDK安全补丁、板型/供电/Flash分区，再用获准开发板进行限定BLE实验。
手机接收端须实现本协议并持久提交后才ACK。iPad/iOS需原生CoreBluetooth等受支持路径；
这里没有iOS Web Bluetooth方案，也没有开发原生App。Android同样尚未互通验收。
冻结的Windows `windows_ble.py`只允许`SYNTHETIC`测试设备，不能伪造该INFO标记冒充真实接收器。
完整清单见 [实机验证门](docs/DEVICE_GATES.zh-CN.md)。
