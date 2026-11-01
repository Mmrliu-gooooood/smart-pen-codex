# 已有V3对照：相同70生成图与旧408质量合同

**只比较已有源代码，不修复、不采纳、不修改活动板或provider，不证明实物笔尖/IR资格。** 本阶段接续已冻结光学筛查；其小项元数据纠正见[独立纠正注](PRIOR_SCREEN_METADATA_ERRATUM.md)。

## 实际结果

|相同70输入|正确接受|错误接受|拒绝|
|---|---:|---:|---:|
|活动正交冷搜索|22|0|48|
|归档V3，实际96/80裁切ABI|29|0|41|

- 共同接受20，恢复9，丢失2，共同拒绝39。9恢复为3个15°合成透视、δ/p=1/6案例和6个cos15/cos30非透视仿射案例；不是通用倾角极限。
- V3的29个接受全返回96×96；17个拒绝没有进入核心。pitch20/32两个活动正例在V3中丢失，原因是裁切不足以提供36个完整观测点。不能给V3绕过ABI喂完整200框后仍冒称原V3结果。
- 包装器记录真实crop调用；同70图的无包装原始返回值与记录版逐字节一致。输入、失败输出、workspace边界按回放脚本核查；具体证据见[replay](replay/README.md)。工作区32640B、result192B，不得沿用活动核心21888B或旧ABI。

## 旧408回归与退出码

`legacy408/run.py`实际调用原V3的`ContinuousROI`、原render/evaluate，通过冻结340+68规格重新生成每张图，先逐一核对原像素SHA，再调用C。结果：**254正确接受 / 0错误或质量违规接受 / 154拒绝，状态变化0，exit0**。原340中253接受；68对抗中只有一致双窗口1例接受。全部must_reject保持拒绝；未将旧负例改为成功。

这是既有V3历史质量合同的重放，不是改用V4，也不把V4原225正确+3违规+180拒绝洗成通过。原V3`evaluate`以点中心支持和原变换误差门判断；**未升级为全墨点边界/完整物理质量oracle**。原始质量合同和盲点必须保留，以后不能把更强标准悄悄套入旧PASS。

原`portable_check.py`另外真实运行exit0：13项host测试通过、296原文件及132诊断PGM像素SHA验证。其JSON中的“未重跑340”只描述该quick工具范围；本阶段独立legacy408随后确实重跑340+68。没有新ASan/UBSan/LSan、SDK或设备测试，不能沿用旧日志冒充新测。

## 最小后续实现建议

先在独立默认关闭候选中，**保留原active完整ROI质量门，复用V3已有正交细化核心**，隔离粗搜索量化改进，不整套替换成固定96/80裁切。回归先锁住6个仿射恢复例、pitch20/32原正例以及全部旧must_reject；明确workspace/ABI变化。一般透视留待证据充分后处理，不重写重复decoder。详见[候选门槛](NEXT_CANDIDATE_PROPOSAL.md)。

后续V4路线必须先修复3个旧质量违规，保留crop外该检查的证据，不能仅靠答案正确或残差小通过。拒绝/缺帧保持GAP，不跨未资格化GAP插值、沿用旧坐标或改时间戳。

## 复现

依赖固定公开仓库源与上一阶段70生成图；没有原始用户照片/PDF。详见DEPENDENCIES.json、replay的source/imagehashes和legacy408/input_hashes。用新可写副本，在保持本阶段与`publication_20261031/target_repo`相对布局时：

```sh
python optics_v3_comparison_20261031_1759/legacy408/run.py
python optics_v3_comparison_20261031_1759/replay/replay_v3.py
python publication_20261031/target_repo/verification/continuous_v3_experiments_20261029/portable_check.py
```

生成输出只写本阶段新副本，编译库在临时目录；原代码不改。普通host O2与记录的时间仅用于复核，不推算ESP32性能。先核manifest，不在冻结目录覆盖日志。
