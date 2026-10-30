# r7：Continuous V2独立RAM基准的新源码/离线重现入口

**NOFAB / NONPRODUCTION / SYNTHETIC ONLY；尚未上板。** 本包归档新的47项冻结源、构建/链接证据和19项独审。它是待板型识别、私有备份/恢复条件和用户允许中断之后另行制定执行流程的候选，**不是实机FPS、目标格式自检已运行、安全或整笔可用的证明**。未提交/推送或执行设备操作；不接应用record链。

## 冻结范围及版本关系

- `smart_pen_continuous_target_benchmark_20261029/`：47项冻结源码/夹具/许可证/中文说明，加24项必要构建证据和`.gitignore`。只保留清单要求的独立旧core对照；不复制r5/r6完整旧仓库或SDK。
- `smart_pen_continuous_target_review_20261029/`：19项独审证据及原manifest；排除`run_output`全部临时二进制。
- 清单SHA256：`af121d057a80ac01be6d19217abea3988b3e96fe6769651ebe7c18c4f45ed2db`。
- 独审manifest SHA256：`b17c9500d106216bdee85c4cd21ac1af82bc2a5bfcdbf346019d37282e7c3fd0`。

旧r5基准仍因nano/64-bit输出不兼容而被阻断，不能以新包通过追溯覆盖旧报告。必须一起阅读r6归档的[独立Nano勘误](../decoder_experiments_20261028/smart_pen_decoder_benchmark_erratum_20261029/ERRATUM.md)；仅解包r7时该跨增量链接需要先合并r6的对应payload。本包的`BASELINE_SAFETY_REFERENCE_ZH.md`只是旧安全流程原文，不是旧基准运行推荐。

新包effective config明确禁用nano，源码误开启会编译拒绝；实际target link map/symbol证明full `libc.a(libc_a-vfprintf.o)`、`_vfprintf_r/_dtoa_r/snprintf`在IRAM，并有分配/解码前格式自检及schema2强制探针。**这些是配置/链接和源逻辑证据；目标自检尚未实跑。** 不把host libc/mock结果代替目标newlib运行证据。

## 资源核算不可漏掉PURE_RAM静态夹具

| 项目 | 冻结证据中的字节数 | 边界 |
|---|---:|---|
| 工作区 |31,104|旧core21,888 + crop9,216；两个实现串行复用，不是双工作区|
| 同一Gray8输入 |40,000|heap输入+工作区71,104，另有运行开销|
| 6个packed-RLE const数组 |125,442|PURE_RAM里占**内部DRAM**，不是外部Flash；字符串/对齐等额外|
| 主任务配置栈 |16,384|另有其他RTOS栈；不是测得余量|
| 加载镜像 |290,480|仅归档hash/装载段文本，不带BIN；不是可用heap|

full printf/dtoa还占代码/静态及可能的动态栈/heap成本。`size`的text/data/bss标签包含linker alias/dummy区域，不能简单相加当物理峰值，也不能用链接通过推定71,104B heap申请或栈余量足够。分配失败为fatal；只有后续另行授权实板日志才能检查实际资源。详见`verification/RAM_ACCOUNTING.md`、sections/stack/size/image-info证据；本轮不重建目标SDK。

## 可离线移植检查，不写冻结证据

需受控环境已经安装Python3.9+、`cc`、标准C/math库和编译器ASAN/UBSAN runtime。无需NumPy、旧源repo、ESP-IDF、网络或设备：

```sh
python3 portable_check.py > /tmp/smartpen-r7-portable.json
```

helper先验92项原始文件SHA，复制两个原目录到系统临时工作区，然后执行已审源码：

1. packed-RLE/源绑定重建，与冻结header和build-inputs逐字节一致。
2. 原host功能12条、作者独立几何检查、作者13项parser测试。
3. 独立34项parser负例、108个上游生成器几何点。
4. 实际`bench_main`五种host配置（enabled/disabled/分配失败/格式自检失败/ASAN+UBSAN）及nano误启用编译拒绝。
5. 用已包含的独审`generator_oracles.json`（其SHA就是原生成器manifest SHA）在**临时目录**恢复原provenance抽取脚本期望的单个文件路径，重提取几何oracle；旧core oracle重算也逐字节一致。没有额外复制整个r6候选。
6. 工作结束再次核对归档源未变；二进制、对象文件和mock输出只在临时目录。新`portable_check_result.json`是本轮证据，和原审查日志分开hash。

人工clock每次增加123，仅验证36次调用的计时边界/次数；不提供可冒充实机的串口捕获。host sanitizer关闭LeakSanitizer，不声称目标硬件内存验证。parser始终`identity_verified=false/overall_pass=null`，即使功能一致CLI仍exit2；文件hash不是设备或日志真实性认证。

## 原脚本相对路径与重新构建

两个原目录保留同级名称，独审脚本默认能找到benchmark，也支持`PEN_BENCH_SOURCE`。普通host重现只用包内文件。原`freeze_independent_geometry.py`有历史同级candidate路径要求，portable helper已经用**包内相同hash的单文件oracle**在临时工作区满足，不需要下载/复制整个旧源码树。

原`embed_fixtures.py`、freeze脚本及独审`run_actual_main.py`会写文件，所以不要直接在冻结目录运行；用helper或手工复制到可丢弃工作目录。旧日志中的`/workspace/...`只是历史出处。归档脚本模式全部100644，需要构建时用`bash tools/build_only.sh disabled`/`enabled`，不假设可执行位。

target重建须自行提供已验证ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`及对应Xtensa工具链/依赖；本包不下载或携带SDK。`check_static.py`还需要新环境生成的effective config、完整map、BIN、symbols与image_info。排除build/BIN/ELF是有意的；仅读存档static-check不能叫新环境重建验证。**不要执行SDK日志自动打印的flash/write_flash尾注。**

原47清单可在benchmark目录核验；全92原始归档可由`SOURCE_SUBSET_SHA256.json`检查；所有新文档/helper/报告则由r7总manifest与SHA256SUMS覆盖。

## 使用分母和剩余门禁

固定6张200×200合成图：旧core六张均预期拒绝；V2三张5/6/7mm phase0接受，45°/深边墨迹/9mm超范围密度三张拒绝。默认3轮36次调用仅9次V2正确坐标，27次预期拒绝；不能将拒绝计成成功吞吐。timer包括V2完整选裁剪/复制/边缘处理/解码/变换，不包括采图、RLE解压、分配、串口或调度；因此不是相机FPS或整链路延迟。

前序v2有限扫测仍为**分数FOV17/36、旋转60/96**；点大小墨迹可被擦除、ROI外像素不查，general透视/物理倾角/笔尖/真实纸张与相机都未获资格。新基准不扩大算法覆盖，不绕过应用record/contact/calibration/camera_qualified门禁。

实物身份、现有固件用途、两次私有整片备份/恢复条件、允许中断、供电接线、目标格式探针、完整启动日志、S3实际内存余量、耗时/功耗/温度均待后续授权验证。不得上传Flash备份、密钥、凭据或笔迹；不force绕保护、不改eFuse、不无条件擦写。
