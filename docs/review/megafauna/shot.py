"""shot.py PORT RUN OUT_PREFIX: screenshot the viewer's peoples panel, all and with a dragon kind picked."""
import re, sys
from playwright.sync_api import sync_playwright

port, run, out = sys.argv[1:4]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True,
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1500, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    def inject(route):
        r = route.fetch()
        body = r.text().replace("window.planetViewer.diag = DIAG;", "window.planetViewer.diag = DIAG; window.__pv = { get V() { return V; }, state, setFrame, refresh };")
        route.fulfill(response=r, body=body)
    pg.route(re.compile(r"/viewer/(index\.html)?(\?.*)?$"), inject)
    pg.goto(f"http://127.0.0.1:{port}/viewer/?run={run}&layer=peoples")
    pg.wait_for_function("window.__pv && window.__pv.V && window.__pv.V.layers && !document.getElementById('tlabel').textContent.startsWith('loading')", timeout=180000)
    pg.wait_for_timeout(2500)
    pg.evaluate("window.__pv.setFrame(window.__pv.V.run.frames.length - 1)")
    pg.wait_for_timeout(1500)
    print("rows with counts:", pg.evaluate("[...document.querySelectorAll('[data-people]')].filter(e => / in \\d+ pockets/.test(e.textContent)).length"))
    pg.screenshot(path=f"{out}-all.png")
    el = pg.query_selector("[data-people]:has-text('black dragons')") or pg.query_selector("[data-people]:has-text('dragons')")
    if el:
        el.click()
        pg.wait_for_timeout(2500)
        print("counted box:", pg.evaluate("[...document.querySelectorAll('b')].some(e => e.textContent === 'Counted')"))
        pg.screenshot(path=f"{out}-black.png")
    print("page errors", errs[:5])
    b.close()
