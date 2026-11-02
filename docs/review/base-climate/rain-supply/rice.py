import json, sys, numpy as np
for f in sys.argv[1:]:
    r = json.load(open(f))
    print(f.split("/")[-1], len(r))
    for lo, hi in ((0, 300), (300, 600), (600, 1000)):
        for lab, sel in (("glacial", lambda u: u["sea_ice"] < -20), ("warm", lambda u: u["sea_ice"] >= -20)):
            x = [u for u in r if lo <= u["t"] < hi and sel(u) and u["Pice_A"] is not None]
            if not x:
                continue
            m = lambda k: np.mean([u[k] for u in x if u[k] is not None])
            print(f"  {lo}-{hi} {lab:7s} n {len(x):3d} | dln sink {m('dln_sink'):+.4f} | ice cells {m('n_ice'):.0f}: P {m('Pice_A'):.0f}->{m('Pice_B'):.0f}"
                  f" ({100*(m('Pice_B')/m('Pice_A')-1):+.1f}%) Twarm {m('Twice_A'):.2f}->{m('Twice_B'):.2f} ground {m('Twground_A'):.2f}->{m('Twground_B'):.2f}"
                  f" | cold land {m('n_cold'):.0f}->{m('n_coldB'):.0f} P {m('Pcold_A'):.0f}->{m('Pcold_B'):.0f} ({100*(m('Pcold_B')/m('Pcold_A')-1):+.1f}%)"
                  f" | >45 land P {m('Phi_A'):.0f}->{m('Phi_B'):.0f} Tw {m('Twhi_A'):.2f}->{m('Twhi_B'):.2f}")
