"""Headless timings of the viewer's peoples views (PW-679).

    uv run --with playwright python tools/viewer_perf.py PORT RUN_ID [--tab]

Opens http://127.0.0.1:PORT/viewer/?run=RUN_ID in Chrome (software GL; set CHROME to override), reports what
the load fetched over the wire, then times, in the page, the interactions that make the peoples views feel
slow: stepping and scrubbing frames, hovering, switching the colour layer, picking a people, playing for 3 s.
Needs `planet serve --port PORT --no-open` already running (never the owner's port). The page's module
scope is reached through a hook injected into the served globe/main.js (nothing is written to viewer/): window.__pv
holds every export of the globe modules (viewer/globe/) and the shared state's V. For a before/after, run each
version's own server.
"""
import json
import re
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PROBE = r"""
async () => {
  const P = window.__pv, { state, setFrame, paint, cellColors, renderRunSummary, renderHover, refresh } = P;
  const out = {};
  const settle = async () => { await new Promise((r) => setTimeout(r, 30)); while (document.getElementById('tlabel').textContent.startsWith('loading')) await new Promise((r) => setTimeout(r, 20)); };
  const T = (name, fn, n = 1) => { const t = performance.now(); for (let i = 0; i < n; i++) fn(i); out[name] = +((performance.now() - t) / n).toFixed(2); };
  out.layer = state.layer; out.frames = P.V.run.frames.length; out.cells = P.V.n;
  out.loaded_MB = Object.fromEntries(Object.entries(P.V.bytes).map(([k, v]) => [k, +(v / 1e6).toFixed(1)]));
  T('setFrame no repaint (ms)', (i) => setFrame(20 + i, false), 20);
  T('cellColors (ms)', () => cellColors(state.layer), 10);
  T('paint (ms)', () => paint(), 10);
  T('renderRunSummary (ms)', () => renderRunSummary(), 10);
  T('renderHover (ms)', () => renderHover(), 10);
  T('setFrame full (ms)', (i) => setFrame(30 + i), 20);
  const sl = document.getElementById('frame');
  let t = performance.now();
  const pn0 = planetViewer.diag.n.paints;  // 40 slider events back to back (a busy machine: they queue); then let the page settle
  for (let i = 0; i < 40; i++) { sl.value = 40 + i; sl.dispatchEvent(new Event('input', { bubbles: true })); }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  out['slider burst of 40 inputs: total ms'] = +(performance.now() - t).toFixed(0);
  out['slider burst: repaints'] = planetViewer.diag.n.paints - pn0;
  out['slider burst: frame shown'] = P.V.frame;
  const cv = document.getElementById('c'), r = cv.getBoundingClientRect();
  const h0 = performance.now(), n0 = { ...planetViewer.diag.n };
  for (let i = 0; i < 100; i++) cv.dispatchEvent(new PointerEvent('pointermove', { clientX: r.left + r.width / 2 + i * 3, clientY: r.top + r.height / 2 + (i % 7) * 4, bubbles: true }));
  out['pointermove (ms each, 100)'] = +((performance.now() - h0) / 100).toFixed(2);
  const n1 = planetViewer.diag.n; out.hover_counters = Object.fromEntries(Object.keys(n1).map((k) => [k, n1[k] - n0[k]]));
  for (const lay of ['peoples mix', 'peoples overlay', 'peoples']) {
    const t2 = performance.now(); document.querySelector(`#layerSeg button[data-v="${lay}"]`).click(); await settle(); out['switch to ' + lay + ' (ms)'] = +(performance.now() - t2).toFixed(0);
  }
  const el = document.querySelector('[data-people]');
  if (el) {
    const t3 = performance.now(); el.dispatchEvent(new MouseEvent('click', { bubbles: true })); out['pick a people (ms)'] = +(performance.now() - t3).toFixed(1);
    document.querySelector('[data-people]').dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }
  const f0 = P.V.frame; setFrame(0); state.playing = true; const a0 = { ...planetViewer.diag.n }, p0 = performance.now();
  const gaps = []; let last = p0;
  await new Promise((res) => { const tick = (now) => { gaps.push(now - last); last = now; if (now - p0 < 3000) requestAnimationFrame(tick); else res(); }; requestAnimationFrame(tick); });
  state.playing = false;
  const a1 = planetViewer.diag.n;
  out.play_3s = { frames_advanced: P.V.frame, rafs: gaps.length, mean_raf_ms: +(gaps.reduce((a, b) => a + b, 0) / gaps.length).toFixed(1), max_raf_ms: +Math.max(...gaps).toFixed(0),
    counters: Object.fromEntries(Object.keys(a1).map((k) => [k, a1[k] - a0[k]])) };
  return out;
}
"""


