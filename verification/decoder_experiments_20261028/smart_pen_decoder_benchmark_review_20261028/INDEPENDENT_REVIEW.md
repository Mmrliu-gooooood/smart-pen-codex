# RAM-only 解码基准独立审查

时间：2026-10-29 00:04 UTC。对象：`smart_pen_decoder_target_benchmark_20261028`，仅本地代码/构建/模拟测试；未连接、识别、读取、复位或刷写任何设备。既有应用83项审查保持不变。

## 决定

**可以归档为待实板执行授权的独立基准候选。不是实机性能报告，也不证明RAM执行零影响或消费级产品安全。** 当前未发现下述范围内未修复阻断；实物识别、原固件私有备份/恢复条件、允许中断及安全接线仍是执行前置条件。

冻结31文件清单 `verification/FROZEN_SOURCE_SHA256SUMS` 的SHA256：
`dc8303fef58385b15ca652618bd52082f3078dc887c52fee1397f1dd4f3a4c62`。
独立副本为 `reviewed_source_SHA256SUMS`，逐项复核通过。

启用BIN：216096字节，SHA256：
`8c56bdbe92b3f55906b2de6f9d6d735ef5b6781b974a2f2d208de1e13775a617`。
SDK固定ESP-IDF v5.4 `67c1de1eebe095d554d281952fde63c16ee2dca0`。

## 默认安全与实际镜像

- disabled配置确实未启用BENCH_RUN；PURE_RAM_APP和RAM构建均启用，CPU配置240MHz，主任务栈16384字节。默认和enabled均未启用PSRAM/无线。
- 直接对最终BIN执行本地image_info：4个实际装载段在DRAM、DRAM、IRAM、RTC，不含IROM/DROM。ELF另有零FileSiz的`.ext_ram.dummy`占位，不是可加载外部RAM数据；`.flash.text`/`.flash.rodata`名字本身也不代表地址仍在Flash，实际映射在内部RAM。
- 独立ninja复查disabled/enabled均成功，无待重编源。没有运行构建日志通用尾注的flash/write_flash建议。
- 应用源只有内置夹具、堆分配、解码、时钟、串口、调度及内存统计。未调用相机、电池、LED、压力、无线、NVS、Flash写/擦、OTA或eFuse写接口。最终符号中未见相关已链接应用API。
- SDK导出表仍含ROM绝对地址别名`dfu_flash_erase`/`ets_efuse_write_key`；不能因存在名字就误报执行，也不能写“所有危险字样彻底不存在”。独立反汇编未见对这两个符号的直接调用。这是静态证据，不是形式化副作用证明。
- 即使默认disabled，SDK启动、3000ms延时与控制台提示仍会执行；UART0 115200与secondary USB Serial/JTAG并非静止。RAM加载/进入下载模式会中断原程序、改变RAM/外设状态；README已明确外设物理断开、先识别/备份/确认，不声称零影响。

## 7夹具、分母与计时

- 7个固定PGM：3个完整200×200/5–7mm视场均预期拒绝；3个裁剪96/80/96像素预期正确坐标；1个空白预期拒绝。此为故意选定的回归集合，不是随机真实相机准确率分母。
- 独立在临时目录从PGM重建RLE头，与冻结`fixtures.h`逐字节一致；PGM SHA和RLE往返通过。host真实解码器功能测试得到7个cold+3个warm，共10条。
- 每图3轮时，真实`bench_main`路径应产生21个cold、9个warm，共30次调用，其中18次正确坐标（含9次warm）、12次预期NOFIT，另12个warm_skip。不能将预期拒绝称为成功解码吞吐，更不能将这些窗口坐标当笔尖/VALID笔迹。
- 解码参数只有像素、尺寸、纸边界/section、工作区、像素产生的prior；答案只在调用后比较，没有将oracle坐标注入搜索。
- `esp_timer_get_time()`前后仅包围解码调用；不含分配、RLE解压、串口、10ms调度、采图。cold只清几何prior，不刷CPU cache；warm仅同图像，不是移动相机序列，不保证全局唯一性。
- 主机mock时钟故意每读增加123，独立断言全部decode_us=123以验证边界/调用次数。这些是假时间，未存成可误认真实测量的串口记录。

## 工作区与内存证据

- 工作区21888字节，通过host sizeof及真实主程序runtime_config路径核对；图像缓冲固定40000字节，二者在heap，不在任务栈。主任务配置16KiB不是运行余量承诺。
- 目标编译器.su中app_main 272B、decode368B、candidate256B等是单函数静态帧，不可相加当完整运行栈峰值。运行high-water mark和heap最低值未实测。
- allocation failure明确skip且不调用解码、不泄漏成功分配；独立mock验证。PSRAM默认skip且没有可运行PSRAM profile，本次不验证PSRAM性能/引脚模式。

## 审查发现并闭环：机器证据可信度

旧parser曾实际接受wrong oracle、NaN latency、unknown extra且functional_failures=0，见 `parser_before_fix.json`。作者已修复：

1. 读取runtime_config重复次数1–10，不再硬编码3。
2. 限定manifest样本、placement、mode、序号及准确集合，mandatory internal完整轮次，PSRAM未运行须explicit skip。
3. 时间必须非负真正int，拒绝NaN/Infinity/bool/float；重复/遗漏/额外样本拒绝。
4. 独立按manifest重算status/坐标verdict，并检查used_warm、failure contract；warm必须在同fixture/repeat已成功cold之后。
5. header/runtime_config必须先于样本，complete在末尾；未知JSON type拒绝，不混入分母。
6. 没有可信实物/构建身份时固定identity_verified=false、overall_pass=null，CLI即使功能无错误仍exit2；仅函数统计可查看，不授予设备验收通过。日志不具备真实性/防篡改保证。

最终作者11项parser测试通过；独立22项额外边界/负例通过。真实bench_main独立主机编译执行enabled、disabled、双分配失败、ASAN+UBSAN四种配置通过；时钟/heap/RTOS都是窄mock，绝非设备模拟器或实板验证。ASAN关闭LeakSanitizer，不把泄漏工具检查计为通过。

## 中文操作说明复核

README要求先拍板型/模块/接口与现程序用途，核查实际容量/安全状态，私有目录两次整片备份及SHA一致性，不上传凭据/笔迹/密钥、不force绕保护、不改eFuse；备份也不自动等于可恢复。识别/读取可能复位或使用RAM stub，需允许中断。当前未给可直接执行的加载命令，下一步须针对实际板型再确认，符合本候选边界。

## 重现与证据

本目录脚本默认读取同级候选，可设置`PEN_BENCH_SOURCE`：

```sh
python run_parser_negatives.py
python run_actual_main.py
python "$PEN_BENCH_SOURCE/tools/check_host.py"
python "$PEN_BENCH_SOURCE/tools/test_serial_parser.py"
```

`actual_main_mock.log`、`parser_negatives.log`、`host_functional.json`、`author_parser_tests.log`是主机测试；`image_info_enabled.txt`、`target_program_headers.txt`、`target_symbols.txt`、`sdk_recheck.log`是静态/构建证据。均不能用作物理FPS、实机准确率、功耗或温度结论。
