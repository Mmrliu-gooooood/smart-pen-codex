# 帧/错误/应用接入合同

## 一次借用，一个owner

`pen_capture`非线程安全，只能由一个任务串行调用，禁止ISR调用、多个actor共用、其他camera客户端并行使用。不得对活跃实例重新construct。真实LCD_CAM backend是单例，生产start必须经过`pen_capture_idf_start`与空的已审核profile注册表；直接调用portable seam也不能绕过真实backend的armed/allowlist复查。

- `get`成功进入HELD，借用真实driver fb；要求Gray8、640×480、stride640、**精确307200字节**。不用resize/JPEG/隔字节伪灰度。
- 帧timestamp是固定HAL在`ll_cam_start`和人工`ll_cam_do_vsync`之后调用`esp_timer_get_time`取得的**软件boot时间采样**；不是首DMA中断/完成时间，也不是曝光中点。原SDK头的“首个DMA块”描述不能替代实现证据，本v2已纠正头注释。验证非零、严格递增、不在未来、交付时年龄≤200ms；frame_id递增。时序阈值是此候选的明确保守门，不是实测系统延迟预算。
- HELD期间再次get返回STATE，不取下一帧、不触发超时、不自动归还，旧借用仍由调用者负责。
- release仅接受当前非零frame_id；只归还一次。任何先前view、ROI、app_frame都立即失效，禁止继续读取。
- 显式stop在HELD时先归还，再deinit/安全关闭，所有外部借用指针同样失效。stop后app桥拒绝旧view；C指针本身无法自动清零，使用者必须主动丢弃。
- capture错误先归还已经获得的fb再关闭；任何失败的get/app桥都清空新的输出，不能拿上一次图像重复解码或造VALID。

## 超时/恢复

get允许1..200ms。当前构建tick=1ms；SDK按剩余tick等待并处理坏帧/GDMA重试，不是无限阻塞。调度、日志、SDK内部操作会添加延迟，**不是墙钟硬实时上限**。前三次连续超时中，前两次返回TIMEOUT且无帧，第三次返回TIMEOUT_FATAL并关闭；好帧把连续计数清零。格式/时戳/driver错误直接FAULT；held时不会偷偷进行timeout轮询。

portable测试backend可在完整成功stop后显式start；清理失败则`cleanup_failed`锁死不可重试。**真实backend更严格：esp_camera_init一旦尝试，整个boot内不再第二次初始化。** 即使stop报告成功，也不表示官方ISR/GDMA/I²C所有释放都经过实机证实；不存在自动重新上电恢复。后续需要获准的板级安全复位/实机验证才能设计可恢复运行版。

power hooks必须能从任意部分失败状态关钟、阻止IO反灌、隔离并安全关电。它们当前没有任何实现/profile，故不存在实际GPIO动作。SDK deinit不保证断开XCLK输出或关rail，不能替代这项板级合同。

## CPU缓存/内存

只允许`CONFIG_CAMERA_PSRAM_DMA=n`、converter关闭、fb_count=1。GDMA写内部DMA缓冲，官方camera任务CPU-copy到PSRAM fb后入队；消费者与写者不同时持有该fb。这里没有绕过缓存的DMA→PSRAM，因此不在borrowed view上额外flush/invalidate；盲目invalidate可能丢掉CPU刚写的数据。future direct PSRAM DMA需独立验证对齐与cache同步，不在本候选开启。

## 软件ROI和原点

`pen_capture_app_frame`是完整VGA诊断接口，**不得把640×480直接喂给最大256×256的decoder**。

`pen_capture_app_roi(c,view,left,top,width,height,frame,origin)`要求每轴96..256且明确给出原点，逐项防越界；不缩放；stride仍640；length只覆盖最后有效行像素。`origin`保存full_width/height/stride、left/top、parent_frame_id/source_id；与帧共用借用寿命。例子只可用于host测试，不默认“居中200等于6mm”。decoder的paper_to_frame是子视图坐标，后续镜头/笔尖标定必须先加回全帧原点，不能当全传感器坐标。

## 尚未接通的系统部分

这里构造原`pen_app_frame` ABI，不调用pipeline、不提供`pen_board_provider`。`pen_capture_app_disqualify`强制camera_qualified=0、mapper=NULL、标定revision=0；没有资格赋予函数。真实capture可如实标SENSOR，而host替身永远SYNTHETIC；来源标记不等于电气/成像资格，也不是授权。

真实曝光与压力边沿的关联仍未资格，不能由当前freshness校验推出。真实集成须独立排队压力边沿、HAL软件帧时间与idle poll；不能在actor里阻塞200ms而丢压力边沿，也不能把新idle事件排到旧帧之前。必须把缺图/超时作为无效观察打断笔画，不能插值出VALID。没有物理mapper、标定、接触时序与硬件资格前始终不记录有效坐标。