PHASES = {  # --profile=NAME: just this loop, under the sampling profiler
    "hover": r"""async () => { const cv = document.getElementById('c'), r = cv.getBoundingClientRect();
      for (let i = 0; i < 150; i++) cv.dispatchEvent(new PointerEvent('pointermove', { clientX: r.left + r.width / 2 + i * 3, clientY: r.top + r.height / 2 + (i % 7) * 4, bubbles: true })); }""",
    "switch": r"""async () => { for (let k = 0; k < 4; k++) for (const lay of ['peoples mix', 'peoples overlay', 'peoples']) {
      document.querySelector(`#layerSeg button[data-v="${lay}"]`).click();
      await new Promise((r) => setTimeout(r, 30)); while (document.getElementById('tlabel').textContent.startsWith('loading')) await new Promise((r) => setTimeout(r, 20)); }
      const bins = performance.getEntriesByType('resource').filter((e) => e.name.includes('/layers/')); return { layer_fetches_after_load: bins.length, wire_MB: +(bins.reduce((a, e) => a + e.encodedBodySize, 0) / 1e6).toFixed(1) }; }""",
    "idle": r"""async () => { await new Promise((r) => setTimeout(r, 4000)); }""",
    "spin": r"""async () => { document.getElementById('spin').checked = true; await new Promise((r) => setTimeout(r, 4000)); document.getElementById('spin').checked = false; }""",
    "step": r"""async () => { for (let i = 0; i < 80; i++) window.__pv.setFrame(20 + (i % 100)); }""",
}


def top_self(profile, k=18):
    """Self time per function over the whole probe (ms), from the CDP sampling profiler."""
    nodes = {n["id"]: n for n in profile["nodes"]}
    acc = {}
    for nid, dt in zip(profile["samples"], profile["timeDeltas"]):
        cf = nodes[nid]["callFrame"]
        key = f"{cf['functionName'] or '(anon)'}:{cf['lineNumber'] + 1}"
        acc[key] = acc.get(key, 0) + dt / 1000
    print("top self time (ms):")
    for key, ms in sorted(acc.items(), key=lambda x: -x[1])[:k]:
        print(f"  {ms:9.0f}  {key}")


WB = r"""
async () => {
  const out = {}, T0 = (name, fn, n) => { const t = performance.now(); for (let i = 0; i < n; i++) fn(i); out[name] = +((performance.now() - t) / n).toFixed(2); };
  out.lines = T.lineage.length; out.tab = tab;
  for (const t of ['tree', 'peoples', 'places', 'wishes', 'results']) { const t1 = performance.now(); showTab(t); out['showTab ' + t + ' (ms)'] = +(performance.now() - t1).toFixed(1); }
  showTab('tree');
  T0('drawTimeline (ms)', () => drawTimeline(), 20);
  T0('drawSide (ms)', () => drawSide(), 20);
  T0('drawPeoples (ms)', () => drawPeoples(), 20);
  T0('drawResults (ms)', () => drawResults(), 20);
  const g = document.querySelector('.grip'); if (g) {
    g.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: 300, clientY: 100 }));
    const t2 = performance.now();
    for (let i = 0; i < 40; i++) window.dispatchEvent(new MouseEvent('mousemove', { clientX: 400 + i * 3, clientY: 100 }));
    out['drag mousemove (ms each, 40)'] = +((performance.now() - t2) / 40).toFixed(2);
    window.dispatchEvent(new MouseEvent('mouseup'));
  }
  const b = document.querySelector('.bar'); if (b) { const t3 = performance.now(); for (let i = 0; i < 10; i++) b.dispatchEvent(new MouseEvent('mousedown', { bubbles: true })); out['select a bar (ms)'] = +((performance.now() - t3) / 10).toFixed(2); }
  return out;
}
"""

