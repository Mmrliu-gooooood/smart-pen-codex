# 点阵纸/光学筛查与完整ROI正交细化：受审软件研究

**默认关闭、未接入活动固件，NOFAB / NOPOWER。** 不更换已归档7522静态PCB、不采用V4、不冻结相机/镜头/最终纸参数。全部新增图像为合成测试图（PGM及汇总PNG）；不包含用户实拍照片/PDF。

## 已执行与未证明

- 参数筛查7200组合是几何/proxy筛选，不是解码通过率；active C在70合成图上22正确/0错误/48拒绝。
- 既有V3裁切比较70图29/0/41，9恢复但2丢失；旧408为254/0/154。不能整体采用其96/80裁切来绕开完整ROI质量门。
- 新隔离candidate在相同完整输入上复用未改动的active cold与V3正交细化源码，编译符号隔离。默认OFF；不改生产provider、活动构建或采集链。478图OFF23正确/0违规/455拒绝且保持active相等；ON32/0/446。70探针22→31正确，9恢复、0丢失；340连续纸图仍全拒绝，不是连续纸支持或物理笔尖验收。
- 作者70探针只检坐标/符号；投影全点方形支持属于独立新增证据。历史408另有全ROI支持/必须拒绝门，但不等同旧V3完整变换误差合同。两份勘误优先于旧报告过宽文字。sizeof/ABI不等于内存边界证明；guard/sanitizer只能按各自实际执行范围报告。
- 最终镜头、距离、点距、点径、码制、真实倾角/运动/遮挡、时序和IR材料仍需联合验证。拒绝保持GAP，不插值伪造轨迹。

## 直接阅读源码与独审

- [orthogonal_refine_fullroi_candidate_20261031_1806/README_ZH.md](workspace/orthogonal_refine_fullroi_candidate_20261031_1806/README_ZH.md)
- [orthogonal_refine_fullroi_candidate_20261031_1806/candidate.c](workspace/independent_fullroi_review_20261031_1809/candidate.c)
- [orthogonal_refine_fullroi_candidate_20261031_1806/candidate.h](workspace/independent_fullroi_review_20261031_1809/candidate.h)
- [independent_fullroi_review_20261031_1809/REVIEW.md](workspace/independent_fullroi_review_20261031_1809/REVIEW.md)
- [orthogonal_refine_fullroi_erratum_20261031_1812/ERRATUM.md](workspace/orthogonal_refine_fullroi_erratum_20261031_1812/ERRATUM.md)
- [optics_paper_screen_20261031_1752/README_ZH.md](workspace/optics_paper_screen_20261031_1752/README_ZH.md)
- [independent_optics_review_20261031_1759/REVIEW.md](workspace/independent_optics_review_20261031_1759/REVIEW.md)
- [optics_v3_comparison_20261031_1759/README_ZH.md](workspace/optics_v3_comparison_20261031_1759/README_ZH.md)
- [independent_v3_review_20261031_1803/REVIEW.md](workspace/independent_v3_review_20261031_1803/REVIEW.md)
- [optics_v3_comparison_erratum_20261031_1804/ERRATUM.md](workspace/optics_v3_comparison_erratum_20261031_1804/ERRATUM.md)

## 精确去重重建

[SOURCE_MAP.json](SOURCE_MAP.json)绑定451个原始相对路径：210新增唯一内容，130复用既有仓库文件，111为本包相同字节别名。不要把去重子目录直接当完整工程。运行`python3 verification/optics_fullroi_20261031/reconstruct.py /绝对路径/新空目录`校验并恢复。依赖固定公开提交f92911bc；无网络下载或代码自动执行。

在新可写副本按模块README运行检查。冻结的红/绿开发日志属于追溯，不代表当前失败。13portablequick记录只保留其历史证据，不由本包回放脚本宣称重跑完整296-source/132-pixel闭包。
