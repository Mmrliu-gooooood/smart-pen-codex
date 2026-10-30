# Continuous V2 独立 RAM 基准复审

2026-10-29 00:25 UTC。候选：`smart_pen_continuous_target_benchmark_20261029`。本审查只操作本地文件/编译/测试；未连接、读取、复位、RAM加载、刷写或发布任何设备/仓库。

## 决定与冻结对象

**可归档为待实板识别、私有备份、恢复条件与用户中断授权后的执行候选；不能称为实机性能或设备安全通过。** 本次已审软件/静态链接范围未留未修复阻断。所有结果无设备身份认证，parser维持`identity_verified=false, overall_pass=null`，功能一致时CLI仍exit2。

- 47文件冻结清单SHA256：`af121d057a80ac01be6d19217abea3988b3e96fe6769651ebe7c18c4f45ed2db`。测试前后逐项核对未变；副本`reviewed_source_SHA256SUMS`。
- 启用BIN：290480字节，SHA256 `9845055ad9f77341dd2bb34949710f6302d8ccc8852123489c18cbe3353d9560`。
- SDK：ESP-IDF v5.4 `67c1de1eebe095d554d281952fde63c16ee2dca0`。
- 旧7夹具候选保持不改，其nano格式缺陷仍由`smart_pen_decoder_benchmark_erratum_20261029/ERRATUM.md`单独覆盖。新候选通过不能追溯抹去旧缺陷。

## 目标 libc：不再用 host mock 代替目标链接证据

独立查看最终effective config、ELF/map，而非仅defaults：

1. `CONFIG_NEWLIB_NANO_FORMAT`确实关闭；源码在误启用时#error。独立负例将nano设为1后编译明确失败。
2. 实际map有full `libc.a(libc_a-vfprintf.o)`，无`libc_nano.a`。`_vfprintf_r`、`_dtoa_r`、`snprintf`位于IRAM。
3. main在分配/跑样本前用目标`snprintf`生成`4294967297|1.25`并检查返回长度15及内容；失败只报fatal、不运行样本。独立mock故意使snprintf失败，验证0次malloc/0次timer/0次decode。
4. mandatory format_probe还含超32位整数4294967297及17位double；parser校验数值和类型，缺失/错误拒绝。

这些是配置、链接、源路径与主机故障注入证据。**目标自检尚未实际运行**，不能称目标libc已实测；但旧版已知的nano配置/链接冲突在新版本静态闭环。

## RAM、默认关闭与副作用边界

- 独立ninja复核disabled/enabled均成功；默认有效配置BENCH_RUN关闭，RAM/PURE_RAM启用。两构建均无设备动作。
- 实际BIN image_info仅4装载段：DRAM、DRAM、IRAM、RTC；没有IROM/DROM。ELF里的`.dummy`零装载/内部别名占位不当作外部Flash运行证据。
- 已链接符号中未见审查列明的相机/无线/GPIO配置/LED/Flash写擦/NVS/OTA/eFuse写API。应用源只内置图、heap、解码、时钟、stdio和调度。SDK ROM绝对地址别名并不等于应用调用，静态检查也不是形式化无副作用证明。
- 默认disabled仍启动SDK、延时并控制台输出；UART0及secondary USB Serial/JTAG会动作。PURE_RAM不等于零影响，复位/下载会中断现程序并改变易失状态。README明确外设断开、私有整片备份、禁止无条件Flash建议/force/eFuse修改。
- 工作区31104B和Gray8 40000B在heap，两个decoder串行复用core；任务栈16KiB另算。其他RTOS/代码/夹具/printf内存未实测，71,104B申请成功不能由链接成功推断。分配失败fatal，不计成功。PSRAM明确未测试。

## 冻结对照、分母、计时范围

同一6张完整200×200合成图，各依次调用冻结原core和continuous V2，无prior、无oracle入参。

