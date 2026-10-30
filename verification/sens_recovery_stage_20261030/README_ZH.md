# r18 外部SENS参考树研究归档

**仅本地暂存，NOFAB/NOPOWER，不能制板或上电，不是整笔成品。** 正式历史9a03未被替换。当前ca66研究板完整DRC0/143/0、exit5，SENS12/12、AON23/39、GND57/102物理pad到各自核心，仍有143未连。

本批只收sens_joint_plan_0155、sens_tree_candidate_0158、独审0202和本阶段冻结恢复分类。37个新增对象(30条0.25mm线、7颗0.60/0.30mm孔)连接外部参考树，全部736旧铜/102实体保持。SENS输入来源仍为J202.23设计合同，不是本机稳压器。

实际pullup电源端为R242.2/R243.2，不是.1；R242.1=SENS_SCL、R243.1=SENS_SDA。以embedded实际源符号和原生网络为准，不能从空PAD.GetPinFunction猜身份。U201–203 AXC VCCB=SENS，U204 TCA VCCA=SENS。

几何连通不证明外部1.8V参考源的载流/启动/时序/爬升/掉电反灌能力，也不证明未知相机的电平。JP301保持OPEN，未知30针相机隔离。原八个MCU EP孔in-pad和23.8µm名义EP孔边余量仍未取得填孔/阻焊/焊料/注册误差工艺资格。

冻结原件、失败源引脚假设日志及独审证据逐字节保留；独审执行副本由作者清单overlay复建。SOURCE_AND_DEPENDENCY_MAP.json提供精确来源路径。当前active后续修改不收录。旧r17并集7373项保持，24批上传计划、状态与checkout不改，本批无远端写入。
