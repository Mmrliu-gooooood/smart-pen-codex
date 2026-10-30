# v2普通驱动正确性修复与v1撤回说明

## 已确认问题

独审用真实`esp_camera.c → camera_probe → sc031gs.reset → write_regs`配合主机I²C/HAL替身运行，确认v1继承的官方`sc031gs_reset_regs`只有reset和delay两项、没有终止项，而旧writer靠查找REG_NULL停止，发生表末尾越界读取。v1原先的单sensor测试只测set_framesize，遗漏实际reset链。因此**v1不能当成可运行驱动候选**；默认OFF/profile空虽防止默认硬件执行，却不证明该路径正确。

原v1及独审证据保留不改。独审日志位于本工作区`smart_pen_camera_capture_review_20261029/driver-reset-oob-asan.log`，此次只修普通边界/错误传播与回归，不接任何设备。独审当时流程中断，不能宣称其已有完整通过报告。

## 统一修复，而非仅补终止项

1. `write_regs(addr, regs, count)`必须取得真实数组的显式元素数；全部count来自`SC031GS_ARRAY_COUNT(实际数组)`，不是外部数据。
2. 所有表统一为至少一项操作加**唯一末尾`{REG_NULL,0}`**。writer先在显式count内验证最后项、值与中途不得出现终止符，验证完成前不执行任何I²C写。
3. 仅执行`i+1<count`的有界循环；每次写错误立即返回，绝不继续后续项。delay不向SCCB写，终止项也不写。
4. reset补上同一终止项并传真实count；200表与VGA表分支分别配对真实count；删除未用的无长度writer宏。200表的单元测试仅验证内存/错误合同，**不新增或资格化200物理模式**。
5. 实际`esp_camera_init`串联回归覆盖正常reset、所有109处写失败、6处读失败、SCCB/HAL init与config错误以及cleanup计数/不得额外写；不是再用“只有framesize成功”替代启动链。

此内部函数的count是编译期数组边界合同，不是任意不可信指针/长度解析器。没有新增wire/远程寄存器接口，也没有暴露任意写入能力。

## 时戳勘误

固定HAL在`ll_cam_start`与人工`ll_cam_do_vsync`之后立刻调用`esp_timer_get_time`；该值是**HAL软件boot-time采样**，不是首DMA开始/完成时间或曝光中点。v2改正driver头注释、采集层注释和应用合同。真实HAL mock测试验证这一调用顺序，不把软件顺序冒充传感器时间测量。

当前时间只支持单调/年龄/freshness拒绝逻辑。曝光和压力边沿关联仍未资格，不得用它声称物理笔尖时空对齐。

## 扩展回归的来源与边界

`test_driver_api.c`、`test_hal_cleanup.c`、`test_idf_backend.c`、`test_core_extra.c`及窄driver stubs基于本地独审留下的测试源码纳入v2并扩展，均实际重新编译运行；结果属于**本v2实现者回归**，不是独立复查已经通过。ASan/UBSan启用，LSan仍因本环境ptrace限制关闭。HAL的主机指针/descriptor替身不证明32位目标硬件的真实中断/DMA/内存占用。

v2继续默认OFF、空profile、单boot初始化策略、无mapper/VALID。完成后仍须安排独立正确性复查，且不因此获得上电/刷机许可。
