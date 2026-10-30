# V4 独立回归：门禁未通过

最终源重跑：340 continuous + 68 adversarial，图像 SHA256 均逐项匹配冻结 V3 原结果。`run_regression.py` **退出码1**，因为3个原要求拒绝的墨迹负例被接受；不能据此替换 V3 或集成应用。

|集合|接受且正确|禁止负例被接受|错坐标/符号/方向|拒绝|
|---|---:|---:|---:|---:|
|continuous 340|224|3|0|113|
|adversarial 68|1|0|0|67|

- continuous索引252/280/308，分别fov5/6/7的`edge_stroke`：墨迹在输入y=51..54，V4固定80裁切从60开始，未观察墨迹就接受。这违反原`must_reject`契约，**即使坐标正确也不豁免**。精确PGM：`regression_false_252.pgm`、`regression_false_280.pgm`、`regression_false_308.pgm`。
- V3原253个接受中，新API37个转拒绝；新增11个接受中8个正确、3个上述禁止负例。新路径不是无回归替代品。
- 68 adversarial的镜像、quarter-turn、假码、矛盾窗口均未误接受。两窗口一致例正确接受；冲突例返回NO_GRID(-3)，不承诺保留V3的AMBIGUOUS(-4)状态码。
- 独立44例旧`pen_roi_decode_opt` ABI：新TU所包含的旧实现与冻结V3全部cold结果逐字节一致；12个cold成功者warm结果和prior也逐字节一致（其余32例warm未调用，以null而非false记录）。新projective API的回归与旧API未回归是两个不同结论。

## 完整支持与保守方形界

旋转索引140/160/182/202的墨点**外包方形角**越裁切边界，初始保守门禁记为失败；这不等于圆墨点缺失。`support_oracle.py`独立解析计算真实合成圆盘经单应映射后的轴向极值：每轴为`(A+B cosθ+C sinθ)/(D+E cosθ+F sinθ)`，先检查整圆分母为正，再解导数零点`K cosθ+L sinθ+M=0`。浮点边界容差1e-8px。

四例完整圆盘实际最小余量分别约+0.497386638px、+0.497386638px、+0.499579853px、+0.499579853px，因此完整圆盘均在裁切内。结果同时保留`square_support`和`circle_support`，不把保守方形失败冒称假码。独立4096角/点诊断与解析结果一致；100随机单应、每圆20000采样的交叉检查通过（`test_support_oracle.py`）。这只证明理想合成圆盘，不代表真实印刷、失焦PSF或相机。

## 复现与证据

在本目录执行（numpy、C11编译器）：

```sh
PYTHONDONTWRITEBYTECODE=1 python run_regression.py  # 预期exit1
PYTHONDONTWRITEBYTECODE=1 python replay_legacy44.py
PYTHONDONTWRITEBYTECODE=1 python test_support_oracle.py
```

- `regression_results.json`、`regression_summary.json`、`regression.log`：最终408例；`regression_provenance.json`：实际编译源码/脚本哈希，完成时全部仍匹配。
- `legacy44_results.json`、`legacy44.log`：旧ABI逐字节对照。
- `initial_square_*`：初轮保守方形门结果保留；不与最终真实圆盘分类混淆。两轮全部状态和已接受H逐项相同。
- `regression_false_140/160/182/202.pgm`是初轮保守方形诊断图，不是错误坐标证据。
- 新API实际workspace36480字节；本集合观察上界：32879粗候选、31种子、775细化迭代。诊断有overflow failclosed。这里只记录host秒数便于复现，不折算S3 FPS。

未修改冻结原目录，未改C算法以迎合结果，未push；仍需父任务整合holdout、安全测试及独立审查。
