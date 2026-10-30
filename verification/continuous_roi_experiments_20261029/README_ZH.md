# r6：连续纸张ROI v2独立实验与修前/修后审查

**NOFAB / NONPRODUCTION / SYNTHETIC ONLY。仅本地归档、主机可重现检查；未提交/推送、未连接/复位/刷写设备。所有源码留在本实验命名空间，不替换主项目`firmware/vision`，不接应用record链，不赋予笔尖VALID。**

## 先看限制，不能用108/108掩盖

| 冻结作者合成组 | 接受/尝试 | 仍待解决的问题 |
|---|---:|---|
| 精确5/6/7mm、36相位/视场 |108/108|仅该理想Profile-C条件|
| 分数FOV |**17/36**|非连续尺度鲁棒性证明|
| 平面旋转 |**60/96**|不是物理笔倾角支持|
| 全部扩展组 |218/340|有限测试中0错OK/218接受；不是总体零风险|

工作区**31,104字节**，另有40,000字节输入；合计71,104字节还未包括调用栈、应用、RTOS和DMA。没有S3耗时/FPS、目标栈高水位、功耗或温升测量；存档主机wall-clock字段不许换算成S3性能。离散搜索、透视/剪切/镜头畸变、物理笔尖标定、真实相机和手写污染均未获得资格。

V1会擦除8/11/12像素深边缘墨迹；V2以面积≤24、bbox≤6×6、每个接触边的入侵深度≤4修正这三项。**点大小墨迹仍不可与点阵区分，ROI外图像仍不检查。** 保留正确坐标也不是墨迹分类安全或整帧健康证明。原V1负面发现、原日志和V2闭环均完整保留。

## 精确选取的归档，不是358文件整树复制

- `smart_pen_continuous_roi_candidate_20261028/`：63项选取文件，含v2 core/codec和许可证、19张固定图及oracle、当前候选8项测试与导入依赖、设计/集成门禁、340条扩展结果、80项原host gate日志、栈/ASan+UBSan证据、修前结果、冻结完整清单。没有其他硬件/应用模块或SDK。
- `smart_pen_continuous_independent_review_20261029/`：122项，含V1与V2各自9文件源码snapshot、72张V1固定图、6张V2片段/角点图、前后结果、原审查脚本/报告/日志及原SHA清单。只排除编译出的`review.so`和`safety`程序。
- `smart_pen_vision_opt_20261028/tests/`：仅4项旧ctypes布局/纯Python渲染导入依赖，来自固定`685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`；**不是完整旧仓库**。
- `smart_pen_viewport_audit_20261028/`：仅49项：原44张PGM、原regression manifest、432条原基线记录、合成方向NPY、来源与旧SHA清单。NPY仅1000×710 uint8方向0–3，不含pickle。无厂商PDF、用户打印PDF、笔迹或设备备份。
- 另4项独立旧Nano勘误映射到同级`../decoder_experiments_20261028/smart_pen_decoder_benchmark_erratum_20261029/`，不改r5旧包。

候选完整manifest SHA256：`b1f93dc63cb5a564a51fb742520f23af96abed81bd5d4bb5974dba00cd64b460`。
完整SHA清单SHA256：`3cadddcc69e133478afddd5f6cfad2ae0d7bcc8e95359459084a69f12b58a549`。

归档前358项全部逐项核对，但只复制明确必要子集。**原358项清单和旧viewport SHA清单是历史全范围出处，不能对这个缩减胶囊直接运行并期待全部文件存在。** 离线验证本包应使用`SOURCE_SUBSET_SHA256.json`、portable helper及r6根目录总manifest/SHA256SUMS。

## 可离线快速检查：不写冻结文件

在本目录使用受控环境中已安装的Python3.9+、`cc`、`nm`和libm：

```sh
python3 portable_check.py > /tmp/smartpen-r6-quick.json
```

先验238项原始源码/依赖SHA，再复制到系统临时目录运行原候选**8项host单元测试**，运行后重验归档未变。包括6张全场图、10张扩展图和3项深墨迹拒绝、API/缓冲区/变换/工作区/heap符号测试。临时已知C代码编译产物不进归档。helper不下载、不联网、不访问设备，也不运行工具链SDK。

