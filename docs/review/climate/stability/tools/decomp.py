"""Lane 158: what carries the forked nulls' divergence? Per era, rms over the six draws (fn and fn2 vs fm) of the
paired differences of each term of the climate's target and of the carbon balance's parts. Read only."""
import gzip, json, sys
import numpy as np
L = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l144/judge"
six = [("0.0005", "l6c_0", "819014"), ("0.001", "l6c_p", "957317"), ("0.001", "l6c_0", "819014"), ("0.001", "l6c_0", "53669"),
       ("0.0005", "l6fix", "957317"), ("0.001", "l6fix", "957317")]
bins = [(300, 350), (350, 400), (400, 500), (500, 600), (600, 700), (700, 800), (800, 884), (884, 1000)]


def rec(arm, r, tag, s):
    st = json.load(gzip.open(f"{L}/{arm}_r{r}_{tag}/seed{s}_L6.json.gz"))["steps"]
    return {round(x["t"], 3): x for x in st if abs(x["t"] - round(x["t"])) < 1e-9}


F = {"dT": lambda x: x["dT"], "drift": lambda x: x["drift"],
     "ln src": lambda x: np.log(x["src"]),
     "ln src_raw-plume": lambda x: np.log(max(x["source_raw"] - x["plume_src"], 1e-9)),
     "ln plume": lambda x: np.log(max(x["plume_src"], 1e-9)),
     "ln sink@X=1": lambda x: np.log(x["sink"]), "ln supply": lambda x: np.log(x["w_supply"]),
     "ln w_temp": lambda x: np.log(x["w_temp"]), "ln w_plant": lambda x: np.log(x["w_plant"]),
     "w_area": lambda x: x["w_area"], "co2 lnX": lambda x: x["co2"], "co2_term": lambda x: x["co2_term"],
     "albedo": lambda x: x["albedo_term"], "ghg": lambda x: x["ghg"], "land": lambda x: x["land"],
     "iced_land_pct": lambda x: x["iced_land_pct"]}
if __name__ == "__main__":
    for arm in sys.argv[1:] or ["n", "n2"]:
        print(f"== {arm} - m (forked at 300), rms of paired difference over 6 draws")
        print(f"{'term':>22} " + " ".join(f"{f'{a}-{b}':>9}" for a, b in bins))
        D = {k: {b: [] for b in bins} for k in F}
        for r, tag, s in six:
            A, B = rec(arm, r, tag, s), rec("m", r, tag, s)
            for b in bins:
                ts = [t for t in A if b[0] < t <= b[1] and t in B]
                for k, f in F.items():
                    D[k][b] += [f(A[t]) - f(B[t]) for t in ts]
        for k in F:
            print(f"{k:>22} " + " ".join(f"{np.sqrt(np.mean(np.square(D[k][b]))):9.3f}" for b in bins))
