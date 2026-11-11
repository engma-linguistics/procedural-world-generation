"""Screenshots of the map labels (PW-1655) at three zoom levels, in headless Chrome.
    uv run --with playwright python tools/maplabels_shots.py PORT RUN_ID OUT_DIR [--view=lat,lon] [--dists=3.2,1.9,1.25]
Needs `planet serve --port PORT --no-open` already running (never the owner's port) on a data root with RUN_ID (a peoples run with
languages). Writes OUT_DIR/<n>_<far|mid|near>_<english|local>.png and labels.json (what each shot labelled)."""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    port, run, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    opt = dict(a[2:].split("=", 1) for a in sys.argv[4:] if a.startswith("--") and "=" in a)
    view = opt.get("view", "45,-110")
    dists = [float(x) for x in opt.get("dists", "3.2,1.9,1.25").split(",")]
    out.mkdir(parents=True, exist_ok=True)
    rep = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), headless=True,
                              args=["--headless=new", "--ignore-gpu-blocklist", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_context(viewport={"width": 1600, "height": 1000}).new_page()
        pg.on("pageerror", lambda e: print("[pageerror]", e))
        pg.on("response", lambda r: r.status >= 400 and print("[http]", r.status, r.url))
        for i, (d, tag) in enumerate(zip(dists, ("far", "mid", "near"))):
            pg.goto(f"http://127.0.0.1:{port}/viewer/?run={run}&view={view}&dist={d}")
            pg.wait_for_function("window.planetViewer?.mapLabels && window.planetViewer.mapLabels().length > 0", timeout=300000)
            pg.wait_for_timeout(3000)
            for lang in ("english", "local"):
                pg.select_option("#mapLabelLang", lang)
                pg.wait_for_timeout(1500)
                f = out / f"{i + 1}_{tag}_{lang}.png"
                pg.screenshot(path=str(f))
                rep[f.name] = pg.evaluate("window.planetViewer.mapLabels()")
                print(f.name, len(rep[f.name]), "labels:", ", ".join(t for _c, t in rep[f.name][:12]))
        b.close()
    (out / "labels.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