- 原core：6张均预期-2。
- V2：5/6/7mm phase0三张预期成功；45°旋转预期-3；深边墨迹case063与超目标范围9mm压力图预期-2。
- 默认3轮共36次调用：9次V2正确输出，27次预期拒绝。这是固定回归集合，不是一般准确率，不能将NOFIT算成功吞吐。
- V2 full200输入仍在内部选中心96/80px及有界边缘处理，不等于拟合/验证全图；选中ROI外证据不检查。未验证真实纸张、相机、姿态、笔尖、通用透视/噪声可靠性。
- timer严格包围完整函数：V2裁剪选择、复制、边缘处理、解码与变换计算都在内；RLE解压、malloc、串口、调度与摄像头采集不在内。仅cold，不刷CPU cache，不虚构warm速度。
- header的timing_scope/cold_means/hardware_providers曾未严格核对；已要求作者修复，最终parser拒绝篡改范围，不能把core-only时间冒充含预处理。

## 独立 oracle 核查

不只与拟合矩阵自比：本目录`generator_oracles.json`冻结来自上游连续纸生成器的像素hash、origin、方向网格（源文件SHA256 `fe31d8a99bcf8c3419db83774fc5247982886480834f0e89d18820eb34152a2c`）。

`check_independent_geometry.py`实际编译运行新C，对3成功图各36个点：

- 像素hash匹配；36方向直接与生成器网格逐项核对。
- 独立计算像素中心`pitch*(cell-origin)-0.5`，不将真实位置/变换输入C。
- 验证返回paper_to_frame与上述中心误差、frame_to_paper逆变换。
- 共108点通过；每图最大逐轴误差约0.099/0.043/0.278px，阈值分别1.2/1.0/0.857px。这只是理想合成前视几何检查，**不是物理笔尖精度**。

临时独立目录重建packed RLE与source绑定，头文件和build-inputs逐字节相同。源码静态校验已改成包内LEGACY_SOURCE_SNAPSHOT，避免依赖作者workspace中特定同级旧目录。

## 测试与负例

- 作者host功能：6图×2实现=12项正确状态/oracle/failure-output检查通过，未用主机用时冒充S3结果。
- 作者parser13项通过；独立34项边界/负例通过，包括错误oracle、transform、NaN/Inf、bool/小数时间、额外/缺失/重复/重排、缺memory/complete、源/夹具绑定、格式探针及错误计时范围。
- 实际bench_main在独立窄mock下：enabled、disabled、allocation failure、format selftest failure、ASAN/UBSAN均通过；另nano启用编译拒绝通过。全部人工时钟每次增加123，36次调用应有72次timer读取，全部elapsed=123只验证计时边界/次数。**不能把这些值当实机时间**，未保存成可冒充目标测量的串口日志。
- 成功路径与完整schema2解析接合，仍overall_pass为空/CLI exit2；有限几何和完整日志不认证真实设备或日志防篡改。
- sanitizer为host ASAN+UBSAN，LeakSanitizer关闭；不是目标硬件内存测试。

## 仍需实物数据

芯片/板型/接口与已有程序识别、备份恢复可行性、允许中断、供电/接线、RAM实际余量、目标格式自检实际输出、完整启动至complete日志、冷解码时长、温升/功耗均未知。不执行设备前不再给无条件加载/刷写指令。README中文流程覆盖整片实际容量、两次私有读取hash一致性、加密/安全启动限制、不上传密钥/凭据/原固件及不force。

## 重现

```sh
export PEN_BENCH_SOURCE=/absolute/path/to/candidate
python run_actual_main.py
python run_parser_negatives.py
python check_independent_geometry.py
python "$PEN_BENCH_SOURCE/tools/check_host.py"
python "$PEN_BENCH_SOURCE/tools/test_serial_parser.py"
```

仅按本目录`REVIEW_ARTIFACT_MANIFEST.json`收录报告、脚本、generator oracle及静态/测试日志；不收录run_output里的主机可执行文件。所有证据分类保留，未发布/未刷机。
