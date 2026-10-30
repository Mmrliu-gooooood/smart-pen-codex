# r24 IMU控制链冻结快照

**仅本地暂存，NOFAB/NOPOWER，不可制板或上电。** 当前5ed5f0ad全DRC0/106/0、exit5，ERC0错误/1旧警告；AON38/39、GND70/102、SENS12/12。仍有1个AON域pad和32个GND域pad未到相应核心，不等于仅剩这些整板未连。正式历史9a03未替换。

仅收0444初始尝试、0456围栏范围、原始0505完整模型19项、0515可视路径模型、0522原生候选和0543独审。849旧铜替换3条AON、增137（13孔），共983；源/FP/pad/值/规则未改。R503保持47k/RC0603FR-0747KL；R501/R502仍10k。SCL GPIO5、SDA GPIO6、IRQ GPIO1/INT1，名字PICKUP_INT_N不等于硬件已配置低有效。

**不可隐藏新增clock参考退化：原EXTCLK在In2、In4各新增0.0017414094705mm²投影缺口**，bbox(4.175,80.068649,.15,.107654)mm。实际native填充推翻模型零损预测，不扣成允许own-hole、不四舍五入为零。IRQ与旧clock孔合并，IRQ最近核心GND孔距3.779302mm，不证明回流合格。

AON .25mm侵蚀后主759.077146217768mm²及小.0058354382355mm²岛：两组件不证明主干断开，也不代表供电合格。MCU SDA处7孔合并bbox(.8845,9.1245,3.866,11.326)，MEMS侧AON/SDA孔合并；不能视为独立理想圆。53条<.1mm短段仍在，13孔pad-clear不代表布局优雅或制造/SI合格。

旧压力链、IMU14供电pad、19完整网/12DVP及clock连接保留；真实十类切断/回滚、前向再生证据核验。真实raw回滚为69d93e父板，不需格式修复。时序、10k总线RC/长线、IRQ默认push-pull高有效不锁存、固件provider-null、压力寿命/ESD/去抖与B52/B70.5映射、U203下孔、courtyard、EP孔、JP301 OPEN及未知相机/充电电池全部未资格。

截止仅这六份冻结包；排除active未冻结V4 decoder及其他新工作。SOURCE_AND_DEPENDENCY_MAP.json为精确源/依赖/支持overlay。旧r23并集9866项不改，不访问24批active uploader的plan/state/checkout，无远端写入。LOCAL_PUBLICATION_STATUS.json提供仅本地当前状态和仓库内精确入口。

复验补入单项只读依赖board_provider_absent.c（94字节、SHA256 4af628e878e51a7088b1b330e4cd5c4f00c84cf96c507eb93dee7fbac42adf77），与冻结physical.json观测一致，内容仅返回0。不是收录active应用/V4目录，不包含其头文件或编译产物。首轮缺依赖草稿独立保留在发布包外，干净重建后重新完整复验。
