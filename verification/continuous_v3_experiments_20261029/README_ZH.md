# r8：V3连续拟合实验、失败根因诊断与独审

**NOFAB / NONPRODUCTION / SYNTHETIC ONLY。仅本地，不提交/推送、不执行设备、不替换V2或主项目firmware、不接应用record/VALID链。** 不等待或收录新target变体；r7仍是V2对照基准，不能偷偷换V3源码后沿用其ABI/栈/构建结论。

## 结果、拒绝与不可越过的边界

| 冻结主扫测 | V2 | V3 | 解释 |
|---|---:|---:|---|
| 分数FOV |17/36|36/36|19个有真实完整窗口的粗网格残差失败被恢复|
| 平面旋转 |60/96|76/96|恢复16个；另外**20个没有完整实测6×6窗口，保持拒绝**|
| 全部340图 |218接受|253接受|仅35个NO_GRID→正确OK，其余状态不变；0错OK/253仅有限合成观察|
| 独立clean 102图 |77接受|97接受|剩余5个也无完整实测窗口；0错OK/97不是总体概率保证|

真值、已知FOV/角度/格点/码字、生成器矩阵只用于**C返回后的诊断或oracle**，从不传入生产initializer、phase、prior或搜索。诊断132张PGM保留原像素SHA和全部点/阶段计数。无完整窗口不能用插点、码字猜测或成功驱动ROI重试伪造恢复。

V3仍检查26,901粗假设；宽松值只用于捕获initializer，不放松最终major/minor残差、不同格点、实测完整窗口、codec边界与全已找到模型一致性。保留全部合格seed，**第65个拒绝AMBIGUOUS，不截取top-k、不提前OK**。真实默认64预算溢出图在864次粗假设后得到65 seed、0 refit/0 refined model，输出/transform及seed两侧guards保持。

有限capture范围/最多5次迭代不是全部连续模型的全局唯一性证明；点大小墨迹仍可能被擦掉，ROI外图像不检查；真实打印、相机、笔尖/物理倾角、透视、手写、功耗/热及S3实时性均未获资格。

## 内存、ABI与性能门

- 工作区**32,640B** = 21,888 core + 9,216 crop + 1,536 seed；200×200输入另40,000B，输入+workspace **72,640B**还未计result/栈/RTOS/DMA/应用。
- **V3 continuous result=192B，V2=184B**。必须匹配新header/ctypes，不得把V2 buffer传入V3或强制转成应用mapper。原opt result/workspace ABI保留，不代表代码大小或栈成本不变。
- decode失败保持result/transform，diagnostics则每次有意重置/覆盖；diagnostics/result/transform/seeds/input/config/workspace不能重叠，scratch不能并发复用。
- 64 seed、最多320 refit迭代、64额外严格验证有界，但捕获评分/phase重算也消耗CPU。32KiB内放得下不证明60FPS。原paired主机CPU比例只作为环境相关历史数据，不推算S3速度或“更快”。本次没有target构建/执行。

## 归档精确范围

- `smart_pen_continuous_roi_v3_candidate_20261029/`：严格遵循作者`V3_DELIVERY_ALLOWLIST.json`的**99项**当前core、测试、夹具、设计/集成门禁和证据；不是完整394项继承历史树。
- `smart_pen_continuous_fit_diagnostic_20261029/`：显式snapshot的**164项**源码/数据/日志/132张PGM，另原snapshot+SHA清单。包括V2原源码与明确命名的instrumented副本、未采用的neighbor-vector原型和两个initializer envelope实验，不隐藏失败方案；排除全部.so。
- `smart_pen_continuous_v3_independent_review_20261029/`：**29项**冻结源码/报告/脚本/结果/stack文本加2项原SHA清单；排除.so、.o和safety可执行文件。
- 旧V2源码、旧72图、旧44图和生成器矩阵由`DEPENDENCY_LINKS.json`精确引用r6的**154项 / 5,242,776字节**；不再复制整旧仓库。helper验证每项hash后仅在临时目录恢复原相对目录名。

