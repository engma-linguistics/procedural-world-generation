"""Earth L6: open-water evaporation (lake_evap), land aet, pet and rain at known lakes."""
import sys
sys.path.insert(0, ".")
import planet  # noqa
import numpy as np
from planet import climate
from planet.grid import build_grid
from tools import earth_data, moisture_budget

PTS = {"Lake Victoria": (-1.0, 33.0, 1500), "Amazon floodplain": (-3.3, -60.0, 1350),
       "Lake Nasser": (23.0, 32.8, 2700), "Caspian": (42.0, 50.5, 1000), "Lake Chad": (13.0, 14.5, 2200),
       "Great Lakes (Michigan)": (44.0, -87.0, 650), "Aral": (45.0, 60.0, 1000), "Lake Eyre": (-28.4, 137.3, 2000),
       "Lake Baikal": (53.5, 108.0, 450), "Lake Titicaca": (-15.8, -69.4, 1700), "Lake Malawi": (-12.0, 34.5, 1800),
       "Lake Balkhash": (46.5, 74.5, 1000)}

grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
c, _ = moisture_budget.capture(grid, d["elev"].astype(np.float64), d["ice"].astype(np.float64))
xyz = np.c_[np.cos(np.radians(grid.lat)) * np.cos(np.radians(grid.lon)),
            np.cos(np.radians(grid.lat)) * np.sin(np.radians(grid.lon)), np.sin(np.radians(grid.lat))]
land = d["elev"] > 0
print(f"{'lake':24}{'lake_evap':>10}{'obs~':>6}{'aet':>6}{'pet':>6}{'P':>6}{'T':>6}")
for k, (la, lo, obs) in PTS.items():
    v = np.array([np.cos(np.radians(la)) * np.cos(np.radians(lo)), np.cos(np.radians(la)) * np.sin(np.radians(lo)),
                  np.sin(np.radians(la))])
    i = int(np.argmax(np.where(land, xyz @ v, -9)))
    print(f"{k:24}{c['lake_evap'][i]:10.0f}{obs:6d}{c['aet'][i]:6.0f}{c['pet'][i]:6.0f}{c['precip'][i]:6.0f}"
          f"{c['temp'][i]:6.1f}")
