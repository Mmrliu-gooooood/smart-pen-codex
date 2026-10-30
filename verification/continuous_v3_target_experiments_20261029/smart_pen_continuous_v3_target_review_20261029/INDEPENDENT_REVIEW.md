# V3 最小目标基准独立复审

2026-10-29 01:35 UTC。对象：`smart_pen_continuous_v3_target_benchmark_20261029`。只做本地读源、编译、反汇编和主机测试；未连接、读取、复位、加载、刷写设备或发布外部仓库。

## 审核决定

**可按75项allowlist归档为待设备识别/私密备份/恢复条件与中断授权后的实验候选。已审范围未发现未闭环阻断。** 这不是S3实测、RAM容量余量证明、实时性能、真实相机或消费级安全验收。旧7夹具nano缺陷勘误与V2历史报告保持原样，本次通过不回改历史结论。

- 最终56文件清单SHA256：`2ac17a4f1262a659b3696d36491ca23db89818f593d062d2c3b307360996f61b`；测试前后逐项未变。
- 核心绑定V3 snapshot：`1636084759c3ebfc358574f669ea5292b11ae4421145401e7c2ccaed12664ccf`。SOURCE_BINDINGS各核心/codec/9PGM哈希独立核对。
- 启用BIN：275344字节，SHA256 `e8dd4f36bf318d9cbd13df2d690b025b31b0a39a76d7a3651b1f91696e05a86c`。
- 固定ESP-IDF v5.4 `67c1de1eebe095d554d281952fde63c16ee2dca0`。两目标ninja独立复核成功。

## 新增关键边界：实际目标插桩

独立对最终Xtensa ELF反汇编，不沿用host推断：`pen_roi_decode_continuous`实际call至`__wrap_pen_roi_decode_refined_transform`，shim实际call至真实`pen_roi_decode_refined_transform`。摘录保存在`target_call_excerpt.txt`。

shim仅维护自己的计数/诊断缓存，在真实函数返回后复制diagnostics；不改变灰度输入、核心阈值、output或核心源码。调用计数与fixture期望不符，或应搜索但coarse为0时，main发fatal并释放heap，不输出complete。

独立真实main主机测试故意替换**测试副本**中的trace调用计数为0、或丢弃diagnostic复制：两种均在首个V3调用后fatal，只有前一个legacy样本，不能混成完整通过。此故障注入未改候选源。正常失败场景仍验证整个result保持poison原字节；不从失败result读取种子统计。

header明确`instrumented=true`及continuous_v3_only_link_wrap；逐记录V3为true、旧core为false。timer包围完整wrapper，含裁剪/边缘处理/coarse/refit/变换及shim内部计数、诊断复制开销；trace_reset、返回后get/calls检查、RLE解压、malloc、串口与调度在外。插桩不同，不能把旧core/V3绝对时间差全归算法，更不能称未插桩生产性能。

## 功能、overflow与完整日志

9幅完整200×200固定图：5/6/7mm、45°恢复、5.1mm恢复、无完整窗口、深墨迹、密度、真实65seed溢出。9图×2实现的18个host功能结果通过；默认3轮主程序共54次调用：15次V3预期成功、39次预期拒绝（含旧core），不是一般准确率或FPS分母。

真实溢出夹具返回diagnostics `[864,65,0,0]`，status=-4，result保持不变；生产上限仍64，未改变宏制造溢出。64×24B seed ABI独立用Xtensa编译器static_assert通过。预处理拒绝不调用refiner的夹具应trace_calls=0/stat全0，不能伪称执行了搜索。

schema3检查：准确样本顺序/集合/轮次、绑定hash、timing范围、instrumentation、status、方向、crop、双向矩阵、成功result统计与trace一致性、overflow/失败输出保留、完整memory与complete、mandatory格式探针。41项独立负例通过，包括NaN/Inf、bool/小数时间、缺失/重复/重排、错误几何、错误trace计数、66seed与溢出后仍fit、伪造instrumentation范围。作者16项parser测试也独立重跑通过。

