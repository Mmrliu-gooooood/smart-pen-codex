# 光学与可采购性结论（2026-10-27）

**状态：候选筛选完成；未选定量产/两支成品摄像头，禁止据此冻结连接器、镜座或采购。** 未联系供应商、未下单。本文件区分传感器能力、模组已引出的能力、实测能力；三者不能互换。

## 结论及推荐顺序

0. **最低成本且优先：复用用户已有MMSYDZ-ESP32-S3-HDSF035V1.0 RevA SC035HGS DVP模组做台架**。已检查用户提供的真实图纸，见下节；它不是第三方6.5mm MIPI小模组。先验证近焦和遮挡，再决定是否需要买新模组。以下三家仅是替代采购方向。
1. **第一询价方向：AS-video 的 SC031GS DVP 8×8 mm 模组**，要求近摄镜头、无 IR-cut 版本及完整图纸。体积与接口方向最接近，但价格、总高、初始化程序和实测近摄均缺失，不能称为已可交付方案。
2. **有公开零售价格的台架备选：IADIY DCM1M210M7 / OV9281**。仅在确认 DVP 引脚、实际帧率和近摄镜头后才值得用户授权买样；$38/个对人民币380元整笔预算压力大。它不是现有30针3.3V附件的即插即用替代。
3. **第三家对照：Hampo HAMPO-E3MPF-OV9281 V1.0 NIR**。有模组尺寸、无IR滤镜说明，但近摄不明，固定焦、长尾尺寸及小量报价必须确认。
4. HM0360可作为低功耗对照，**不能作为全局快门替代**；SC035HGS的已知MIPI模组也不能直接接DVP。现有RevD外置附件不证明能装进笔。

## 用户现有模组：比网上泛搜更直接的证据

已渲染检查用户提供 `module-drawing/MMSYDZ-ESP32-S3-HDSF035V1.0(1).pdf`（RevA，深圳舜雨电子科技有限公司），本交付另存 `EXISTING_MODULE_DRAWING_NOTES.md` 的数据摘录。实际SC035HGS模组是30针DVP，不是只因芯片有DVP就推定模组有DVP。图纸：主体13±0.2mm方形，含耳宽21.82±0.2mm、孔距18±0.1mm、孔径1.8±0.1mm，轴向9.44±0.2mm，镜头Ø10±0.1mm；全长65.04±0.2mm；FPC宽8±0.1mm，端部15.5±0.1mm，0.5mm针距。**完整模组并不笔尖级微型，但可作现有台架。**

镜头表：1/6英寸、EFL1.98mm、F2.2、D/H/V视角65°/54°/40°、畸变<1%。图纸没有MOD、IR滤镜、近摄MTF或可调焦说明。先以现状扫焦，未经确认不旋松胶封镜头。只有在证实支持调焦后才调整并记录原位置。

接口表pin2/28为3V3，D0–D7及同步/时钟明确引出；传感器栏列2.8/1.5/1.8V。**图纸不能证明内部LDO或每个输入的3.3V容限**，须电子负责人核验电路。源资料内还有SC035HGS V0.3完整数据手册与DVP 30/60FPS配置文件；配置名不是实测帧率。其机密标记文件不在公开交付中重新分发。

先做可见光静态台架、记录近焦失败的原图；若能满足5–7mm有效视野和斜视门槛，可暂缓新相机开支。台架通过不等于当前21.82mm安装耳能进入目标笔壳，不能切削改造传感器模组来强行适配。

## 货比三家：模组级而非只比芯片

