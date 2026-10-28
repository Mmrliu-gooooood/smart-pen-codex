# 小视场灰度点阵获取：可运行实验实现，不是实物验收

## 本次补齐什么

`firmware/vision/roi.c` / `roi.h` 从 **真实输入形式 Gray8 像素**开始，调用者仅提供缓冲区长度、宽高、stride，以及纸张矩阵尺寸和 section。调用者不提供点坐标、cell坐标、网格起点、pitch、角度或正确答案。旧 `canonical.c` 保留为已对齐窗口的历史单元测试，不冒充采集算法。

处理链：

1. 读取灰度动态范围，低于60拒绝；中点阈值，8邻域连通域，灰度权重质心。对过大、长条、触边、过多组件拒绝；<3像素孤立噪点忽略。
2. 搜索8–32像素pitch（0.25步长）和相对纸张正方向−20°到+20°旋转（1°步长）。周期圆均值估计两轴相位、迭代消除方向分布偏差，不依赖全页或已知cell原点。
3. 全部保留点需满足一格一观测、偏移主轴0.10–0.30格、次轴≤0.065格；不补点、不猜遮挡、不预测墨迹。
4. 枚举完整6×6候选，现有MIT `pen_anoto_decode` 精确验证section、纸张边界和编码序列；多个窗口必须具有一致坐标平移，多网格候选不得给出相互冲突的原点。
5. 返回已解码**窗口起点**、检测点数、通过窗口数、搜索网格参数和几何残差。不是笔尖坐标，不是质量概率，更不是 `VALID` 笔迹包。失败时整个输出结构不变。

## 硬边界与尚未支持

- ROI 16–256像素宽高，最多128个点；通常至少36个完整清晰独立圆点。只有6×6的ROI缺任意一点都会拒绝。更大ROI可使用其他完整窗口，但不补失点。
- 当前是近似正交、同尺度两轴的方格模型，不是透视/仿射求解器。轻微透视只有残差仍过门限且精确码校验时可能成功；大透视、非均匀尺度、弯曲纸、镜像、90°/180°象限未知不承诺支持。
- 主要验证原generator默认pitch/6偏移；较大偏移有探针，但不能据此宣称支持所有纸型。
- 阈值为全ROI动态范围中点，不是局部自适应曝光；渐变阴影、失焦、点融合、墨水遮挡、饱和、欠采样、传感器坏点需真实RAW后另行验证。没有用主观“置信度”补偿图像缺证。
- 仅C11/libm，动态工作区最大65536字节（visited）另有固定栈数组；分配失败显式返回。搜索是有界host参考实现，但耗时不适合作为已证实时性能指标。宿主GCC `-O2 -fstack-usage`显示 `pen_roi_decode` 本体13168字节（dynamic,bounded），另有被调函数开销；这不是Xtensa结果，不能直接放入ESP-IDF默认小栈任务。ESP32栈/RAM预算与性能仍需目标编译、测量与优化。
- 未接入sensor驱动；没有把SC031寄存器挪作SC035。没有镜头/曝光/倾角/真实笔尖标定结果；没有宣称实物精度、帧率、全倾角过关。上层接入前必须将窗口坐标经已验证几何、压力接触和时序门控转换，失败不能画线。

## 实际源检查点与许可

原项目 `Mmrliu-gooooood/digital_pen` HEAD `0f8b569176c77dad34aaf83bb008eb118c9f1208`：

- `digital_pen_ov5640/pc/src/digital_pen/vision/dot_detector.py`：加权质心、候选面积/形状/光学拒绝；原实现OpenCV轮廓、复杂消融去混叠，不直接嵌入本C。
- 同目录 `grid_fitter.py`：周期相位估计、邻域基轴、残差索引；原实现另有homography/spline和全页大点集支持。小ROI不照搬全页邻域统计；本实现独立有界pitch/angle搜索 + 圆均值相位。
- 同目录 `direction_classifier.py`：反投影后按主轴方向分类；本C增加每点主/次轴门限、唯一cell归属、完整窗/精确码验证。
- `digital_pen_ov5640/tools/patterns/generator_adapter.py`、`点阵笔资料/py_microdots_develop/microdots`：用于独立生成编码真值。测试光栅器不调用C decoder或给decoder传网格答案。
- MIT `Copyright (c) 2022 Christoph Heindl` 原全文保留在 `firmware/codec/LICENSE.microdots`。该许可适用于保留的py-microdots派生编码器序列/算法；不把整个无独立许可证的PC应用误称MIT移植。

## 复现

```sh
python -m unittest discover -s tests -p 'test_roi*.py' -v
# 已有完整hostgate自动发现新ROI测试，缺依赖/跳过不算通过：
python software/verify_host.py --upstream-pc-src /path/to/digital_pen/digital_pen_ov5640/pc/src
# 原编码器独立重生成并比对冻结真值：
python tools/verify_roi_fixture_source.py --help
```

fixture renderer采用独立4×4亚像素抗锯齿圆点、逆homography、确定性随机噪声。保存的PGM与参数见 `tests/fixtures/roi/`；全部为合成，绝非相机RAW。`tests/test_roi_consensus.py`另有原generator生成7×7/49点、4重叠窗口坐标一致性验证。

测试与本机时间结果见 `verification/roi_vision_20261028.json`。host速度仅记录C调用（不含renderer），不能外推ESP32速度；sanitizer的LSAN若受沙箱限制会明确排除，不声称泄漏扫描通过。
