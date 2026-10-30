"""shot.py PORT RUN OUTDIR: viewer screenshots for the dragon-density page: the peoples layer at the present, then one dragon kind
picked (its range against the peoples'). Needs a `planet serve --port PORT` on the run's data root and /usr/bin/google-chrome.

Run: uv run --with playwright python docs/review/megafauna/dragon-density/shot.py 8791 3097e3 docs/review/megafauna/dragon-density/shots
(after the docs/review/megafauna/shot.py pattern)
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

port, run, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
KINDS = sys.argv[4:] or ["green_dragon"]
CLIP = {"x": 290, "y": 50, "width": 1100, "height": 740}  # the globe and the peoples panel, not the side bar
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True,
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1400, "height": 860})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    def inject(route):
        r = route.fetch()
        body = r.text().replace("window.planetViewer.diag = DIAG;", "window.planetViewer.diag = DIAG; window.__pv = { get V() { return V; }, state, setFrame, refresh };")
        route.fulfill(response=r, body=body)
    pg.route(re.compile(r"/viewer/(index\.html)?(\?.*)?$"), inject)
    pg.goto(f"http://127.0.0.1:{port}/viewer/?run={run}&layer=peoples")
    pg.wait_for_function("window.__pv && window.__pv.V && window.__pv.V.layers && !document.getElementById('tlabel').textContent.startsWith('loading')", timeout=300000)
    pg.wait_for_timeout(2500)
    pg.evaluate("window.__pv.setFrame(window.__pv.V.run.frames.length - 1)")
    pg.wait_for_timeout(2000)
    hide = """(() => { const ds = [...document.querySelectorAll('div')].filter(d => d.textContent.includes('human seafarers') && d.textContent.includes('template') && d.textContent.length < 3000);
      ds.sort((a, b) => a.textContent.length - b.textContent.length); if (ds[0]) ds[0].style.display = 'none'; })()"""
    pg.evaluate(hide)
    pg.screenshot(path=str(out / "peoples.png"), clip=CLIP)
    for kind in KINDS:
        idx = pg.evaluate(f"(window.__pv.V.run.meta.lineages || []).findIndex(l => l.id === '{kind}')")
        if idx < 0:
            print("no line", kind)
            continue
        pg.click(f"[data-people='{idx}']")
        pg.wait_for_timeout(9000)
        pg.evaluate(hide)
        pg.screenshot(path=str(out / (kind.replace(" ", "-") + ".png")), clip=CLIP)
        pg.reload()
        pg.wait_for_function("window.__pv && window.__pv.V && window.__pv.V.layers && !document.getElementById('tlabel').textContent.startsWith('loading')", timeout=300000)
        pg.wait_for_timeout(2500)
        pg.evaluate("window.__pv.setFrame(window.__pv.V.run.frames.length - 1)")
        pg.wait_for_timeout(2000)
    print("page errors", errs[:5])
    b.close()
