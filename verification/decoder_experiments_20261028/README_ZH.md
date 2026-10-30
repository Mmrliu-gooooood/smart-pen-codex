# r5：视场审计、冻结解码基准与独立审查

**NOFAB / NONPRODUCTION / SYNTHETIC ONLY。仅本地归档与主机回放；没有推送、连接设备、复位、读写Flash或运行板端程序。** 构建成功、主机功能通过和有限合成图上的正确坐标均不代表实机FPS、真实相机准确率、笔尖VALID、安全、量产或整笔可行性。

> **已知阻断勘误：旧benchmark启用nano printf却使用64-bit PRId64，不能作为可运行推荐入口。必须先读[KNOWN_ISSUES_ZH.md](KNOWN_ISSUES_ZH.md)。旧独审“未发现阻断”的历史判断不覆盖本次新发现。**

## 内容与不可混淆的来源

- `smart_pen_viewport_audit_20261028/`：原始审计脚本、报告、432帧基线/432帧诊断数据、44张固定PGM、像素/坐标oracle、上游合成方向矩阵与原SHA清单。所有原文件逐字节保留；只排除已编译`audit.so`。
- `smart_pen_decoder_target_benchmark_20261028/`：按冻结清单完整保存31项源码/夹具/许可证/中文说明，另保存13项构建与测试证据、`.gitignore`。未收录build目录、BIN/ELF/map、SDK、工具链或设备备份。
- `smart_pen_decoder_benchmark_review_20261028/`：原manifest及其15项独立审查证据；不含`run_output`的二进制/反汇编。`parser_before_fix.json`是历史失败证据，不是当前验收结果。
- `KNOWN_ISSUES_ZH.md`与`known_issue_nano_printf_evidence.json`：本轮新增、只读源配置核对的nano/64-bit输出勘误；不修改或隐藏旧审查。
- `portable_replay.py`、`portable_replay_result.json`、`portable_benchmark_host.json`、`portable_author_parser_tests.log`、`portable_independent_parser_negatives.json`与本说明是**本轮新适配器/新复核证据**，不是原冻结审计的一部分，单列SHA与来源。

冻结31文件清单SHA256：`dc8303fef58385b15ca652618bd52082f3078dc887c52fee1397f1dd4f3a4c62`。

独审15项manifest SHA256：`f5019bd1bf7e2fb2622581971b858b31f19492996c9165a77582ca44de8c1bfe`。

逐字节复制意味着旧日志中的历史工作区绝对路径、原先环境名和SDK自动打印的flash建议原样保留：**它们是出处记录，不是用户环境路径或执行指令。不要运行这些flash/write_flash尾注。** 上游许可保留于benchmark的`codec/LICENSE.microdots`；这不扩展为对所有新增项目文件重新授MIT许可，也不授予商标/专利权。

## 可离线快速回放（不需要旧仓库、NumPy或SDK）

在本目录运行，前提只有受控环境中已安装Python **3.9+**、`cc`及标准C数学库：

```sh
python3 portable_replay.py > /tmp/smartpen-r5-portable-replay.json
```

适配器先核对冻结31文件、原regression manifest和NPY SHA；在系统临时目录编译包内已核对C源码，只向stdout输出新报告，不写原冻结证据。没有设备/网络调用，不报告主机延迟或FPS。44张PGM按像素SHA、原状态、成功坐标与独立上游方向/视口oracle检查；失败必须保持输出不变；prior固定NULL。

本轮在归档目录另复核：benchmark主机7 cold+3 warm共10条功能记录、作者11项parser测试、独审22项parser边界测试通过；设置`PYTHONDONTWRITEBYTECODE=1`防止往冻结目录添加缓存，没有改动原测试代码或原日志。这些均不验证设备身份、真实计时或实板安全。

原审计依赖的`vision/roi.h,roi_opt.h,roi_opt.c`及`codec/anoto.c,anoto.h,sequences.h,LICENSE.microdots`与包内benchmark同名文件完全一致，因此回放不需读取整笔项目的可变`firmware/vision`，也不混入后续`continuous_roi`候选。`upstream_directions.npy`已确认只是1000×710 uint8、0–3方向数据，无pickle/对象，绝不是可执行程序。

## 旧脚本完整重生成：额外依赖与移植边界

原`audit.py`与`replay_regression.py`保留原貌，默认在父目录查找`smart_pen_original_20261028`、`smart_pen_vision_opt_20261028`；**仅有本增量包时，不能原样运行它们完成全生成。** 使用portable回放即可复核固定44图，但这不等同重新执行整个432帧生成/诊断流水线。

完整生成须准备受控、已审查的源码副本（**本包没有偷偷复制整个旧仓库/厂商资料**）：

