# r17 translator局部供电域归档

**仅本地暂存，NOFAB/NOPOWER，不能制板或上电，不是整笔成品。** 正式历史9a03未被替换。当前7c816研究板完整DRC0/149/0、exit5，AON23/39与GND57/102物理pad到核心，SENS外部输入仍仅1/12，四个局部旁路岛不等于全参考电源树。

本批仅收translator_domain_candidate_0130、对应独审0149和只读sens_tree_plan_0149。C207/C208只交换物理位置，原ref/pad UUID/网络身份不互换；U201–203 VCCA=AON/VCCB=SENS，U204 TCA VCCB=AON/VCCA=SENS。实际embedded符号与原生网络为依据，PAD.GetPinFunction为空不能推断无功能或正确电源。J202.23为设计合同的外部输入，原符号passive不是本机1.8V输出。

SENS只读规划的两个完整树方案全部因有限铜距碰撞拒绝，未保存为新板，不能将概念连通当实际完成。当前active joint SENS修正不属于本批。

冻结原件、失败日志及独审证据逐字节保存；独审执行副本由作者清单精确overlay复建。所有以前的制造限制仍开放，包括八个EP焊盘内孔、移位孔23.8µm名义EP边间隙、真实焊接/有效电容/回流与时序。JP301保持OPEN，未知30针相机隔离，不擅连接或上电。

SOURCE_AND_DEPENDENCY_MAP.json提供精确路径重建。旧r16并集7188项保持，24批上传计划、状态与checkout不改，本批无远端写入。