GLOBE = Path(__file__).resolve().parent.parent / "viewer" / "globe"


def workbench(port, run):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), headless=True,
                              args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Network.enable")
        enc, reqs, errs = {}, {}, []
        cdp.on("Network.loadingFinished", lambda e: enc.__setitem__(e["requestId"], e["encodedDataLength"]))
        cdp.on("Network.requestWillBeSent", lambda e: reqs.__setitem__(e["requestId"], e["request"]["url"]))
        pg.on("pageerror", lambda e: errs.append(str(e)))
        t0 = time.time()
        pg.goto(f"http://127.0.0.1:{port}/viewer/lineages.html?run={run}&tree=dnd")
        pg.wait_for_function("document.querySelectorAll('.bar').length > 0 && result", timeout=60000)
        print("workbench load_s", round(time.time() - t0, 2))
        for rid, u in reqs.items():
            if rid in enc:
                print("  ", u.replace(f"http://127.0.0.1:{port}", ""), round(enc[rid] / 1e3), "kB")
        pg.wait_for_timeout(1000)
        print(json.dumps(pg.evaluate(WB), indent=1))
        print("page errors", errs[:5])
        b.close()


def main():
    port, run = sys.argv[1], sys.argv[2]
    if "--workbench" in sys.argv:
        return workbench(port, run)
    base = f"http://127.0.0.1:{port}"
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), headless=True,
                              args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Network.enable")
        enc, reqs, errs = {}, {}, []
        cdp.on("Network.loadingFinished", lambda e: enc.__setitem__(e["requestId"], e["encodedDataLength"]))
        cdp.on("Network.requestWillBeSent", lambda e: reqs.__setitem__(e["requestId"], e["request"]["url"]))
        pg.on("pageerror", lambda e: errs.append(str(e) + " | " + (e.stack or "")[:300].replace("\n", " ")))

        def inject(route):  # every export of every globe module, merged, plus the shared state's V
            r = route.fetch()
            mods = sorted(f.stem for f in GLOBE.glob("*.js") if f.name != "main.js")
            head = "".join(f"import * as __{m} from './{m}.js';\n" for m in mods)
            hook = (f"window.__pv = Object.assign({{}}, {', '.join('__' + m for m in mods)}, "
                    "{ get V() { return __state.S.V; }, state: __state.state });")
            body = head + r.text().replace("window.planetViewer.diag = DIAG;", "window.planetViewer.diag = DIAG; " + hook)
            route.fulfill(response=r, body=body)
        pg.route(re.compile(r"/viewer/globe/main\.js$"), inject)
        t0 = time.time()
        pg.goto(f"{base}/viewer/?run={run}&layer=peoples")
        pg.wait_for_function("window.__pv && window.__pv.V && window.__pv.V.layers && !document.getElementById('tlabel').textContent.startsWith('loading')", timeout=120000)
        load = time.time() - t0
        tot = {u.split("/runs/")[1]: enc[rid] for rid, u in reqs.items() if rid in enc and "/runs/" in u}
        print("load_s", round(load, 2), "wire_MB", round(sum(tot.values()) / 1e6, 1), "files", len(tot))
        for k, v in sorted(tot.items(), key=lambda x: -x[1])[:10]:
            print("  ", k, round(v / 1e6, 2), "MB")
        pg.wait_for_timeout(1500)
        prof = next((a.split("=")[1] for a in sys.argv if a.startswith("--profile=")), None)
        if prof:
            cdp.send("Profiler.enable")
            cdp.send("Performance.enable")
            met = lambda: {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
            m0 = met()
            cdp.send("Profiler.start")
            print(pg.evaluate(PHASES[prof]))
            m1 = met()
            print("browser time (ms): " + ", ".join(f"{k.replace('Duration', '')} {1000 * (m1[k] - m0[k]):.0f}" for k in ("ScriptDuration", "LayoutDuration", "RecalcStyleDuration", "TaskDuration")))
            top_self(cdp.send("Profiler.stop")["profile"])
        else:
            print(json.dumps(pg.evaluate(PROBE), indent=1))
            print("pickCheck", pg.evaluate("window.planetViewer.pickCheck ? planetViewer.pickCheck(300) : 'n/a (before the fast pick)'"))
        print("page errors", errs[:5])
        b.close()


main()
