# 保守 GND 分支恢复独立复查

结论：限定研究块的静态复查通过；**仍 NOFAB，不得上电，不提升为完整产品或正式 9a03 电气后继**。

## 输入与结果

原件 gnd_conservative_recovery_2305 的103文件清单及214依赖逐项大小/SHA256前后核验未变。目标PCB ead39fa832de2aabff4fbec9ce67d12199094ac9d77e700de54920d8fec86959。

独立新目录保留同basename原理图、项目与规则，执行 kicad-cli pcb drc --format json --all-track-errors --schematic-parity --severity-all --exit-code-violations：0违规 / 203未连 / 0 parity，退出5。没有屏蔽未连或新增排除规则。作者 materialize 从fd989与原9a03完整对象重放，生成同SHA；新重填不依赖旧2159失败板作为基线。

## 独立几何与反例

independent.py 独立构造有限铜邻接图，使用实际 IsOnLayer 与physical-pad UUID区分重复焊盘；铜多边形最大近似误差100nm，via钻孔用512边多边形扣除。normal与-O均确认：

- 534原铜对象精确保留，96新增对象逐UUID、网、坐标、层集合、线宽及钻孔与原9a03一致。
- 17个完整GND子图均真实接J106.3核心；逐组删除该组全部对象后，其目标pad均不再接核心。
- GND physical pad到核心30/102，仍72未接；AON仅1/39，仍38未接。
- 原理图、.pro、.dru与fd989逐字节相同。

作者 analyze.py 新计算normal/-O一致，102实体/366pad/源保持，14链及19网保持，参考投影未变；不是只读取旧analysis.json冒充重跑。

另独立选group0、23、48制作真实原生删组副本，分别得到0/204/0、0/206/0、0/204/0（均退出5），未连报告包含相应目标终端。删全部96对象并freshfill精确回fd989bf844a8bc224f315dd3d2559d7a55ae1ba8f9384b0c06b6e301b6668454及0/231/0。

## AON与返回面边界

planes.py从三个实际原生板重提取填铜：基线、被拒18组、当前17组的0.25mm侵蚀分片分别7、8、7。被拒版→当前版精确仅减少group37的14对象；当前7片与基线7片逐一对应。四个GND plane的完整填充几何字符串与fd989相同，不仅面积相等。

当前AON填铜较fd989减少8.7967521655mm²。等分片数量和逐一映射**不是**最小全路径宽度、载流/热、PI或电磁兼容证明。group37 C207.2/U204.4仍未连；不能因为小碎片没有pad中心就断言它不承载电流。全部17组移除的有限铜反例已复跑；18个带项目绑定的历史fresh-fill对照作为冻结证据核验，本独审未再逐一重做18次原生填充。

JP301保持OPEN；未进行采购、上电、刷写、制造、发布。后续需完成剩余供电/地与信号、完整机电与实际工艺/测量验证。

## 工具失败的处理

初次独立删组试验使用pcbnew.Remove对象API导致子进程段错误（退出139），仅影响可丢弃副本，保留REJECTED_remove_api.py/log，未计通过。最终native_negatives.py按精确UUID从独立副本删块，再fresh load/fill/save，并以真实CLI核验。未改变任何冻结原件。

## 再现与归档边界

本目录清单仅包括审查源码、结果、日志与报告，不含作者整树复制件或临时原生负例副本。独立脚本需同hardware根下的原作者包、aon_entry_bridge_candidate_2156、j202_low_speed_reference_candidate及gnd_fixed_branch_candidate_2159（仅planes比较用）；作者重跑需复建gnd_conservative_review_work_2317为作者103文件逐字复制并保留其dependencies.json的相对依赖。input_integrity.json与final_integrity.json记录清单身份。缺任何依赖时应报告不能重跑，不推断成功。
