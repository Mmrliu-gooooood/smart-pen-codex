# J202 七个地端限定独审

**接受4994作为后继静态布线基线，仍NOFAB。** 不代表24Pin信号布通、DVP返回资格、连接器底部绝缘/装配或完整笔板完成。地via/短引是版本审计对象，不是后续永远禁止调整的布局。

输入 `../j202_ground_return_candidate/manifest.json` SHA `179319e8759f5c4a853279c4a7ca3ad1c244f2f3f8f0dc97774d84841f4a5aac`，106项逐个复核。当前PCB **`4994ba2d8810b2f44434bd43f7cecfaab16aa601a0837c9923883613583554f6`**；基线为已审I²C `6b44e149edf7e3b6c843375125a71247ece6c664eb531686dd3b451e1586ee71`。

## 结果

- 隔离同basename pro/dru及完整条件叠层规则，fresh KiCad9.0.2全量 **17违规/26未连/parity0，exit5**；原17项完整finding multiset不变。ERC **0错误/1既有VBUS边界warning**。制造模式明确拒绝。
- 102封装/356源端点、原生MPN、完整源/库/工程字节与全部规则轮廓/层/禁止flags不变。J202当前24脚身份不变，未改固定焊脚网；1/4/7/10/13/17/24确为源GND。
- 仅增加12段B面0.25mm地线与6个0.60/0.30mm普通通孔；旧铜0删除0修改。有限铜/真实填铜图确认七地脚接原核心，全部旧pad关系不退化，AON6岛/GND4岛仍接核心。新增铜与任何异网实际铜无正面积相交。
- 精确delta重放与独立fresh-fill获得同一PCB SHA，候选原填充逐zone-layer相同。JP301 OPEN及相机隔离保持。

## 本体/孔/阻焊与共享回流

独立核对 [Molex官方SD-503480-001 J1图](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/503/503480/5034802000_sd.pdf)，并查看p1底视/剖面/推荐板图；不从未完整尺寸化的底部金属窗口推导安全绝缘距离。保守Fab框不是公差认证模型。

六新增via原生F/B显式TENTED及IsTented均正确，钻孔不侵入任何实际F/B SMT pad，孔边位于名义body y90边之外，最小仅0.05mm。**不代表制造公差后仍有0.05mm，或0.30mm孔盖油可靠性获批准。** 无树脂塞孔/填孔假设。

pin13本体下孔已取消。独立将 `ground_links.json` 所有路径逐段对齐实际铜端点并用原生长度重算：pin13到pin10支路2.900000mm，加共享pin10到via1.673837mm，总4.573837mm。共用段有有限阻抗/返回耦合，不能当零阻抗地。B y91.2短条占用后续信号空间，需成组逃线复审。

所有新track无显式mask开窗，pin13水平短条与J202 mask开窗交叠0。**另用实际pad mask多边形独立测量**相邻web约0.200mm、短条到信号mask约0.225mm（计算阈值1nm），不是抄写候选硬编码。全球mask expansion/min-width=0仅是native设置，不能据此宣布板厂容差、底面接触、焊锡抽吸/回流或实物装配合格。

## 参考面

新旧面均扣除全部实际通孔钻孔后比较，避免将地孔中心当实心铜：In1/In4各损失0.424073mm²；In2 AON约3.054899mm²。对所有旧F/In3/B track参考投影未发现>1e-8mm²新增缺口，RF六层区域无新增侵入。此为投影/连通筛，不是全局最小颈、载流、回流电感、阻抗或EMI验证。

J202是未来紧凑头的**24Pin研究口**，不兼容/不授权连接未知30Pin定制SC035HGS。JP301/充电commissioning保持OPEN；余17违规/26未连、装配/信号路由/电源动态/制造成本门仍开放，未采购、通电或发布。

## 复现

复制本目录到隔离副本后重跑，勿回写冻结包。`run_native_checks.py`重跑源导出/ERC/完整同名规则DRC；完整命令与退出码见 `native_command_results.json`，DRC参数为 `--all-track-errors --schematic-parity --severity-all --exit-code-violations --format json`。

`verify.py`、`compare_drc.py`、`plane_reference_audit.py`、`connector_mask_audit.py`、`extra_checks.py`、`path_mask_checks.py` normal/-O六组等价。`negative_tests.py`六类×两模式共12次按精确原因拒绝；`replay.py --output NEW-EMPTY-DIR`同SHA。`final_checks.py`显式检查各门，不靠assert。原算法隔离重跑加独立全源/全部规则/freshfill/新增异网交叠/全SMT孔侵入/真实路径与mask几何，不声称两套完全独立几何内核。
