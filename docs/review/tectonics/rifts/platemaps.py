"""usage: PLANET_DATA=<main checkout> platemaps.py OUT_DIR RUN_NAME [...] -> per run: a plate-map PNG at
0/300/600/800/1000 Myr (plates coloured, continents darker) and a plate-share line: largest plate share and
plates over 2% of the surface every 100 Myr, plus their means over 600-1000 Myr, and the run's rift,
triple-junction and margin-subduction counts per 200 Myr. Harness only (PW-565, PW-952)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from planet import store as S  # noqa: E402
from planet import timeline as T  # noqa: E402
from planet.geo import latlon  # noqa: E402
from planet.grid import build_grid  # noqa: E402

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
ids = {}
for p in S.runs_dir().glob("*/run.json"):
    h = S.read_header(p)
    ids.setdefault(h.get("name"), []).append(p.parent)
for name in sys.argv[2:]:
    run_dir = sorted(ids[name], key=lambda d: d.stat().st_mtime)[-1]
    run, arr = T.load_frames(run_dir, ("plate", "crust"))
    grid = build_grid(run["meta"]["level"])
    lat, lon = latlon(grid.centers)
    frames = run["frames"]
    ts = np.array([f["t"] for f in frames])
    big = np.array([f["stats"]["largest_plate_pct"] for f in frames])
    o2 = np.array([f["stats"]["plates_over_2pct"] for f in frames])
    late = (ts >= 600) & (ts <= 1000)
    every = [int(np.argmin(abs(ts - t))) for t in range(0, 1001, 100)]
    ev = run["events"]
    cnt = {}
    kinds = {"rift": lambda e: e["kind"] == "rift" and "triple junction" not in e["text"],
             "triple": lambda e: e["kind"] == "rift" and "triple junction" in e["text"],
             "subduction": lambda e: e["kind"] == "subduction"}
    for kind, is_ in kinds.items():
        cnt[kind] = [sum(1 for e in ev if is_(e) and a < e["t"] <= a + 200) for a in range(0, 1000, 200)]
    print(f"{name} ({run_dir.name}): largest% " + " ".join(f"{big[i]:.0f}" for i in every)
          + f" | >2%: " + " ".join(str(o2[i]) for i in every)
          + f" | 600-1000 mean largest {big[late].mean():.1f}% max {big[late].max():.0f}%, >2% {o2[late].mean():.1f}"
          + " | stress rifts/200 " + "-".join(map(str, cnt["rift"])) + " triple/200 " + "-".join(map(str, cnt["triple"]))
          + " subd/200 " + "-".join(map(str, cnt["subduction"])))
    show = [int(np.argmin(abs(ts - t))) for t in (0, 300, 600, 800, 1000)]
    fig, axs = plt.subplots(1, len(show), figsize=(4 * len(show), 2.4))
    for ax, i in zip(axs, show):
        pl = T.frame(run, arr, "plate", i).astype(int)
        cont = T.frame(run, arr, "crust", i).astype(bool)
        u, inv = np.unique(pl, return_inverse=True)
        share = np.bincount(inv) / len(pl)
        rank = np.argsort(np.argsort(-share))  # (the 20 biggest plates get 20 different colours)
        cols = plt.cm.tab20(np.arange(20))[rank % 20][:, :3]
        c = cols[inv] * np.where(cont, 0.6, 1.0)[:, None]
        size = (2.0 if grid.n > 20000 else 5.0) / np.maximum(np.cos(np.radians(lat)), 0.05)
        ax.scatter(lon, lat, c=c, s=size, marker="s", linewidths=0)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{ts[i]:.0f} Myr: largest {100 * share.max():.0f}%, {int((share > 0.02).sum())} >2%", fontsize=8)
    fig.suptitle(f"{name} ({run_dir.name})", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=80)
    plt.close(fig)