无可信实物身份时始终`identity_verified=false, overall_pass=null`，功能一致CLI仍exit2；功能错误exit1，缺失/异常日志拒绝。header hash不是设备认证或防伪签名。

## 几何与压缩不是拟合答案自证

从此次独立重跑的实际C输出检查5张成功图、180个生成器网格中心和方向；不是仅将返回矩阵与自身相等比较。生成器origin/pitch或独立renderer的旋转/尺度坐标供返回后oracle使用，不注入C搜索。方向、中心误差界、逆变换全部通过，结果在`geometry.log`。仅理想合成几何，不是物理笔尖精度、真实倾斜或通用投影验收。

将**仅75项allowlist**复制到独立临时目录，重新运行packed palette生成、host功能与parser测试全部通过；重建头文件/source绑定逐字节相同。palette最多32个精确灰度值，uint16编码count/color，PGM SHA与40000字节往返相同，无有损量化或删点。未复制旧build、旧历史或目标二进制。一次性原始来源提取工具有来源依赖，但普通回放/构建使用包内冻结输入。

## libc、RAM、默认关闭

- 独立检查effective config关闭nano，map为full `libc.a(libc_a-vfprintf.o)`且无`libc_nano.a`，`_vfprintf_r`/`_dtoa_r`/`snprintf`在IRAM。源码误启nano即编译拒绝；独立负编译通过。
- main先用snprintf检查超32位整数+double，失败在malloc前fatal；独立故障注入验证0分配/0解码。随后格式probe由parser复核。目标libc自检尚未实际执行，host mock仍不能替代目标运行。
- 实际BIN只有DRAM/IRAM/RTC装载段，无IROM/DROM；默认BENCH_RUN关闭，两SDK构建复查成功。已审源码/链接API无相机、LED、电池、无线、NVS、Flash写擦、OTA、eFuse写调用。ROM绝对地址别名不等于实际调用；静态证据不是形式化无副作用证明。
- Xtensa ABI：21888B core+1536B seeds+9216B crop=32640B单工作区；原图40000B，总运行heap申请72640B。两个decoder串行复用core，不另分配第二工作区。
- 约106KB只读palette夹具在纯RAM内部DRAM，还需代码/full printf/RTOS/16KiB任务栈与动态开销；alias/dummy不能简单累加当峰值。没有实测heap free/largest/stack低水位，link fit不证明72640B申请成功。分配失败fatal，无complete；PSRAM未测。
- 默认关闭仍会启动SDK/延时/控制台输出。UART0和secondary USB控制台并非静止；RAM加载/复位会中断旧固件、改变易失状态，不是零影响。中文说明保留先识别、整片实际容量私有双备份、恢复条件、允许中断、外设断开、不force/eFuse、不上传凭据/原固件的门槛。

## 独立执行记录

`run_actual_main.py`运行真实main+core+shim，RTOS/heap/clock为明确mock：正常启用、禁用、分配失败、格式失败、trace丢失、trace零统计、ASAN/UBSAN七种执行配置通过；另nano错误配置编译拒绝。人工时钟每次+123，54次调用有108次timer读取，仅检验调用边界/次数，不是时间结果。LeakSanitizer关闭，不将其计入通过。

`run_parser_negatives.py`41项；`check_geometry.py`180点；`host_functional.json`18项；`abi.log`目标编译ABI；`static_checks.json`/`target_call_excerpt.txt`/`image_info_enabled.txt`/`sdk_recheck.log`为静态证据。源未变见`minimal_package_check.json`。

复现先设置`PEN_BENCH_SOURCE`，运行三个独立脚本；geometry读取本审查重新生成的host_functional.json。按`REVIEW_ARTIFACT_MANIFEST.json`只归档精简证据，不包含run_output的主机可执行文件、ABI对象和完整反汇编。
