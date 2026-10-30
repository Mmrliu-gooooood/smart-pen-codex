# Resume only fragment probes after phase/replay outputs were already saved.
from pathlib import Path
p=Path(__file__).parent;s=(p/'v2_review.py').read_text();exec(s.split('V1=P.parent')[0]);replay=json.loads((P/'replay_v1.json').read_text());phase=json.loads((P/'phase.json').read_text());exec(s.split('# Pixel-located empty border neighborhood; test thin clipped-dot-like components.')[1])
