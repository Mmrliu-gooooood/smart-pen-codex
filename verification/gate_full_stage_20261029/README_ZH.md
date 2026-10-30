# r11：508e完整gate静态铜块与联合机械复筛

**仅本地备份；NOFAB，禁止据此投板、上电或接未知相机。** “完整gate”是本轮声明的静态源/铜连接范围，不是安全电源门、完整笔或动态试验完成。原r4–r10不改，不收正在变化的CAM_ON平滑试验、四壳CAD或其他移动目录。

## 冻结范围

7个manifest全部成员原样：gate候选100、独审114、共线维护筛9、测试访问门3、剩余计划2、508e联合机械9、夹持铜边界6，另各自manifest，共**250原件**。所选PCB SHA256 `508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35`。

候选清单 `70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52`；独审 `7a4cf7947aa19dbc9954271f0445b74ca06008631a3366805844f586cb65b36f`。完整其它pin和来源映射见r11总manifest及`SOURCE_SUBSET_SHA256.json`。本批不包含任何PDF、INI、厂商照片、设备数据、私密配置或未知软件。FCStd为自有已知设计，检查了ZIP成员/无FeaturePython或Proxy；这不是一般文件安全证明。

## 准确复用r10，而非再复制旧历史

`DEPENDENCY_LINKS.json`精确列322项（8,967,302字节）：原gate输入87+manifest、原输入独审78+manifest、真实native-MPN源152+manifest，以及RevC/RevD各1份冻结CAD。它们保持在r10或已组装repo中；本批不重复归档。当前独审source_rules需要完整87/152成员，候选另pin旧独审；没有递归执行旧祖先builder，也没有收整个机械历史树。

默认quick仅校验本批250原件和既有28/41/0、9short证据，自包含、仅Python标准库：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 portable_check.py
```

原生重放需已安装KiCad9.0.2 CLI/pcbnew/标准库、FreeCAD1.0/Part及对应系统Python。无安装或下载：

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 portable_check.py --native --mechanical
# 不同本地布局可显式指定r10实验根，不是原workspace路径：
/usr/bin/python3 portable_check.py --native --mechanical --dependency-root /your/local/path/hardware_mechanical_stage_20261029
```

脚本可定位相邻已组装实验目录或本地r10增量包。全部输入先按hash核验，再仅将322项依赖与本批源物化到随机临时目录，保留两个项目同层相对布局。原脚本有输出副作用，**不得直接在冻结包运行它们**；helper的guard板、重填板、新CAD和JSON只留临时目录。XDG为可写临时目录，部分原脚本仍使用其明示`/tmp`配置，不需要个人配置。

### 本次实际重放与比较边界

- source_rules、独立实际六层铜audit、主供细支路删除反事实、输出隔离、几何/RF风险、平面岛连接、规则区：正常/-O；另量测与QOD物理分支、删除主桥的2模式负例。
- fresh refill后再次实际audit；从原ae805+显式delta重新生成并audit，**原始序列化hash不是等价判据**。不因为hash不同就忽略铜/焊盘/拓扑差异；显式几何与连接结果须匹配。
- 新完整DRC（全部track、severity、schematic-parity）及ERC；共线分类/无修改证明正常/-O；TP节点图核验。七类普通破坏负例完整证据保留为历史，本次最小重放未另全跑，不能把“保留日志”冒称本轮运行。
- 联合mechanical screen及clamp check正常/-O。CAD保存含序列化差异，比较时仅排除`CAD_sha256`字段，数值/碰撞/探针负例均须匹配；冻结交付CAD始终以manifest的最终hash为准。新临时CAD hash单列，不能覆盖交付CAD。
- 主报告为`portable_check_result.json`，归档新helper/hash与原证据分开；没有制造、物理夹持、探针接触、电源负载或动态试验。

## 保留的阻断与不能推导的结论

**原生板仍28违规 / 41未连 / parity0，DRC exit5。9真实short、9mask bridge、4hole-clearance、1clearance、5dangling仍在。** 减少109项、增加2dangling不等于违规清零。JP301仍OPEN/DNP、两岛分离；既有充电JP1保持OPEN。TPS22918不是过流/过充保护保证，未知相机不能接入。

本delta为229旧导体移除、1段明确裁短、1005新增导体（973track+32via）；**669段小于0.10mm**。共线筛仅3对候选且都有真实支接/平面接触保护，**0合法合并、没有新建/修改PCB**。不能从“无合法合并”宣称微段维护问题解决，也不应仅凭短段数推导开短路或总电气长度失败。后继清理必须另冻并重新独审。

六个AON填铜岛都连核心、四个GND岛也连核心，不代表窄颈载流、HF回流、PI/EMI已合格。主桥.50mm/9.816mm与U204.8独立.30mm支路的反事实只是DC拓扑，不是负载/温升资格。CT回地、QOD脉冲热、总CL/有效CIN、启动/关断/IO回灌、器件NRND/精确MPN、材料叠层/制造/预算均有门。

**TP301=CAM_PWR_EN，不是CAM_ON或门后输出。** 节点图不是测试授权。508e联合CAD保留实际1×1矩形铜pad/保守高度；有限平头探针碰PCB的负例必须保留，不能只展示理想尖点可达。探针、接触力、工具身/相邻件、电气操作和装配尚未资格化。

508e仅四个实体C302/R301/R302/TP301位置变化绑定到新的RevC/RevD派生CAD。它仍是有限几何筛，不是最终19mm壳/实体装配。四条.25mm夹持边带对内层铜最小**.05mm名义几何距**、实际fresh-fill轮廓一致，只说明当前几何未侵入；并不证明绝缘、磨损、夹力、板弯、容差、材料、热/疲劳或金属夹持安全。旧5µm/.01mm自定测量目标和物理验证门没有被本次结果取消。

r10及更早的成本直接输入闭合状态继续保留，但本批没有成本重算、采购或改变旧历史设计的选中状态。
