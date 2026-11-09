"""PW-1497 scout 237: scout6_measure (Andes share, hypsometry) plus land and continental-crust share of the surface
(median over the same frames, and at the last frame). Read-only.
usage: PYTHONPATH=. scout7_measure.py RUN_DIR [RUN_DIR ...]"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from scout6_measure import measure  # noqa: E402

from planet import timeline as T  # noqa: E402


def areas(rd):
    r, arr = T.load_frames(Path(rd), ["elevation", "crust"])
    nf = len(r["frames"])
    land, cont = [], []
    for i in range(0, nf, max(1, nf // 30)):
        if r["frames"][i]["t"] < 100:
            continue
        land.append(100 * (T.frame(r, arr, "elevation", i) > 0).mean())
        cont.append(100 * (T.frame(r, arr, "crust", i) > 0).mean())
    lastc = 100 * (T.frame(r, arr, "crust", nf - 1) > 0).mean()
    return np.median(land), np.median(cont), lastc


if __name__ == "__main__":
    print("run    seed | andes% of >3km | >2km >3km >4km (% land) | land% | cont% (median, last) | top m")
    for rd in sys.argv[1:]:
        x = measure(rd)
        land, cont, lastc = areas(rd)
        print(f"{Path(rd).name} {x['seed']:5d} | {x['andes']:5.1f} | {x['gt2']:5.2f} {x['gt3']:5.2f} {x['gt4']:5.2f}"
              f" | {land:5.1f} | {cont:5.1f} {lastc:5.1f} | {x['top']:5.0f}")
