# SC035HGS 公开驱动核对（2026-10-28）

只审阅代码，未运行下载代码或在实物上验证；不公开保密手册、截图或完整寄存器表。

## 已确认的公开证据

[思特威产品列表](https://www.smartsenstech.com/en/products_list)列出SC035HGS及DVP能力。这证明芯片支持接口，不证明用户定制30针模组怎么连接。

乐鑫 `esp-video-components` 固定提交 `cd6194c97c43d6997eee13faf9e4c2ac4cae0c26`：

- [Kconfig](https://github.com/espressif/esp-video-components/blob/cd6194c97c43d6997eee13faf9e4c2ac4cae0c26/esp_cam_sensor/sensors/sc035hgs/Kconfig.sc035hgs)把SC035HGS限制在 `SOC_MIPI_CSI_SUPPORTED`，自动识别/格式选项为MIPI。
- [驱动L254–385](https://github.com/espressif/esp-video-components/blob/cd6194c97c43d6997eee13faf9e4c2ac4cae0c26/esp_cam_sensor/sensors/sc035hgs/sc035hgs.c#L254-L385)提供四种MIPI格式，没有DVP格式分支。其中120fps RAW10显示名称写20M，但实际xclk字段及表文件为24M，不能只看模式名称。
- README及[FAQ](https://docs.espressif.com/projects/esp-faq/en/latest/application-solution/camera-application.html)中的支持声明，不能代替S3/DVP实现核对。代码中的reset/pwdn软件字段也不能证明定制排线的物理映射。

乐鑫 `esp32-camera` 固定提交 `f37e65608f709bd94846dee01d947f02ae07c0b0`：

- [传感器目录](https://github.com/espressif/esp32-camera/tree/f37e65608f709bd94846dee01d947f02ae07c0b0/sensors)有SC030IOT、SC031GS，没有SC035HGS驱动。
- [SC031GS配置](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/sensors/private_include/sc031gs_settings.h)中的VGA 10MHz/25fps、20MHz/50fps注释属于SC031GS，不能当成SC035HGS已经验证的模式。型号相似、寄存器重叠不是模拟电路或PLL可互换的证据。

## 独立实现：有参考价值，不是原厂模式资格证明

`Redns/SC035HGS @ f704171a47396a08d22b3c6340af0f103d3ec21d`是面向Zynq的独立实现。[像素时钟计算L151–162](https://github.com/Redns/SC035HGS/blob/f704171a47396a08d22b3c6340af0f103d3ec21d/src/sc035hgs/sc035hgs.c#L151-L162)说明缺少PLL编程资料，因而按XCLK/24MHz乘85MHz估算。这不是实际测得的PCLK，更不能证明降XCLK后VCO仍合法。

[头文件模式注释](https://github.com/Redns/SC035HGS/blob/f704171a47396a08d22b3c6340af0f103d3ec21d/src/sc035hgs/sc035hgs.h#L187-L192)写24MHz/85MHz/60fps，仓库附带INI文件名却标120fps/10bit。README的低帧率示例不证明低瞬时PCLK；仓库原理图也不是用户这件模组的内部线路。

## 设计决定

本次没有找到足以认定为“这件SC035HGS定制模组已验证的低PCLK、DVP RAW8模式”的配置。**这不是断言全网不存在，也不是SC035HGS不支持DVP。** 不把摄像头冒充SC031GS，不通过猜测PLL表宣称适配完成。

先依据已有PDF确定芯片端功能与电平，再核实实物供电/连接。电气条件确认后才能使用已有初始化建立基线，测PCLK/HREF/VSYNC及曝光，并由能接收实际时钟的设备采图。低PCLK模式开发属于后续单独验证，不是现成的生产配方。主控端另见[ESP32-S3接收约束](esp32s3_capture_constraints.md)。