|供应商 / 明确型号|公开证据|价格证据（非已确认报价）|本项目主要缺口|结论|
|---|---|---|---|---|
|[AS-video AS-DGSG8A130D7](https://www.as-video.com/product/sc031gs-vga-global-exposure-subminiature-structure-180fps-mini-dvp-camera-module.html)|SC031GS，DVP，8×8mm PCBA；标题180fps但表格480P120fps|没有公开单价；MOQ/2件样品未知|总高、镜座、针脚、供电、实际DVP时序、近焦、滤镜、2件含税价|优先RFQ，不能采购冻结|
|[IADIY DCM1M210M7](https://www.iadiy.com/dvp-camera-module-ov9281)|OV9281，DVP，8×8.5mm，M7，24针0.5mm，50mm尾长；[官方模组PDF](https://www.iadiy.com/image/catalog/IADIY/products/camera-module/fpc-dvp-camera-module/DCM1M210M7/fpc-dvp-camera-sensor-module-DCM1M210M7.pdf)|$38/个；10件$32不能套用2件；页面7–21天，正文14–21天|PDF高速表注明MIPI；网页与PDF电流不同，不能据此定电源；近焦/总高未知|可买样线索最清晰，非已验证成品部件|
|[Hampo HAMPO-E3MPF-OV9281 V1.0 NIR](https://www.hampotech.com/ov9281-globa-shutter-hd-1mp-ff-mipi-camera-module-product/)|厂商称MIPI及DVP，24×8.5mm模组，8.5×8.5×4.75mm镜头，固定焦，无IR滤镜，0.4mm间距连接器|[厂商HKTDC销售页](https://sourcing.hktdc.com/en/Product-Detail/1MP-OV9281-Global-Shutter-MIPI-DVP-FF-Camera-Module-1Z03JN3ER)显示$15.20–19.95区间；未核实2件适用|到底哪个接口被引出、连接器型号、MOD、针脚/总高/含税2件价|作为成本对照询价，不能采用区间低价作BOM|
|[Ronghua RH-CG038A0D1-50](https://www.ronghuayxf.com/sc031gs-dvp-high-speed-fps-camera-module-af-ff-product/)|SC031GS DVP标题；需索取模组PDF|无价格|页面同时出现USB/1080p等与VGA传感器不一致的模板描述|不据此选型；仅备用询价线索|

## 传感器层的事实边界

- [SmartSens SC031GS V5.0官方产品简表](https://smartsens.oss-cn-beijing.aliyuncs.com/web/products/SC031GS_V5.0.pdf)：640×480、3.75µm、全局快门、最高180fps、RAW MONO、8/10/12位DVP；32针CSP3.70×3.07mm；模拟2.8V、核心1.5V、I/O1.8V。**这是芯片尺寸，不是镜头模组尺寸；简表不是完整寄存器/时序手册。**
- [OV9281官方页面](https://www.ovt.com/products/ov9281/)及[2024产品简表](https://www.ovt.com/wp-content/uploads/2024/05/OV9281-PB-v1.4-WEB.pdf)：全局快门、1280×800、DVP/MIPI、8/10bit RAW，模拟2.8V/核心1.2V/I/O1.8V；156mW是传感器指定活动工况，不是整笔或模组功耗。具体模组、位宽、时钟、主控吞吐仍决定可达FPS。
- [Himax官方HM0360页面](https://www.himax.com.cn/products/cmos-image-sensor/always-on-vision-sensors/hm0360/)给VGA60fps约7mA；[Himax模组数据表](https://media.digikey.com/pdf/Data%20Sheets/Himax%20PDFs/HM0360-MWA-00FP963.pdf)属于另一配置，不能混用电流；电子滚动快门不满足优先全局快门要求。

## CH2035AB：5mm近焦是真的，但不等于适合本笔

[创安官方机械/光学图纸](https://www.opticslens.com/uploads/CH2035AB.pdf)明确：MOD0.005m–∞、SC031GS、EFL1.36mm、F2.4、Ø6×3.67mm、TTL4.35mm、M5.5×0.2、图中镜座6.5×6.5mm；**IR650nm滤镜**；水平视角99.2°、TV畸变标注<-10%。供应商[产品表](https://www.opticslens.com/pl/m5-lenses-product/)需询价。MOD的测量基准、近摄时TTL变化和锁付位置还须确认。

- 不要将IR650nm版本配850/940nm照明后假定能透过；需无IR-cut/指定窄带版本的透过率曲线、焦移与近摄MTF。不能自己改滤镜后仍引用原性能。
- 本镜头适配1/6英寸、最大像圈3.3mm；**不可直接视作OV9281全画幅镜头**。M5.5和M7镜座也不兼容。
- 99.2°是指定成像条件视角，不能用它直接证明5mm工作距离下5–7mm清晰视野。SC031GS有效宽约2.4mm；薄透镜示例：6mm物方宽对应放大率0.4，主平面物距约4.76mm（1.36×(1+1/0.4)）。这是定位试验区间的估算，不是供应商工作距离保证。
- 5–7mm横向640像素时0.3mm点距约27–38像素；裁剪、斜视、边缘畸变、点径及散焦均会改变可识别性。点距采样足够不意味着坐标准确。

## 运动与斜视：60fps并非通过依据

物方运动模糊 b=v×t。0.5m/s、1ms曝光会移动0.5mm，已超过0.3mm点距。若初步要求模糊≤点距10%=0.03mm，则0.5m/s需t≤60µs；1m/s需≤30µs。以6mm/640px计，0.03mm仍约3.2px；若要求≤1px，则0.5m/s需≤18.75µs。最终要用点径和定位误差反推，不把60µs当认证阈值。

60fps在0.5m/s下帧间位移8.33mm，180fps仍2.78mm。对于6mm视野，要求相邻图像≥50%重叠的纯跟踪，理想下限约167fps（还未扣斜视有效视野）；绝对码每帧独立解码可能不要求重叠，但不能假定本解码器支持。

角度必须分开记录：笔轴与纸面夹角α；相机光轴与纸面法线夹角θ；相机相对笔轴安装角β。用户所说30–60°未说明基准。纸上沿倾斜方向跨度L时，光轴方向近远深度差约L·sinθ：L=6mm、θ=60°约5.2mm，故单一“5mm近焦”不保证全场景深。相机安装角可与笔轴不同，不能拿笔角直接代光轴角。

**冻结阻塞：**没有同时满足小量价格、完整总成图纸、DVP针脚与驱动、5–7mm近场清晰视野、短曝光实测、笔芯遮挡和光安全证据的同一具体SKU。继续泛搜不能补齐这些证据，下一步是用户授权询价与实体试验。
