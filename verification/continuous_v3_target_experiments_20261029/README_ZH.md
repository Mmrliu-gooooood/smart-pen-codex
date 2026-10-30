# r9：V3 最小目标基准与独审（本地归档，非实机）

**NOFAB / NONPRODUCTION / SYNTHETIC ONLY。** 原75项交付 allowlist + 清单、独审18项 + 清单共95原文件逐字节保留。56源码冻结 SHA256 `2ac17a4f1262a659b3696d36491ca23db89818f593d062d2c3b307360996f61b`；独审清单 `11d51bac3155749ef58262d83413a9f7e94366a1c3b037837658adac81d1602d`。不复制 build/BIN/ELF/.so/SDK、run_output、旧历史树或私密资料；不替换应用 firmware，不接 record/VALID 链。r4–r8原封不动。

## 离线重放与准确依赖

在本目录运行（已安装 Python 3、C11 `cc`、系统 libm；完整脚本还需编译器 ASAN/UBSAN runtime）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 portable_check.py
# 额外重建一次性来源提取；须已有归档r8，不联网获取：
PYTHONDONTWRITEBYTECODE=1 python3 portable_check.py --source-dependencies
# 若目录布局不同，参数指向r8的continuous_v3_experiments_20261029根：
python3 portable_check.py --source-dependencies --dependency-root /your/local/path/continuous_v3_experiments_20261029
```

默认 quick 自包含：95原件hash、9幅PGM/像素palette-RLE无损重建、post-return V3/旧core oracle、头文件和 source binding重建，18功能、16作者parser、41独审parser、180独立生成器几何点、真实 main 七种host运行配置和nano误开编译拒绝。启用/禁用/分配失败/格式失败/trace丢失/trace零统计/ASAN+UBSAN都在一次性临时副本执行。时钟固定+123只验调用边界；未发布可混淆的模拟串口测量。LeakSanitizer关闭，未计入通过。

`DEPENDENCY_LINKS.json`精确复用已归档r8的23项来源/清单；不会整个复制候选。其中仅2份生成器manifest需物化在临时历史相对路径，重跑 `prepare_independent_geometry.py`。其余核对19个core/codec/PGM/fixture来源及2个冻结清单。75项自包含基准内必须保留其绑定core/codec/PGM，即使这些字节在r8也存在；这里避免的是再复制整份历史候选，并非宣称全部来源字节零重复。默认quick不需要r8，来源提取扩展需要r8；脚本可识别已组装repo的相邻实验目录和本地r8增量包布局。

本次 `portable_check_result.json`确实运行上述全部，包括23依赖检查；未重新执行ESP-IDF目标构建。`SOURCE_SUBSET_SHA256.json`仅覆盖原件；新增适配器/报告的出处与hash见r9总manifest。

## 目标构建依赖（本轮未重建）

在**另一可写临时副本**中，使用已自行取得并核验的ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`、Xtensa GCC14.2.0（esp-14.2.0_20241119）、esptool4.12.0及该SDK需要的CMake/Ninja/Python环境；本包不捆绑/安装SDK或工具链。源码和构建脚本使用相对路径，不要求原workspace路径。所有归档文件为100644，shell脚本请显式用`bash`：

```sh
# 仅在可写临时副本的benchmark根；IDF环境应已配置
bash tools/build_only.sh disabled
bash tools/build_only.sh enabled
bash tools/collect_build_evidence.sh
```

只允许build profile，不接受任意idf.py动作；不要照抄构建工具打印的flash建议。采证会重写临时副本verification输出，故不能在冻结归档目录运行。`check_static.py`需要新生成的config/map/nm/compile_commands/反汇编，不是仅凭本包文本就可全重跑的静态检查；原精简证据保留既往结果。

## 目标证据与不可越过的边界

- 历史目标构建/独审保留 full libc、nano关闭、PURE_RAM与默认BENCH_RUN关闭；Xtensa实际机器调用证据为 continuous → `__wrap_pen_roi_decode_refined_transform` → real。新的host mock不能替代这些目标静态证据，目标格式自检仍未设备执行。
- 9幅完整200×200理想合成图，两decoder共18功能对照。V3成功5/拒绝4，旧core9均拒绝；默认三轮54调用不是通用准确率/FPS分母。原图不裁掉失败点，真值仅返回后的oracle，不输入搜索。
- 真64上限的第65seed溢出：`[864,65,0,0]`、status=-4、result保持；20无完整窗口仍必须拒绝。两类预处理拒绝trace_calls=0/统计全0，不伪称跑过搜索。
- V3插桩计时含diagnostics复制等开销，旧core未插桩；不能把绝对时差全归算法，更不是未插桩生产速度。
- 32,640B单工作区 + 40,000B输入 = **72,640B** heap申请；顺序复用旧core，不是两工作区。9组packed数据105,864B + palette125B在内部DRAM，另有代码/full libc/RTOS/16KiB任务栈。`.dummy`/别名不可简单相加当物理峰值。275,344B历史镜像hash只是构建证据，不含镜像文件；link fit不证明分配/栈余量成功。
- 目标分配、格式或trace异常fatal，无complete；parser拒绝部分日志。即使功能日志一致仍 `identity_verified=false`、`overall_pass=null`、CLI exit2。未设备识别、运行、FPS、实测RAM、相机/纸面/笔尖/倾斜或安全验收。
- 默认关闭仍有SDK及UART0/USB控制台活动；RAM加载/复位也会中断旧固件。后续设备操作须另行明确授权并具备板型识别、实际容量私密备份和恢复条件；没有设备执行脚本。

## 历史缺陷不被新通过覆盖

旧7夹具基准nano开启而用PRId64，属于目标日志收集阻断，不能再当可运行推荐入口。参见独立[旧nano勘误](../decoder_experiments_20261028/smart_pen_decoder_benchmark_erratum_20261029/ERRATUM.md)（r6已归档），以及r5 `KNOWN_ISSUES_ZH.md`。本后继关闭nano的构建/静态检查不追改旧报告，也不等于full libc已在设备运行。
