# 追加勘误：旧冻结benchmark的64-bit printf配置不兼容

**2026-10-29追加；优先于旧独审中“未发现阻断”的历史判断。旧benchmark只能作为历史源码/构建/主机回归证据，不可作为可运行的实板基准推荐入口。** 原31项冻结源、原15项独审证据与两个manifest不改写、不隐藏；本勘误是单独的新证据。

## 独立核对事实

- 冻结`smart_pen_decoder_target_benchmark_20261028/sdkconfig.defaults:8`设置`CONFIG_NEWLIB_NANO_FORMAT=y`。
- 原构建配置`build-enabled.config:1106`同样启用nano；第483行声明S3 ROM nano格式能力。该配置仅摘录必要事实并记录SHA，不把完整build配置或BIN/ELF收进包。
- 冻结`main/bench_main.c:41–45`以`int64_t`保存`esp_timer_get_time()`差值，再用`PRId64`输出JSON字段`decode_us`。
- 已核对ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`的`components/newlib/Kconfig:51–75`：nano格式不支持64-bit整数格式，需要该功能时应关闭此选项；在线v5.4官方说明一致。[官方配置说明](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/kconfig.html#config-newlib-nano-format)

据以上配置与源码可判定：旧包依赖了该nano实现不支持的64-bit输出格式。**已完成的编译/链接、主机mock/parser测试不能覆盖或证明目标libc的真实串口JSON格式正确。** 本次未上板，不能捏造目标上实际输出字符串、宣称已观察到具体运行故障或实测时延。

## 影响与后续边界

- r5的44张固定PGM回放、10条主机功能记录与11/22项parser测试仍是相应主机范围内证据，不因此变成目标运行证据；它们不检验S3 ROM printf。
- 不修改冻结旧包来假装过去已通过，也不发布旧BIN。重建、修正SDK配置和重新独审必须进入**另一个明确命名的新批次**。
- 新连续ROI对照基准拟关闭nano、增加编译期防护及64-bit格式探针，并重新核对最终链接输出；这些新工作不包含在r5，尚不能在此称完成或可实板运行。
- 即使后续printf修复并构建通过，仍不等于实板执行、真实FPS、相机准确率、安全或允许中断设备；设备授权/备份/恢复前置条件不变。

精确源路径、行号、SHA与复核关系见`known_issue_nano_printf_evidence.json`。旧独审历史结论应始终与本勘误一起阅读。
