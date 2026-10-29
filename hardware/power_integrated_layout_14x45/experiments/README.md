# 非最终迭代记录

本目录是保留的失败/中间检查，不是当前 PCB 的验证。`u104_escape_drc.json` 是一次直接放置地 via 后发现真实间距/短路错误的尝试，已恢复该尝试之前的板，再使用带实际障碍的路径搜索重布，绝未用豁免掩盖。`move_c101_drc.json` 是移动后未重填铜时的临时检查；最终已重填。`c101_ground.log`/`ce_reroute.log` 记录未找到合法通路、未保存板的失败尝试。

`tools/ground_escape_u104.py`、`tools/close_c101_ground.py`、`tools/reroute_ce_escape.py` 仅失败过程证据，不能在最终板执行。其余探索性移动/布线/清理脚本同样不属于幂等重建入口；最终检查入口仅 `../run_checks.sh`。原生 PCB 是最终可编辑布局源。
