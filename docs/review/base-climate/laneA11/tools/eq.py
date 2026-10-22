"""Is the glacial's leftover ice where the no-index run would grow ice anyway (its smb > 0 there, it just hasn't got
there yet)? The leftover (on - off at 15 kyr after the ending) split by the off-run's final mass balance there."""
import sys, os, numpy as np
WT = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44"
sys.path.insert(0, WT)
from planet import store as S
from planet.grid import build_grid
from planet.timezoom.sim import LAYERS
OUT = os.path.dirname(os.path.abspath(__file__)) + "/out"
g = build_grid(4)
dec = lambda a, k="ice": S.decode(a, LAYERS[k]).astype(float)
for tag in sys.argv[1:]:
    d = np.load(f"{OUT}/end_{tag}.npz")
    i, j = int(d["i"]), int(d["j"])
    on_i, off_i, on_j, off_j = dec(d["ice_on"][i]), dec(d["ice_off"][i]), dec(d["ice_on"][j]), dec(d["ice_off"][j])
    ex_i, ex_j = np.maximum(on_i - off_i, 0), np.maximum(on_j - off_j, 0)
    pos = d["smb_off"] > 0  # the no-index run's own mass balance (t=200, index 0) is positive there
    tw = d["tw_off"]
    print(f"{tag:8s} extra@ending {ex_i.sum()/1e3:6.1f} km-sum, of it in smb_off>0 cells {ex_i[pos].sum()/1e3:6.1f} | "
          f"left@+15 {ex_j.sum()/1e3:6.1f}, in smb_off>0 {ex_j[pos].sum()/1e3:6.1f} | "
          f"left@+15 where off t_warm<0 {ex_j[tw < 0].sum()/1e3:6.1f}; |lat|>60 {ex_j[np.abs(g.lat) > 60].sum()/1e3:6.1f}")
