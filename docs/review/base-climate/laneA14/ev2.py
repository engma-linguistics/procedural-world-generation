exec(open("ev.py").read().split('variant("main (50 m)"')[0])
T = g["sst"] + g["sea_half"]
for k in (0.5, 1.0):
    u = np.sqrt(g["us"] ** 2 + (k * 7.0 * g["trs"]) ** 2)
    for hmin in (10.0, 20.0):
        variant(f"MO storm k{k} hmin{hmin:.0f}", np.clip(mo(u, T), hmin, 50.0))
