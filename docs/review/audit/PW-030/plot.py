"""plot.py OUT.png TAG [TAG ...]: sea-level change curves (and global dT) of tz_eval outputs."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path(__file__).parent / "out"
fig, ax = plt.subplots(2, 1, figsize=(11, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
for tag in sys.argv[2:]:
    z = np.load(D / f"{tag}.npz")
    s = z["series"]
    ax[0].plot(s[:, 0], s[:, 1], lw=1, label=tag)
    ax[1].plot(s[:, 0], s[:, 3], lw=1)
ax[0].set_ylabel("sea level change (m)")
ax[1].set_ylabel("dT global (C)")
ax[1].set_xlabel("kyr")
ax[0].legend(fontsize=8)
ax[0].grid(alpha=.3); ax[1].grid(alpha=.3)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=80)
