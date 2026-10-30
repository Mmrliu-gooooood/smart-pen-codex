# r25 投影解码实验：明确未采纳

**NOT_ADOPTED / REJECTED_EXPERIMENT，不替换V3，不接入app，不代表实物倾斜资格。** 这是软件诊断归档，不是新硬件版本。

8张理想合成图6正确/2拒绝（60°两张拒绝）；120保留集37正确/83拒绝；旧408回归225正确+3质量合同违规接受+180拒绝。3个edge_stroke坐标正确但墨线在旧96内、新固定80外，被裁掉仍接受，必须保持红灯，不能称错坐标也不能称完全通过。全reproduce.sh预期exit1，唯一失败命令必须是run_regression.py的3违规门；归档正确识别拒绝不是让算法通过。

旧85host、44cold/12warm不变；独立39坏数/退化检查ASan+UBSan通过不代表LSan或所有浮点形式证明。workspace36480B是host ABI，不是SDK栈/FPS。真正圆周支持余量约.497px，不把保守方形角越界称错码。

200原像素=6mm对应同倍率640=19.2mm，非全VGA6mm；V2是stride640零拷贝裁切，不缩放。全640=6mm时80像素仅.75mm，无法装下完整6×6点窗。f400px/Z12mm/.3mm只是针孔合成假设，非镜头测量，光轴角不等于握笔角、网格非笔尖。

V4原462项逐哈希纳入或精确复用，完整394旧V3源通过别名重建。其旧CAD和五份review PDF是项目自生成历史输出，不是厂商原件，也不表示这些旧板取代r24。唯一排除的登记文件是独审numerical_review host ELF（493624B）；保留C源码和精确排除记录，可自行重编。私有厂商PDF/实拍照片、未列目录和build产物不收。原manifest逐字节保留，不伪造其覆盖范围。

reconstruct.py仅按源映射复制，不执行代码；可复建同级candidate、394旧V3、光学合成图、44旧图及上游PC Python依赖，并生成独审运行副本。运行仍需已安装numpy/opencv/fastapi/httpx/uvicorn/bleak与C编译器；原reproduce.sh不改，不跳394门。HOST_PYTHON和PYTHON指向符合依赖的解释器后，完整执行必须保持真实exit1和3违规。没有把缺依赖异常冒充预期红灯。所有复验新输出独立保存，冻结源不改。

旧r24并集10861项保持。硬件最新状态仍以r24为准且NOFAB/NOPOWER。本阶段不访问active uploader的plan/state/checkout，无远端操作。

## 原样复现入口

在组装后的仓库中运行本目录`reconstruct.py --repo-root /path/to/repo --output /tmp/r25-workspace`（输出目录必须不存在）。然后进入`/tmp/r25-workspace/smart_pen_tilt_v4_review_run_20261030`，设置`PYTHON`及`HOST_PYTHON`为已安装上述依赖的同一个绝对解释器路径，执行`bash reproduce.sh`。此命令应实际返回1；检查日志唯一`EXIT 1`来自`run_regression.py`，85项旧host为0 skip。不能用缺模块、缺文件或sanitizer失败凑出同样出口。

本次隔离完整执行满足上述条件，8份结果仅剔除host时间字段后与冻结结果完全一致；另行重建公开映射确认candidate465个实际文件和旧V3 394项全匹配。详见`reproduced_acceptance_boundary.json`及完整日志。唯一排除文件位于独审清单，不在V3 394或V4 462；原复现脚本无需跳过任何源码冻结门。
