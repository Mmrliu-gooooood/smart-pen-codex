# r23 压力七链路与独立DFM研究归档

**仅本地暂存，NOFAB/NOPOWER，不可制板或上电。** 当前69d93e全DRC0/113/0、exit5，ERC0错误/1旧警告；AON36/39、GND70/102、SENS12/12。正式历史9a03未替换，整笔远未完成。

仅收0425拒绝方案、0429联合拓扑、0433原生候选、0436 U203封装下过孔独审和0441独审。821旧铜去除4条STRAP escape、增32，共849；其余817对象保持，102实体/366pad位置、源和mask规则不变。R503仍47k/RC0603FR-0747KL；U101物理7=GPIO2，不是GPIO7；STRAP物理8=GPIO3。真实六类切断与回滚证据保留；本版raw回滚等于d6c913父板，不需前阶段的格式修复。

**强制参考边界：NIB MCU近端实际native孔为BOOT_N旧孔与NIB新孔合并，1.341×.951mm；远端.751×.751mm。精确实际端孔轮廓扣除后残余0不是两颗独立理想圆、不是完整SI/回流资格，不能扩大圆吞掉缺口。** 长NIB53.2674mm、CONTACT2.5464mm；47µs/约.979µs名义RC不含寄生且不是去抖。

U203实际Value SN74AXC4T245PWR、独立MPN字段未指定；PW是TSSOP而非BQB/QFN，无指定中央外露热焊盘，不等于内部没有引线框架。孔(5.4,55)在塑封体下，两面规则tenting不等于填孔，也不证明Gerber/注册/针孔/残留/焊接工艺；R222 B courtyard与U101 courtyard相交仍未资格。不得由DRC0作制造豁免。

压力铜连通不解决实际AON≥3V条件、50k次额定寿命、触点机构、ESD/噪声/去抖、provider-null固件、R504远离C504、J103 B52与虚拟B70.5。JP301 OPEN、未知相机/充电电池以及旧EP孔/短逃线/IMU应力/clock动态全部继续NOPOWER。

旧r22并集9149项逐项只读核验，无改动；本轮不访问active uploader的24批plan/state/checkout，无远端操作。只冻结清单及指定依赖，不收活动IMU控制布线。

可移植复建补齐明确间接依赖：physical.py经0333 geometry读取0318历史native，按既有清单保留；独审chains.py来自0405，SOURCE_AND_DEPENDENCY_MAP.json的support_copies单文件overlay记录该来源。初次缺依赖/overlay与manifest字典形状草稿留在发布包之外，不作为板级失败或完成证据；从干净隔离目录重跑，不改冻结源。
