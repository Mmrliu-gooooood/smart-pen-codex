# V4 投影实验独立复核（2026-10-30）

## 结论 / 使用边界

**NOT ADOPTED：维持拒绝，不得替换 V3、接入目标 app 或宣称产品支持倾斜。**
中心80 ROI 的确改善若干理想投影图，但旧96证据域中的墨线被裁掉：三个原 `must_reject` 的 `edge_stroke` 负例仍接受。它们的坐标、36符号和方向正确，仍然是质量合同违规；“0错坐标”不能把这三个违规洗成通过。

独立复核只在新增 review 目录和 sibling 运行副本写入；未改候选/基线、未调参、未运行硬件、未发布。原候选 manifest SHA256 为 `14d0db5c3b3dd96b6b70d3e9afa349d3afc2eeeba85e729ec68a402868ae5384`。

## 发现与证据

1. **发布阻断：证据范围缩小。** `source/firmware/vision/roi_projective.c:45–69,125` 只扫描中心80；三个 edge_stroke 的完整独立重跑见 `negative_contract_review.json`。额外将80之外全部替换为240，返回结果（含诊断和H）仍逐字段相同，直接证实外围像素不参与决策。必须保留原负例合同为红；本轮没有实现任何外围验证修补。
2. **ABI 必须独立。** `roi_projective.h:9–27` 明示 version4、正逆9系数；不可当旧6系数affine使用。新TU在 `.c:4` include原 `roi_opt.c`，故不可同时链接两份TU。原 `source/firmware/vision_idf/main/CMakeLists.txt:1` 仍编译旧 `roi_opt.c`，非新算法目标集成证据。
3. **数值与计算界。** `.c:8–40` 检查有限数、分母、逆矩阵、部分选主元、正行列式及ROI分母变化；`.c:74–89` 的5阶段×5迭代上界固定；`.c:94–97` 在整数转换前限制格坐标±80；`.c:128–136` 固定61×49×11=32879粗候选，256种子上限溢出返回AMBIGUOUS，不截断挑最好。独立 `numerical_review.c` 39项坏数/退化/镜像/地平线/大坐标检查通过ASan+UBSan+float-cast-overflow。它是有界针对性测试，不是所有浮点输入的形式证明。
4. **四个方形支持警告不是实际圆点越界。** 独立标量投影与每圆65536角度采样核查，最小真实圆周余量0.4973866375px（另两例0.4995798526px）；与解析分式正弦极值差<1e-6px。采样仅交叉验证，不把离散采样冒充连续几何证明。`support_oracle.py:17–33` 的导数极值公式亦经源码审阅；保守方形角越界不应称错码。

## 精确验收合同与计量单位

- 所有结果针对200×200原始连续像素合成图，整数为像素中心，ROI像素覆盖域边界为 `[left-.5,left+width-.5)`。
- 原8成功图/保留集：36符号逐项相同、6×6完整支持、每个格点两基方向差<5°、最大格点位置误差≤0.1 cell（pitch10时≤1px），且不是must_reject负例。不是“置信度超过某分数”或统计可靠率。
- 旧408回归位置容差为 `.1*(60/fov)` 像素，即0.1cell；连续圆支持容差仅1e-8px，允许浮点边界误差，不放松坐标/符号/负例合同。
- 独立复核的原8成功图最大误差0.102532225px，最小逐基cosine0.999997655；4圆支持警告及原8成功图记录于 `independent_geometry.json`。
- 120保留集是固定合成设计样本，不是独立同分布的真实相机总体抽样。“37正确、0观察错接”不能推出生产可靠性，更不能掩盖旧负例3违规。

## 光学与硬件边界

相机V2是固定VGA640×480 Gray8、stride640的零拷贝子视图，不缩放（`../smart_pen_camera_capture_v2_candidate_20261029/src/pen_capture_app.c`，参照 `../smart_pen_optical_sampling_audit_20261030/REPORT.zh-CN.md`）。200原像素=6mm要求全幅640在同倍率下=19.2mm；若全幅=6mm，200裁切仅1.875mm、96内部仅0.9mm、80仅0.75mm，放不下6中心1.5mm跨度，更不满足约1.7mm完整墨点支持。

f=400px、Z=12mm、点距0.3mm只是理想合成针孔假设；相机光轴倾角不等于握笔角，网格坐标不等于笔尖。workspace36480B是host ABI结果；32879候选之外还有≤256×25次refinement及codec窗口检查，不可据此推算ESP32-S3 FPS。本次无SDK构建/目标栈/性能/真实镜头/SC035支持资格结论。LSan未运行，不能借ASan/UBSan通过声称LSan通过。

## 复现方式

`PYTHON=../smart_pen_host_venv_20261028/bin/python bash ../smart_pen_tilt_v4_review_run_20261030/reproduce.sh` 在运行副本执行。必须保留最终非零的原回归负例门；不得删断言。所有依赖均在当前工作区找到，无依赖或权限缺口。

独立附加测试源在本目录：`numerical_review.c`、`independent_geometry.py`、`negative_contract_review.py`。完整命令/结果见 `reproduce.log`、各专属log与最终 `verification_summary.json`。

## 最终执行结果（已完成）

|检查|独立复现结果|
|---|---|
|冻结manifest|462登记文件哈希/大小全部匹配；465实际文件前后完整快照完全相同（额外3项是MANIFEST、SHA256SUMS、NEW_FILES）|
|旧V3冻结源|394原件及候选复制件都逐哈希匹配|
|原8张投影图|6正确/2拒绝；60°两例都拒绝|
|120保留集|37正确/83拒绝，30负例全部拒绝；不是生产成功率|
|原340+68回归|225正确接受 + **3质量合同违规接受** + 180拒绝；违规非错坐标|
|旧ABI|44 cold / 12 warm逐字节一致|
|旧host|85 tests，0 skip，全部通过|
|ASan/UBSan|候选56调用/随机32及独立39数值检查通过；seedcap=1注入拒绝通过|
|总复现出口|**1**，唯一失败命令是原 `run_regression.py` 的3违规门，保留红灯|

8项复现JSON（忽略机器运行时字段后）与冻结版本全部一致，涵盖图像哈希、坐标、H、状态、诊断、oracle与各组汇总；不是仅比总数。最终记录见 `verification_summary.json`，原日志 `reproduce.log`。

下一候选若授权，应先明确更大验证域/墨线合同，再设计外围验证，不是调松门限或修改旧must_reject。本复核没有提出已通过的新候选，也不授权硬件/SDK/app集成。