1. 上游原始源码pin：`0f8b569176c77dad34aaf83bb008eb118c9f1208`，原本地origin记录为`https://github.com/Mmrliu-gooooood/digital_pen.git`。使用用户已有可信仓库，或由用户自行获取该源后核对commit；若远端没有该commit，应停止并索取可核对源码，不改用HEAD。
2. 优化解码器源码pin：`685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`。原origin是本地开发副本，不声称新GitHub仓库已有这个历史commit。须从用户已有可信git副本获得该commit；本包冻结7文件只能保证回放所需C代码，不代替完整旧测试模块的出处。
3. 原审计的Python导入需要上游`点阵笔资料/py_microdots_develop/microdots/*.py`；`provenance.json`固定10个模块的SHA。生成器使用NumPy；这些调用不需要绘图，不需为本审计安装matplotlib。`digital_pen_ov5640/pc/configs/pattern.yaml`的SHA也须按provenance复核。
4. 优化源码所需C文件见上述7项；Python ctypes布局来自`tests/test_roi_vision.py`、`tests/test_roi_opt.py`，其导入还需要`tests/roi_fixture.py`、`tests/roi_opt_fixture.py`。独立运行那些旧单元测试还会需要相应tests/fixtures，不要把“可导入布局”误称整个旧测试套件已打包。
5. 原脚本通过`git rev-parse HEAD`记录来源，因此完整生成应使用真正的固定commit工作树，而非把随意复制的文件伪装成那个commit。可从已经含该commit的可信本地仓库创建detached worktree；本次没有下载依赖或建立工作树。

在一个**新建的、非公开输出的临时工作目录**构造下列布局，复制本包审计目录作为可写工作副本；绝不在冻结归档内运行会覆盖结果的脚本：

```text
<scratch>/
  smart_pen_original_20261028/      # 上述固定commit的可信工作树
  smart_pen_vision_opt_20261028/    # 上述固定commit的可信工作树
  smart_pen_viewport_audit_20261028/ # 本包审计目录的工作副本
```

核对git commit、来源/许可证、provenance中的generator/profile SHA和decoder 7文件SHA后，在已安装NumPy与cc的受控环境按顺序执行`audit.py → verify_rolling.py → boundary_diagnostic.py → finalize.py → prepare_regression.py → replay_regression.py`。`finalize.py`会向报告追加文本，不应反复在原报告上运行；工作副本须管理好原报告与重生成结果。旧主机耗时字段与运行时工具版本不同可能导致JSON字节不一致，不能把重生成时间字段混进原冻结清单。完整生成仍全是理想合成图，不产生物理可靠性结论。

## 基准与独审的重现边界

- 目录保留原始同级命名，独审`run_parser_negatives.py`/`run_actual_main.py`默认能找到benchmark。也可显式`PEN_BENCH_SOURCE=<本包benchmark目录>`。建议复制到临时工作目录后运行，因为`run_actual_main.py`会生成`run_output`，且sanitized配置需要已安装的编译器ASAN/UBSAN运行库。
- `tools/check_host.py`与`tools/test_serial_parser.py`只依赖包内冻结内容和标准库/cc。`tools/embed_fixtures.py`会重写`main/fixtures.h`，只能在工作副本运行，随后应与冻结文件逐字节对比。
- MCU重新编译需要自行提供已验证ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`、xtensa GCC14.2.0工具链及IDF依赖，本包不带SDK。所有归档脚本保存为非可执行普通文件，使用`bash tools/build_only.sh disabled`或`enabled`（仅build），不执行日志里的设备命令。
- `tools/check_static.py`还需要重新构建产生的`build-enabled.config`、BIN和重新提取的symbols/image_info；这些可执行/构建产物故意不在包内。仅凭存档的static-check.json不能声称在新环境重新完成该验证。
- 没有实板RAM/PSRAM性能结果，没有受验证的PSRAM可运行profile；mock时钟每次增加123是假时间。parser即使功能一致也固定`identity_verified=false`、`overall_pass=null`，CLI exit2不是设备通过。
- 任何实板执行仍须针对实际板型确认接线、允许中断、私有备份/恢复及另行授权；本归档没有提供现阶段可直接运行的设备加载流程。

## 发布边界

此目录是候选增量，不改变r4或`assembly_plan_2228`。提交/推送尚未执行，仍待父任务澄清；PGM/NPY均为合成输出，不含用户打印PDF、厂商私密PDF、设备Flash备份、密钥或笔迹。模式筛查未发现高置信秘密特征，但任何自动筛查都不是“绝无秘密”的证明。原文件的字节数/SHA256/Git blob SHA1、原路径→目标路径映射及旧树未变证据见r5根目录manifest/report。