需要已安装NumPy的可信Python时，可重现独立V2审查：

```sh
python3 portable_check.py --independent > /tmp/smartpen-r6-independent.json
```

这仍在临时工作副本运行**原`v2_review.py`与`corner_control.py`**，不是替换审查算法：

- V2 snapshot重放V1原72张像素；保留V1原results供修前/修后比对。
- 原独立逆向栅格化器重生成48个精确相位样本；验证符号、支持范围、正反向变换。
- 重生成5个片段+1个隔离角点PGM。
- 将5份JSON与6张PGM同冻结结果比对（图像字节/状态严格一致，浮点仅允许1e−9相对舍入差）。

新helper与`portable_check_result.json`是本轮新证据，和原审查日志分列hash。它不重跑原V1全部研究、原80项整仓host gate或sanitizer；那些被保留为历史证据，不能重标为本轮重新运行。原V2独审的77/102接受、0错OK/77是有限理想测试，不是概率保证。

## 原脚本相对依赖闭环

原`review.py`从同级`smart_pen_vision_opt_20261028/tests`导入Config/OptResult，再从同级`smart_pen_viewport_audit_20261028`读取矩阵和44图oracle。`v2_review.py`重用`review.py`setup/renderer/oracle，并改绑`v2/snapshot`，同时读取父目录的`results.json`和72张PGM；`resume_fragments.py`还读取既有replay/phase结果；`corner_control.py`同样依赖V2 setup。上列必要文件全部按原同级目录布局归档，不把工作区绝对路径当成用户路径。

**不要直接在冻结目录执行原脚本**：它们会写`bridge.c/review.so`、结果JSON与PGM。用portable helper或手工复制整个实验胶囊到临时目录，再运行。原`run.log`保存了V2初次helper空白区域查找过严的失败；修正后的原脚本及resume证据保留，不抹除历史。

## 完整340 sweep、80 host与sanitizer的进一步复现

完整340 sweep需要已安装NumPy；`tools/continuous_roi_sweep.py`读包内矩阵/results即可渲染，但还会用`git rev-parse HEAD`记录来源。此缩减胶囊没有完整git源树，不能用当前新仓库HEAD伪装原base。

要完整复现，应从用户已拥有的可信本地源，创建固定base `685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`的工作副本，再**仅在该副本**覆盖本包candidate子集，并按完整358项manifest核对补齐的来源；不能盲目改成远端HEAD。本次没有获取或下载完整旧仓库。

然后将本包audit依赖目录放在同级，在工作副本运行原sweep并使用`--out <独立临时输出目录>`，避免覆盖冻结results。完整80项`software/verify_host.py`另外依赖整套base代码、原上游`0f8b569176c77dad34aaf83bb008eb118c9f1208`的`digital_pen_ov5640/pc/src`以及已安装cv2/numpy/fastapi/httpx/uvicorn/bleak；它缺依赖或跳过测试即失败。这个缩减包不是80项全仓应用测试的独立发行版。

ASan+UBSan复现需受控编译器对应runtime；原命令见独审REVIEW。原成功sanitizer关闭了LeakSanitizer，应保留这个限制，不声称内存形式化证明或目标栈安全。本轮portable复现没有再执行sanitizer。

## Nano勘误交叉链接和下一门禁

旧基准的独立补充勘误在[ERRATUM.md](../decoder_experiments_20261028/smart_pen_decoder_benchmark_erratum_20261029/ERRATUM.md)，SHA清单`174cff456320f04a159d6d80e2174818b99efe16155ed41fa0b61fd91648a38d`。它进一步核实旧实际link map使用`libc_nano.a(nano-vfprintf)`；旧基准目标计时JSON采集被阻断，不能用hostmock/构建成功绕过。原r5未改写。

正在开发的新target变体不在r6；不等它、不收移动日志、不默认加载设备。后续先修尺度/旋转获取覆盖并保持拒绝，再做真实相机/手写资格、S3资源测量与笔尖映射；应用record/contact/calibration/camera_qualified门禁均不能旁路。
