# r10：当前稳定硬件输入门与机械台架（本地备份）

**NOFAB / NO POWER-ON RELEASE / NOT A FINISHED PEN。** 这里只归档已冻结输入门PCB、其完整原生源与独审，以及已冻结RevC短线机构/RevD共基准台架。正在变化的完整gate路由没有收录；不覆盖旧repo主设计或r4–r9，不提交/推送，不制造/采购/操作设备。

## 收集范围与来源完整性

1. 当前gate审核最小闭包：`gate_input_local_routing`87项、`gate_input_independent_review`78项、`imu_compact_0402_placement`96项、`gate_supply_native_mpn_source`152项，**413项+四个manifest均完整**。原独审逐项校验这四包，故不能只收PCB却声称独审原脚本可跑。完整sheet、same-basename project/custom rules、实际本地symbol/footprint库、fresh XML/BOM及配置证据均保留。作者确认见`smart_pen_next_20261028/docs/electronics/gate_input_release_dependencies/`。
2. RevC源manifest列30项，交付保留28项，排除1份FCBak、1份会话prl；RevD源manifest列93项，交付92项，排除1份FCBak。两份原manifest原样保留作来源证据；**这些机械源清单不是交付目录可全项校验的清单**，应使用本目录`SOURCE_SUBSET_SHA256.json`。保留生成FCStd/参考STEP/预览PNG和几何审计，不把STEP当制造图。
3. RevB仅取实际负例需要的FCStd，及README/terminal_handoff/sources/原manifest说明边界，不收整个祖先树。FCStd按ZIP检查，未发现脚本成员、FeaturePython/Proxy对象；只运行已审自有脚本、打开这些已知设计，不运行未知外来程序。
4. 原厂PDF和原厂页图不随包；保留官方URL、作者摘要、原文件hash和明确省略清单。没有厂商私密PDF/INI、相机照片/原固件、个人资料。可见PNG均为自有CAD生成图。
5. C503旧BOM指向后来变化的README路径：原hash `08ce8577…5fa`对应已冻 `imu_decoupling_c503_source_fix/manufacturer_basis_snapshot.md`，不是当前更正README；两版本分别保留并有机器映射。不能将旧hash硬指向新文本。MPN均为未获采购/PI/装配批准的候选。

## 最小离线检查与原生复核

默认仅标准库，校验全部所选原件、413项原审核闭包、外部文本出处及历史102实体/356端点、135/54/0记录：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 portable_check.py
```

完整当前审核复核需要已安装**KiCad 9.0.2 CLI + 对应pcbnew和标准库**、**FreeCAD 1.0/Part**（本环境库路径`/usr/lib/freecad-python3/lib`）；系统Python须能导入这些库。不会下载安装。以实际具备这些模块的Python运行：

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 portable_check.py --native --mechanical
# 两部分也可分开：--native 或 --mechanical
```

helper把选定两项目目录复制到随机临时目录，配置可写XDG目录，再执行原审核与负例。原文件不追改；输出、破坏性负例板、FreeCAD重导STEP、会话文件均不进归档。部分原脚本沿用`/tmp/rf-independent`配置路径；仍不读取用户私密配置。临时副本中仅将RevD `native_contract.json`的历史绝对source路径绑定到**相同ae805哈希**的包内PCB，原/派生JSON hash、改变字段列入新报告。不要求读者有原workspace路径。

native复核包括原source_rules、measure/binding、独立真实铜多边形audit、5种配置负例，正常/-O；7种铜/网/MEMS/OPEN破坏×正常/-O；完整原生DRC及ERC。wrong_C301_pad负例在KiCad重存时可能使相连铜改网，冻结audit遍历无序set，所以首报UUID不确定。新适配器不是“任何RuntimeError都算过”：严格同一mutation/exit1/serialized-net拒绝类别，且旧/新首报UUID必须属于本次实存板独立解析得到的改网集合；保留本轮与历史错误全文，不称文本逐字相同。

机械复核执行原RevC/RevD `verify.py` 正常/-O：包括旧未切RevB壳碰撞、预装叉座装配失败、原柱触电源预算等负例，以及28插装采样/6工具角点、38台架件及STEP回读。都是有限采样静态几何，非真实装配、连续运动、承力/疲劳/焊接或精度认证。详见本轮`portable_check_result.json`，不能把保留历史报告当成新重跑。

## 明确不包含“从零重建所有祖先”的承诺

- 四硬件包足够当前gate独审和当前native ERC/DRC；不递归执行旧builder。`gate_supply_native_mpn_source/tools/build.py`和其历史差量check仍要0402旧源树；placement旧builder也有更早基线依赖。它们作为来源保留，**不是本闭包的自包含入口**。
- RevD当前build输入为RevC CAD、native_contract和ae805；extract_native另用已附dd55做102封装差量。RevC build输入为已附RevB CAD、context_imu_snapshot和dd55；extract_context另需历史4059板。历史JSON/脚本路径需在新研究副本中显式参数化。
- RevB从零重建还需更早B52.FCStd/上下文；没有因此递归收width14、84/94、wholepen或多版失败树。当前输入CAD和负例已附、可复核，非完整历史生成链包。
- 官方资料闭包生成器`gate_input_release_dependencies/build.py`读取被省略PDF/页图以产生原hash，因此它不是无原资料情况下的重跑入口；本helper直接验证已冻closure里的所选文本和4个当前原生包。

## 不可省略的停止门

**硬件：** 绑定原ae805 PCB（不是fresh重存副本）；135违规 / 54未连 / parity0，DRC exit5，**禁止投板、上电或接未知相机**。输入VIN/GND局部DC连接闭合不等于完整gate；EN/CT/QOD/输出未完成，GND仍15分量，动态/回流/PI未测。JP301保持OPEN/DNP；既有电源充电JP1仍为OPEN/DO NOT BRIDGE，本批没有改变或放行。TPS22918不是过流保护保证。六层.83名义/.93机械边界和未确认材料/叠层/制造门保持；默认Dk不是受控阻抗资格。

**机械：** RevD是50mm宽、118mm长外置台架，不是19mm成品笔壳/自由书写样机。静态零交叠不证明夹力、刚度、热、跌落、焊点疲劳、打印公差或电池安全。38个新增件仍有加工/薄垫/紧固/量测与报价门，不默认免费设备或人工。短线没有服务余量，不能拉线定位。

**计量：** 复用r9独立[计量勘误](../../docs/research/cost_archive_20261029/metrology_target_erratum_0139/README.md)（组装repo相对链接；单独增量包位置见`DEPENDENCY_LINKS.json`）。5µm是自定窄ON窗研究目标，非原厂/非必买；.01mm/轴也是测试目标，不是允许线材应变；.35mm未批准、.25mm也非精度无损承诺。器件回差、实际测法能力与验收窗口仍待实验。

## r9成本直接来源闭合，不冒称旧生成链全闭合

`COST_DEPENDENCY_UPDATE.json`按内容hash映射原26条引用到旧并集或r10文件。r9原缺15引用已全部补齐；额外只取ADC XML、高βNTC README、2356旧build_cad三个精确历史来源，**未运行旧builder、未将旧CAD设计提升为当前选中版本、未递归取其依赖**。全部26个直接来源可恢复，但本轮没有重跑完整BOM提取或价格查询，也没有因此证明≤760元、可采购、充电架构或结构已通过。r9旧清单仍保存当时缺15条的历史状态，不追改。
