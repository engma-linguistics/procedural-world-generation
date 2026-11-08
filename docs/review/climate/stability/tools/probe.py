"""Lane 158: the weathering thermostat's temperature leg, measured on a saved planet (lane 144's 300 Myr fork states,
code 4abc1707 = l144/code/main). For each dT offset: resume the state, shift dT, redo the climate update `rounds`
times (the ice sheets settle toward that climate), then the weathering sink at the balance's CO2 (earth.weathering).
Prints ln sink, ln supply, the supply-weighted local temperature and runoff, ice-free land, against the offset.
usage: probe.py CODE_DIR FORK_BASE [rounds] [offsets...]"""
import gzip, json, pickle, sys, zlib
from pathlib import Path
import numpy as np

code, base = sys.argv[1], Path(sys.argv[2])
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 2
offs = [float(x) for x in sys.argv[4:]] or [-4.0, -2.0, 0.0, 2.0, 4.0]
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa: F401,E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, earth  # noqa: E402

meta = json.loads(gzip.open(f"{base}.json.gz", "rt").read())
blob = Path(f"{base}.ckpt").read_bytes()
grid = build_grid(meta["level"])
params = Params(**meta["params"])
w_area = earth.ocean_area(grid)
rows = []
for d in offs:
    sim = Simulation.from_state(grid, meta["seed"], params, meta["dt"], pickle.loads(zlib.decompress(blob)))
    dT0 = sim.dT
    sim.dT = dT0 + d
    for _ in range(rounds):
        sim._climate(sim.w_elev)
    land = sim.land()
    sink, supply, warm, plants, bare = earth.weathering(sim, land)
    s = supply * plants
    wT = float((s * sim.temp).sum() / s.sum())
    wq = float((s * np.maximum(sim.runoff, 0)).sum() / s.sum())
    ice = float(((sim.ice > 0) & land).sum() / max(land.sum(), 1))
    rows.append((d, np.log(sink.sum()), np.log(supply.sum()), np.log((warm * s).sum() / s.sum()), wT, wq, ice))
    print(f"off {d:+5.1f} (dT {sim.dT:+6.2f})  ln sink {rows[-1][1]:8.4f}  ln supply {rows[-1][2]:8.4f}  "
          f"ln warm {rows[-1][3]:7.4f}  wT {wT:6.2f} C  wq {wq:6.0f} mm  land iced {100 * ice:5.1f}%", flush=True)
r = np.array(rows)
for j, name in [(1, "ln sink"), (2, "ln supply"), (3, "ln warm"), (4, "wT"), (5, "wq")]:
    print(f"slope d {name} / d dT: {np.polyfit(r[:, 0], r[:, j], 1)[0]:+.4f}")