V3完整snapshot SHA256：`1636084759c3ebfc358574f669ea5292b11ae4421145401e7c2ccaed12664ccf`。
V3完整SUMS SHA256：`b5a5a468ef113d9bf64836a6e4714e7c5218546554046b89ac01cfbfca1716e4`。
99项allowlist SHA256：`76857d7103d895bbedf2e723984e59eba593660e4837ae43a88f3a12c685bd4b`。
诊断snapshot SHA256：`d63ddd9365cc235d0ab2c4af38a71c0f7c445d7a7220e9335698d7abe0a9cdfe`。
独审报告SHA256：`bd3060e24a05cc87dd0fdf3adf34b00ac752718d3dd79f7670db6fc23bd5e49b`。

归档前394项全清单逐项通过，但完整394清单只是来源记录；不要在缩减包直接执行它并期待未选历史文件全部存在。当前复制的296原文件由`SOURCE_SUBSET_SHA256.json`精确验证，新helper/说明/结果由r8总manifest覆盖。原README的`verification/v2_baseline`和完整host脚本等历史路径未盲目带入，应查r6或可信完整base。

## 离线quick验证：不改冻结文件

受控环境已安装Python3.9+、cc、nm和libm，在本目录：

```sh
python3 portable_check.py > /tmp/smartpen-r8-quick.json
```

无需NumPy/旧依赖即可核296源文件、132诊断PGM像素SHA及20无窗口记录，并在临时副本执行**13项候选测试**，覆盖默认64/cap1分支、真实65 seed溢出、窗口冲突/缺失、输入/输出/ABI/工作区等。native测试为普通host编译，不冒称新sanitizer运行。

完整独审复现需要已安装NumPy及固定r6实验目录：

```sh
python3 portable_check.py --independent > /tmp/smartpen-r8-independent.json
# 若r6不在已组装repo的同级实验目录或原本地archive布局：
python3 portable_check.py --independent --dependency-root /path/to/continuous_roi_experiments_20261029
```

helper不会网络获取依赖。将296项本包及精确154项r6文件装入临时工作区后，运行**原**`review.py`、`verify_observed_support.py`、`overflow_probe.py`；比较8份JSON（仅容许1e−9相对浮点舍入差）及真实默认溢出PGM字节：

- 原44图cold完整result、成功warm result/prior与V2逐字节一致。
- 原72图重放、48相位生成、6片段/角点、20无完整窗口拒绝。
- 54 clean图独立实测component支持复核；49个返回窗口全部由实际观测组件支持，剩5无窗口。
- 真默认第65个seed拒绝及guards检查；不是只把编译预算缩成1来代替。

运行前后再次核对本包和r6依赖未变，所有编译物/输出只在临时目录。`portable_check_result.json`是本轮新复核证据；原85host、340扫测、68 adversarial、132完整诊断及原ASan+UBSan日志保留，但本轮没有声称全部重跑或重做sanitizer。原LeakSanitizer关闭限制保留。

## 完整研究再生成与必要依赖

原独审相对依赖是：同级旧V2 core，旧独审的72PGM/results及V2 phase/fragment结果，同级viewport的矩阵+44图，以及本包诊断results/20对应像素。`DEPENDENCY_LINKS.json`包含精确路径/hash。诊断Python还导入V2的sweep/ctypes测试布局；其最小必要模块、V2结果和paired数据所需6图也在复用清单中。

原脚本会写桥接C、.so、JSON、PGM；不要直接在冻结目录运行。想重跑完整诊断/原型，只能在按helper相同布局复制的可写副本先编译原REPORT列出的桥接源码，再调用原脚本。`paired_cpu.py`只是host观察，不把新时钟值混回冻结证据；任何全量再生成都应保存到独立输出。

完整85 host需可信base commit `685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`的完整工作副本和原上游PC source及其现有Python依赖，覆盖本包allowlist后核对完整snapshot；本包不携带无关硬件/应用或自动下载依赖。340 sweep的原脚本会记录`git rev-parse HEAD`，须用真实固定base工作树，不能把新仓库HEAD伪装出处。详情仍以冻结作者/独审报告为准。

r4–r7不改写；后续target变体另行冻结、构建/独审，实物身份、备份恢复和允许中断另需授权。不得把V3主机改善直接写成S3FPS、相机可靠、物理笔尖VALID或设备安全通过。
