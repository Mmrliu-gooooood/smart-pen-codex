# 默认关闭的完整ROI正交细化候选

**独立host研究候选，不接入活动固件/provider，不是V3整套裁切或V4透视采纳。** 原公开源、活动板和生产NULL provider保持不变。没有制造、购买、上电或外部发布。

## 最小代码变化

`candidate.c`32行、`candidate.h`18行（冻结前以实际文件为准）：
- 未定义`CANDIDATE_ENABLE_REFINEMENT`时默认0。OFF调用精确原活动`pen_roi_decode_opt(...prior=NULL...)`。
- ON完整调用已有V3`pen_roi_decode_refined_transform`，输入尺寸、stride和像素原样传入；不调用`roi_continuous`，不裁96/80，不制造prior，不先返回活动成功。
- 仍遍历所有有界粗候选/合格seed并执行一致性检查；第65seed失败关闭，不能截断seed或取首成功。
- 原active/V3`detect`逐字相同：整ROI对比度、连通域形状/面积/边界、36..128点检查不变。宽松seed搜索盆地不是放松最终严格位移/完整窗口合同。
- 输入/config/workspace/result/diagnostics范围重叠或地址加法溢出，新增ARGUMENT拒绝在任何写之前发生。其余调用diagnostics按接口重置，失败不写result；workspace/seed为可变scratch。调用者须提供真实可读/写buffer和足够容量；范围检查不能证明一个任意地址属于已分配对象。

编译符号隔离原active和归档V3。没有复制改写decoder算法；已有源码按SHA固定。OFF的额外别名保护定义了过去不可用/未保证的调用行为，不声称对重叠非法输入与旧未定义行为逐字相同。

## 已执行验证

- OFF基本用例先红后绿；ON六个cos15/cos30仿射恢复用例先红后绿。target11项：6恢复+pitch20/32两个保留接受，三个δ/p=.10边界拒绝。拒绝阈值未放松。
- 70冻结图+408旧质量合同分别运行最终OFF、ON；精确逐图像素SHA与结果见`regression/`。完整200ROI的语义与归档V3中央crop不同：不得套用V3旧254接受数作为本候选分母。
- 默认宏完全省略时单独重编译，四个冻结输入与原active状态/68B输出一致；不是仅手动设置0。
- 普通native与ASan+UBSan六配置（OFF64、ON64、ONcap1，各两种构建）全部通过。实际workspace前后、result前后和input前后canary；input不改、失败result不改、alias/range拒绝；真实65seed及cap1第2seed均AMBIGUOUS且0refinement。**LeakSanitizer关闭，未做LSan/SDK/设备/实时性能测试。**
- 普通host ABI：workspace23424B=21888core+1536seed，result68B。不是V3continuous的32640B/192B，也不能据此推定ESP32内存/栈/功耗已达标。调用者应使用独占arena，不建议未知task栈上分配。

## 最终结果（两种构建各exit0）

|输入集|OFF正确/违规/拒绝|ON正确/违规/拒绝|
|---|---|---|
|冻结70局部码图|22 / 0 / 48|31 / 0 / 39|
|340连续纸图|0 / 0 / 340|0 / 0 / 340|
|68对抗图|1 / 0 / 67|1 / 0 / 67|
|合计478|23 / 0 / 455|32 / 0 / 446|

OFF与原active的478状态和全部OptResult字节一致；ON恢复9个原拒绝局部例，未丢掉该70集原正例。全部50显式must_reject仍拒绝，408再生像素SHA全匹配。只有非冲突双窗口case66在68集中接受。

本接口只返回OptResult，不带完整平移/pose变换；本回归的“正确”绑定36符号一致、后验完整点包围框支持及禁止负例门，**不声称重做原V3完整transform-error验收或物理坐标准确度**。普通O2host时长不是targetFPS。

## 不解决的问题

这是正交量化细化，不是一般透视解码。完整200连续纸图会因原有点数上限、边缘/形状等整ROI门被拒绝；不能为了通过改成偷偷裁切、放宽门或删掉笔迹。有限无噪声局部码图改善不说明近笔尖实拍/连续纸/BLE/笔迹链可用。

没有mapper、相机标定、provider注册或轨迹补点。调用失败必须保留GAP，不能插值跨未资格化缺口、沿用旧坐标或改时间戳。若后续研究需要ROI选择，必须独立保留输入质量证据和完整窗口合同，不能重复V4的crop外负例丢失。

## 重现

先校验`MANIFEST.json`和`DEPENDENCIES.json`，保持相对源码布局。在新可写副本执行：

```sh
python -m unittest -v
python check_default.py
python run_native.py
python regression/run.py --enabled 0
python regression/run.py --enabled 1
```

构建临时共享库，不把编译产物带入冻结包；普通host`cc`、Python、NumPy和已有公开源为依赖。报告退出码和每组结果，不把中间旧构建输出冒充最终代码。`verification/`红测保留预期失败，最终gate不能把红测exit1计成未解决回归。
