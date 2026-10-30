# r22 IMU供电、J107与EXTCLK联合研究归档

**仅本地暂存，NOFAB/NOPOWER，不可制板或上电。** 正式历史9a03未替换。当前d6c913全DRC0/120/0、exit5，ERC0错误/1旧警告；AON35/39、GND68/102、SENS12/12，全部14个IMU供电/地pad入相应核心。仍有120未连、49网，分类是实际组件证据而非路由批准。

只收0333失败方案、0341小孔对照、0345失败通道、0357联合方案、0405原生候选、0416独审和0416恢复索引。完整失败病例留作REJECTED，不用小孔掩盖实际跨层冲突。旧789铜去除一条EXTCLK、增33，共821；仅J107 B(3.2,84)→(5.2,84)，其余101实体不变。R503保持47k和RC0603FR-0747KL。

EXTCLK的U203.13↔J202.18连通，R235.1仍隔离；11.9mm投影未增长不代表时序/串扰/阻抗/电气回流合格。精确native孔轮廓覆盖检查从实际新clock投影开始，不先扣理想圆；仅扣精确孔轮廓后残余0，不扩圆消除sliver。

撤销33、恢复旧线和J107的raw rollback不是原始6902字节；它等于序列化/填充后的父板。差异仅R503 MPN格式/字段顺序；显式恢复原格式后才回到原SHA。保留raw、normalized与format-restored三类证据，绝不宣称raw exact parent。

IMU孔与courtyard重叠0.0292143mm²、MEMS应力/装配、动态clock、旧MCU短逃线/EP孔、外部SENS时序反灌、压力GPIO2采集、未知相机、充电电池与实测仍未资格。JP301 OPEN。机械仅源关联/名义预算，不声称整笔机械重算。恢复索引中pressure7、IMU control7、OE7、J1073、MCU DVP24为实际未连分类，不是可制作批准。

SOURCE_AND_DEPENDENCY_MAP.json记录精确清单与依赖。旧r21并集8579项不改；uploader现在独立ACTIVE，其plan/state合法变化不参与本批冻结断言，本工作不读取/写入这些文件或checkout，不执行远端操作。
