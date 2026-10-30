# ESP32-S3 接收 SC035HGS：主控端的额外核对

2026-10-28；公开一手文档与固定版本代码审阅，**没有在实物上运行，没有可直接刷写的 SC035HGS DVP 驱动**。

## 1. PCLK 和平均吞吐量不是同一个限制

乐鑫官方 [Camera Application FAQ](https://docs.espressif.com/projects/esp-faq/en/latest/application-solution/camera-application.html#is-a-higher-pclk-always-better-for-the-camera)列出 ESP32-S3 的 PCLK 上限为 40 MHz。即使遵守该上限，板线、电平转换、DMA、存储器、曝光与帧丢失仍须验证，不能承诺满速稳定。

厂家初始化文件名中的 72 MHz 不是实测值；若实际 PCLK 为 72 MHz，就超过上述公开指导范围，不能直接当 S3 合格输入。RAW8 640×480×60 的有效图像平均数据量约 18.432 MB/s，不会把 72 MHz 的瞬时采样要求变成 18.432 MHz。降低帧率或裁剪图像也不能自动证明 PCLK 已降低。

## 2. 只增加传感器识别表仍不够

审阅版本：[`espressif/esp32-camera @ f37e656`](https://github.com/espressif/esp32-camera/tree/f37e65608f709bd94846dee01d947f02ae07c0b0)。

- [S3采样模式代码L578–586](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/target/esp32s3/ll_cam.c#L578-L586)按传感器PID选择灰度输入字节数。已列出的SC031GS走1字节路径；未匹配的灰度传感器默认走2字节路径。不能假装035是031来绕过这一区分。
- [拷贝路径L557–574](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/target/esp32s3/ll_cam.c#L557-L574)在2字节输入/1字节输出时提取交替字节。若自定义035适配仅增加detect/init而遗漏RAW8接收模式，可能得到错误帧长度或丢像素；这是静态代码风险，不是已观测故障。
- [控制脚初始化L204–228](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/driver/esp_camera.c#L204-L228)对PWDN和RESET使用不同的切换顺序。未知FPC脚不能仅凭相同名字填入这两个配置字段；禁用通用GPIO控制也不等于未知模组已经具备安全上电条件。

## 3. 请求的 XCLK 也必须核实

同一[S3时钟配置L331–334](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/target/esp32s3/ll_cam.c#L331-L334)和[动态设置L615–621](https://github.com/espressif/esp32-camera/blob/f37e65608f709bd94846dee01d947f02ae07c0b0/target/esp32s3/ll_cam.c#L615-L621)使用160 MHz整数除法，分数分频字段置零。按这段路径计算，请求24 MHz得到整数分频6，对应约26.67 MHz，而不是精确24 MHz；这是代码路径计算，不是板上测量。应测量实际XCLK、占空比及PCLK，不能只打印请求值来证明符合工厂初始化条件。

这不授权修改PLL，也不证明把输入改成6/10/20 MHz后原表仍合法。外部时钟或更改时钟路径属于需重新验证的设计选项，不是当前已交付能力。

## 4. 验证顺序

先确认这块实物的供电、I/O电平和控制网络，再用电平安全的SCCB和已确认时钟建立寄存器/测试图基线。记录真实XCLK/PCLK、同步波形、有效行长、每帧字节数、曝光及掉帧。只有公开来源或实测支持的DVP RAW8模式可以进入S3联调；MIPI模式表、另一款芯片的表和推算的PLL比例不能替代它。

若现有模组无法满足S3接口与笔内尺寸，保留它作独立试验对象，重新选有可核对接口资料的小型模组；不为迁就既有30针要求锁死最终笔的线序。
