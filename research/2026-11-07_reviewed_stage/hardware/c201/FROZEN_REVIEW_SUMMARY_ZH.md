# C201 地返回：隔离原生及独立审查冻结

仅新增两段 F.Cu / GND / 0.20 mm：(506.15,66.605)→(504.5,66.605)→(504.5,67.025)。C201.2 接既有 via 792874b9-4a51-47a8-84dc-3769ca2eb5c1 的真实环铜，没有新增孔、via、Mask、移动元件或改变旧AST。候选 native/merged_main_power.kicad_pcb 位于 translator_c201_ground_native_20261107，SHA256 39620767d41fbe387f2c99a9bed91e1e4546e583ddf91ebb34f478a8c9dc10a6。

200元件、795原生pad记录/736正铜UUID、367 tracks、55 via、61孔；逻辑地44→45，Power46另岛，其他691 pad分区不变，565→564分区，369→368未连。C201.1与U201.VCCA仍各为singleton，无实际供电回路或有效去耦资格。三条返回与zone全断后，候选仅为C201.2/C209.2两电容地端浮岛，不能称系统地。

先读作者 REPORT_AUTHOR_ZH.md；独审以 FINAL_README_R2.md、FINAL_MANIFEST_R2.json、ARCHIVE_WHITELIST_R2.txt、SHA256SUMS_FINAL_R2.txt 为最终权威，REPORT_ZH.md是未变的完整工程报告。R2仅补两份P5KS实际footprint依赖，旧R1元数据和失败证据全部保留；不要采用报告末尾仍提及的R1清单作为最新归档依据。

完整6Cu图、普通/-O、真实native删线/fresh-fill和保存后读回均已完成：37命名场景实际35种不同场景，13命名切源组中有12唯一切集；294继承graph cuts加新增4cuts，不冒称294次新原生保存。6保存负控均无自动网重标。错B层碰C503.1的3V3_AON；末段0.10mm仅相切不导通；深入孔虽图仍连通且CLI不新增错误，实际侵孔0.00453311754mm²而被严格拒绝。

正式环铜正面积约0.00531262569815mm²，钻孔交面积严格0、孔净距约0.075mm；只允许指定目标环铜近孔例外。自身实际实体减真实GND pad残量、新曝铜均严格0。完整217保存实体、764Mask、61孔、200庭院及802原图/916有限宽笔画已审查；保守BBox、真实轮廓、笔画及实体区分，不缩体放行。不是安装/加工公差资格。

37份完整DRC原始JSON/控制native字节与其SHA均保留。源与候选仍8旧warning、2旧parity，不称DRC全绿。同一via切除两别名的PCB字节和全图相同，但airwire代表source5条/candidate10条变化；全部UUID绑定物理组件后371条组件对多重集相同，完整差异保留。独审另跑CLI的source9/candidate6条代表替换同样核全组件对，没有只比计数。

作者normal1412/-O1376项，共同工程1340项一致；36项差异只因首次生成36个控制归档需72次检查、复核既有归档需36次。机械2624、annulus77、DRC25595均各两模式；独审电气29177、DRC45901各两模式，另有全机械、笔画、1nm残量负控与别名专项。所有首次失败、修正版本和唯一证据保留。

普通ZIP仅收两最终manifest精确列明常规文件及对应自身清单、协调文件和3份stage说明/入口。所有symlink只保存元数据，禁止自动跟随；进程FD链接不当持久恢复源。工程复现仍需SOURCE_PREREQUISITES列明的外部输入/原路径与project companions；同字节别名不等于原路径已恢复。保留的runtime配置/缓存不是工程资格，独审明确排除的可重建缓存仍留磁盘。厂家原始PDF、未列源树与活动后继排除。默认 verify_bundle.py 只读核归档字节，不执行工程、不改回执；--check-local才额外核本地路径。工程脚本只在新的隔离目录重现，不覆盖本冻结阶段。

全部NOFAB/NOPOWER，commission OPEN；qualification/current_rating_A/effective_C null，JP201/JP1951仍DNP/OPEN。真实馈电、OE默认禁用、ground-first、欠压/部分供电、相机兼容、额定电流和制造均未完成，本阶段不代表整体任务完成。
