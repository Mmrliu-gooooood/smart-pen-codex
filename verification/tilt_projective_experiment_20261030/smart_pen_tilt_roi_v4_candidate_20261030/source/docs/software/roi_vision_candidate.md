# ROI优化候选：显式工作区、每帧重验证的warm-start、有限非均匀尺度

此候选从参考版 `a225ed29d68c134228c3683a73f293d5a854cdee` 独立继续；保留 `roi.c/.h` 与其测试不变，不将参考版数据与候选版混为同一次验收。入口是新的 `pen_roi_decode_opt`，实现 `firmware/vision/roi_opt.c/.h`。

## 本次实做

- 调用者持有 `pen_roi_workspace`：**21888字节**，包括8192字节visited位图、固定连通域队列、点/变换/网格数组。每帧不malloc/free，工作区可静态分配或用启动期arena；不要在默认小task栈声明，不能并发复用同一workspace。图像缓冲、工作区、prior和result须是有效、正确对齐、互不重叠的存储。
- 取消原参考版约13KiB函数大栈数组。真实Xtensa编译器报告候选入口368B、candidate256B、phase48B；codec另有axis128B/decode64B等。**这些是编译器单函数帧，不是完整运行时峰值**，libm、SDK、中断栈尚未测量；不得由此宣布任意小task栈安全。
- 可选 `pen_roi_prior` 只保存pitch/angle/y_scale。上一帧参数附近最多27个候选，每次仍从当前图像提点、全点几何检查、完整6×6和section精确码校验。prior不保存旧坐标或旧方向，不能输出预测笔迹。
- warm失败退回有界cold搜索；cold仍失败则拒绝，result保持不变且prior清零。NaN、Inf、非法valid标记或越界参数仅导致丢弃hint并重新获取，不能绕过校验。结果明确记录 `used_warm_start` 和 `candidates`，不靠耗时猜是否走了快速路径。
- cold候选扩为图面旋转−60°..+60°（步长2°）、x pitch8..32px（步长0.5）、y/x比例0.6..1.4（步长0.1），最多26901候选。离散搜索范围不是连续全范围通过保证；cold扩大搜索比参考版更慢，不称其冷启动实时优化。
- 每个保留点必须满足主/次轴偏移门限及一格一观测，多个成功解码窗口及多候选坐标一致性校验保留；无新增误码纠正、缺点补全或置信度猜测。

**warm的额外安全边界：**warm成功后不再运行全域cold，所以“一致性”只涵盖实际搜索的局部候选；远离hint的冲突模型可能漏检。它不与cold全域歧义排除安全等价，不能作为已验收 `VALID` 画线依据。需要全域搜索时传 `prior=NULL`。当前没有全局多解构造覆盖或真实数据证据消除此风险；`used_warm_start`必须在后续集成中保留。

## 与握笔倾角的明确区别

新增模型是“正交两轴、独立尺度”的矩阵 `R(angle) × diag(pitch, pitch*y_scale)`，属于受限仿射子集。它既没有剪切，也没有一般homography投影分母。**图面旋转±60°不等于支持30–60°握笔倾斜。** 在某些理想相机朝向下倾斜可近似轴向压缩，但不能借此宣称握笔透视已支持；真实镜头/安装角/笔尖偏置/纸面曲率均未纳入。

独立测试提供非均匀尺度、大图面旋转、亚像素平移和噪声的正样本。更大透视、剪切、80°旋转和比例0.35是**应拒绝的探针**；记录拒绝不等于已支持。仍无真实SC035 RAW、物理坐标准确度、笔迹或全倾角验收。

## 真实S3编译证据，不是烧录/性能测试

新增 `firmware/vision_idf` 是无硬件动作的compile/link harness；`app_main`仅打印警告并返回，不执行decoder、GPIO、相机、无线、flash或OTA。不应烧录成整笔程序。

使用同一已安装官方ESP-IDF v5.4 (`67c1de1eebe095d554d281952fde63c16ee2dca0`) 与Xtensa GCC14.2.0/esp-14.2.0_20241119，target `esp32s3`，真实vendor headers/libraries完整链接。不是host mock；链接保留 `pen_roi_decode_opt`、`pen_anoto_decode` 和静态workspace，避免未使用代码被GC后的假成功。

```sh
export SDK=/absolute/path/smart_pen_sdk_20261028
export IDF_TOOLS_PATH="$SDK/tools"
. "$SDK/esp-idf/export.sh"
export PATH="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin:$PATH"
cd firmware/vision_idf
idf.py -B "$SDK/build-vision-opt" -D SDKCONFIG="$SDK/vision-opt.config" \
  -D IDF_TARGET=esp32s3 \
  -D CMAKE_MAKE_PROGRAM="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin/ninja" build
```

实际ELF符号、source/binary hash、stack-usage、无heap依赖证据见 `verification/roi_opt_sdk_20261028.json`。SDK日志打印的flash建议**未执行**。该固定SDK版本仅为复现检查点，不是部署安全支持承诺。

当前仍用double/libm；Xtensa对象含软件double运算符号。必须后续目标板测帧时与task high-water，才能决定是否换float/LUT、分级获取或进一步缩小搜索；不能把host的亚毫秒warm时间外推到S3。21888B工作区也不等于完整摄像头/BLE应用的RAM总预算。

## 验证与复现

```sh
python -m unittest discover -s tests -p 'test_roi_opt*.py' -v
python tools/benchmark_roi_opt.py > verification/roi_opt_host_benchmark_20261028.json
python software/verify_host.py --upstream-pc-src /path/to/digital_pen/digital_pen_ov5640/pc/src
cc -std=c11 -g -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined \
  -fno-omit-frame-pointer tests/test_roi_opt_safety.c firmware/vision/roi_opt.c \
  firmware/codec/anoto.c -lm -o /tmp/roi-opt-safety
ASAN_OPTIONS=detect_leaks=0 /tmp/roi-opt-safety tests/fixtures/roi/reference.pgm
```

LSAN因ptrace沙箱限制关闭；不声称泄漏扫描通过。native sanitizer覆盖新opt函数，不借用只测参考版的sanitizer结果。hostgate自动发现新测试，依赖缺失/skip不算成功。

来源与许可仍按参考版 `roi_vision.md`：审阅原PC detector/grid fitter的思想但未照搬全页定位或宣称已移植其homography/spline；codec的原MIT许可全文继续保留于 `firmware/codec/LICENSE.microdots`。
