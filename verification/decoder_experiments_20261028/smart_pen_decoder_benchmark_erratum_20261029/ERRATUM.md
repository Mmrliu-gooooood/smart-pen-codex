# 独立审查勘误：旧 RAM 基准的 64 位格式输出不兼容

时间：2026-10-29 00:18 UTC。本文追加更正，不改写旧报告、旧源或旧证据。

## 修正结论

**旧`smart_pen_decoder_target_benchmark_20261028`不应直接作为可执行目标计时日志采集候选。存在尚未修复的目标 libc 格式兼容阻断：启用 nano printf，却用 PRId64 输出 int64_t 时间。** 必须在新候选修复有效配置、核对实际链接实现并重新验证，不能沿用旧 host mock/构建通过作为目标格式正确性的证据。

本勘误覆盖旧报告中“未发现范围内未修复阻断”的结论及对目标日志可用性的潜在推断。旧源仍可作为历史诊断归档；RAM镜像段、默认disabled、无设备执行、夹具功能和parser拒绝测试的事实不因此变为虚假，但不能弥补此缺口。没有任何实机日志/FPS可被据此认可。

## 独立核实

1. 旧有效`build-enabled.config`确实为`CONFIG_NEWLIB_NANO_FORMAT=y`，不是仅defaults文件中的建议。
2. `main/bench_main.c:45`以`%`加`PRId64`输出`int64_t elapsed`。
3. 固定ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`的`components/newlib/Kconfig:55–75`明确nano格式不支持64位整数，需64位格式时应禁用该选项。
4. `components/newlib/CMakeLists.txt:76–90`将此配置映射到`--specs=nano.specs`。旧目标link map实际纳入`libc_nano.a(libc_a-nano-vfprintf.o)`，`_vfprintf_r`/`_vfiprintf_r`在0x40389660，证明不是只看配置而未检查链接。
5. ESP32-S3 ROM caps也声明具有nano格式；本PURE_RAM镜像中的具体实现来自所见libc_nano链接对象。不能把“函数位于IRAM”误认为完整64位格式实现。

影响：目标串口时间字段及其后格式输出可能无法按预期形成正确JSON/数值。未执行目标程序，因此不臆测具体错误字符串、崩溃方式或数值偏差；仅静态不兼容本身已足以阻断目标测量证据使用。

## 为什么旧测试未发现

主机mock编译链接宿主libc，支持该64位格式；ASAN/UBSAN同样使用主机库。它们证明的是夹具/解码调用/计时边界与主机输出，不是Xtensa目标newlib格式能力。目标编译链接成功只说明符号和内存布局可完成，不能保证选定printf子集支持所有格式。旧审查遗漏了“有效配置→实际链接libc→格式能力”的检查，应明确承认而不是追改历史测试记录。

## 冻结关联及下一步

- 旧报告SHA256：`6cbb644c41b36256ede67484b177bfa59dc61ef1ad6d2ebda054150172f07582`。
- 旧审查清单SHA256：`f5019bd1bf7e2fb2622581971b858b31f19492996c9165a77582ca44de8c1bfe`。
- 旧候选源清单SHA256：`dc8303fef58385b15ca652618bd52082f3078dc887c52fee1397f1dd4f3a4c62`。
- 旧启用BIN SHA256：`8c56bdbe92b3f55906b2de6f9d6d735ef5b6781b974a2f2d208de1e13775a617`。
- 证据原文件哈希与带行号摘录随附。未修改任何上述冻结对象。

新的独立continuous benchmark应关闭NANO_FORMAT，拒绝不兼容有效配置，核对link map完整格式实现，加入超32位数值的目标格式自检并以自检失败阻断后续日志认可。仍需保持无设备身份时overall_pass为空，真实设备执行另行授权。当前未连接或刷写设备。
