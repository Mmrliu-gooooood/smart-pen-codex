# 窄设计与代码证据

## 选择与未实现

本候选只调用官方SC031GS的 `FRAMESIZE_VGA / PIXFORMAT_GRAYSCALE`，XCLK固定10MHz。表名虽含50fps，公开注释明确同时写20MHz/50fps与10MHz/25fps；不把注释当实测。`SC031GS_PID=0x0031`，公开detect按0x3107高字节、0x3108低字节识别；新 checked-read 要求两次I²C都成功。仅编译SC031GS detect/init，SC035HGS/其他型号拒绝，不在错误型号上初始化。

官方内部200×200表存在，但公开framesize枚举没有200×200。`set_output_window`接收offset却未使用；`set_aec_value`的字节写序不能由注释证明符合实物曝光语义。本候选**不增加200模式、不改窗口偏移、不设置曝光/增益**。软件200×200子视图仍来自完整VGA采集，采集吞吐/帧率不变，不能宣称120fps或6mm视野。

## 固定一手来源

- [SC031GS源](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/sensors/sc031gs.c)：detect、set_framesize、set_output_window、set_aec_value。
- [官方模式表](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/sensors/private_include/sc031gs_settings.h)：约L207的VGA时钟/帧率注释。仅分发公开官方源及其许可证，未复制厂商保密资料。
- [S3低层](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/target/esp32s3/ll_cam.c)：160MHz整数分频、SC031GS灰度1B输入/1B输出、DMA大小计算。
- [HAL](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/driver/cam_hal.c)：单帧队列、CPU-copy与PSRAM-DMA路径、cam_take剩余tick超时、帧归还。
- [SCCB新I²C](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/driver/sccb-ng.c)：原SCCB_Read16失败仍返回未初始化rx_buffer；候选新增checked API，不使用错误值识别或读改写。
- [S3官方FAQ](https://docs.espressif.com/projects/esp-faq/en/latest/application-solution/camera-application.html#is-a-higher-pclk-always-better-for-the-camera)：PCLK≤40MHz指导上限，不是GDMA80MHz等价能力。
- 本地SDK固定`67c1de1eebe095d554d281952fde63c16ee2dca0`、v5.4，`components/soc/esp32s3/register/soc/lcd_cam_struct.h`说明cam_clk_sel=3为PLL_F160M_CLK（低层旧注释“no clock”不应照抄）。

## 时钟校验与证据边界

`pen_capture_clock_plan`计算整数分频且要求请求值能精确实现；10MHz→div16；24MHz→div6、26666666余4，返回错误，而非继续假装24MHz。真实backend初始化后回读clock source=3、fractional A/B=0、div16，并记录requested/configured；这只是寄存器配置证据，不是晶振精度、占空比或示波器证据。

profile必须引用独立的真实时钟测量记录并给出PCLK≤40MHz。降低FPS、裁剪、平均4.8MB/s或低XCLK都不能单独证明瞬时PCLK合规。低速VGA模式也未获电气/物理资格。

## 对公共源的有限补丁（包含v2）

完整差异在`verification/esp32-camera.patch`。只支持本仓IDF5.4/new-I2C/SC031GS构建；未声称补丁兼容所有原仓平台/legacy SCCB。

0. v2所有SC031GS reset/mode表按显式数组长度传入，先核验唯一末尾零值REG_NULL后才有界执行；缺失/提前/错误终止项在第一笔写前拒绝。reset表补齐该统一合同；详见`V2_CORRECTNESS_FIX.zh-CN.md`。
1. `SCCB_Read16_Checked`在缺handle、NULL输出、I²C失败时返回失败并清零输出；SC031GS全部读/读改写、detect使用它。
2. framesize在索引resolution前检查枚举；模式表写失败立即返回，不继续设置窗口并假报成功。
3. `esp_camera_init`检查set_pixformat返回；HAL检查创建camera任务返回。
4. 新`esp_camera_fb_get_timeout_ms`复用真正cam_take，保留原4秒API；候选调用只允许1..200ms。无忙等、无伪造buffer。
5. `PEN_CAMERA_GRAY_ONLY_BUILD`去掉capture头的隐式JPEG转换头依赖；构建wrapper仅编译真实所需源，不需要下载esp_jpeg。

未彻底重写官方驱动的所有cleanup语义：真实backend只允许一轮相机初始化尝试/boot，stop或故障后不暖重启/自动power-cycle；任何新的尝试需经过后续获准复位流程，不是catch后重试。

### 时间戳与pressure边界

固定HAL在ll_cam_start和人工VSYNC之后采集软件boot-time；不是首DMA时间/曝光时间。v2更正了原SDK头误导性注释。只用于freshness拒绝，pressure/frame/曝光关联仍未资格。
