# 中间比较，不是接受版本

- uniform grid mask 的矩形外扩会错拒 pad 斜角；记录无路只对当时保守搜索范围成立，不是全板不可布证明。
- 四网原始铜 17/22/0 作回退；五网原始铜未经有界简化。
- pin17 改共地条分支仍没有关闭 reset，已拒绝；最终保留4994全部地铜。
- reset .45/.20 手动合法出口先出现仅单层dangling，再用 x0.40 mm 真实板边通道闭合；全规则没有放宽。
- 25um出口微移后仍17/21/0，参考缺口未完全归零，见最终报告。
- exploratory_scripts zip 是当时施工记录，路径与输出属于历史试验，不能在冻结目录直接运行。最终可重现入口只有根目录 replay.py。
- manufacturing_preflight.log 是一次错误CLI参数调用的日志，不作制造拒绝证据；真正资格拒绝是根 manufacturing_expected_rejection.log + JSON。
