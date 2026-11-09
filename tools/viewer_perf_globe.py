"""Headless timings of the globe viewer on a finished world, at any grid level (lane 91, PW-1198 first step).

    uv run --with playwright python tools/viewer_perf_globe.py PORT WORLD_ID [--layer=biome] [--sw] [--profile]

Opens http://127.0.0.1:PORT/viewer/?world=WORLD_ID.json in headless Chrome on the real GPU (ANGLE on OpenGL, as on
the owner's Chrome; --sw: SwiftShader instead) and reports: the load (wall time, wire MB, the world's and the grid's
fetch + JSON parse, the JS heap), then in the page: prepareGrid, buildTopology, cellColors, paint, a forced overlay
rebuild, a layer switch end to end (paint + the next drawn frame), hovering, and frames drawn (a pixel read back after
each, so the GPU's time counts) with the camera turning, from the default distance and close in (1.3 radii).
--profile: the CDP sampling profiler over the load and over the probe (top self time).
--fingerprint: hashes of the mesh in each view; --layerhash: hashes of every layer's numbers (compare two versions).
Needs `planet serve --port PORT --no-open` already running (never the owner's port). The page's module scope is
reached as in tools/viewer_perf.py: a hook injected into the served globe/main.js.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

GLOBE = Path(__file__).resolve().parent.parent / "viewer" / "globe"

# --fingerprint: hashes of the mesh's buffers (topology, positions, colours, normals) in each view, to check that a
# rewrite of the mesh code draws the same thing (compare the output of two versions)
FINGERPRINT = r"""
async ([layers, equirect]) => {
  const P = window.__pv, { state, S } = P, out = {};
  if (equirect) P.proj.name = 'equirect';  // (the flat map as the live three.js map, not the Equal Earth canvas)
  const raf = () => new Promise((r) => requestAnimationFrame(() => r()));
  const h = (a) => { if (!a) return null; const u = new Uint8Array(a.buffer, a.byteOffset, a.byteLength); let x = 2166136261 >>> 0;
    for (let i = 0; i < u.length; i++) { x ^= u[i]; x = Math.imul(x, 16777619) >>> 0; } return `${a.constructor.name}[${a.length}]:${x.toString(16)}`; };
  const T = (a) => (a && !ArrayBuffer.isView(a) ? Int32Array.from(a) : a);
  const snap = (key) => {
    const t = S.topo, g = S.mesh.geometry, at = g.attributes;
    out[key] = { vCell: h(t.vCell), vCorner: h(t.vCorner), vSrc: h(t.vSrc), base: h(t.base), triCell: h(T(t.triCell)), triStart: h(t.triStart),
      cStart: h(t.cStart), cList: h(t.cList), index: h(g.index?.array), position: h(at.position.array), color: h(at.color.array),
      normal: h(at.normal?.array), maxR: t.maxR, minR: t.minR, R: h(P.V.R) };
    const pc = document.getElementById('projCanvas');
    if (P.proj.on && pc.width) { out[key].projCanvas = h(pc.getContext('2d').getImageData(0, 0, pc.width, pc.height).data); out[key].png = pc.toDataURL(); }
  };
  const view = async (key, setup) => { await setup(); await raf(); await raf(); snap(key); };
  await view('globe ' + layers[0], async () => {});
  await view('globe ' + layers[1], async () => { state.layer = layers[1]; await P.refresh(P.paint); });
  document.getElementById('smooth').click();
  await view('globe smooth ' + layers[1], async () => { await P.refresh(P.paint); });
  document.getElementById('smooth').click();
  await view('map ' + layers[1], async () => { document.querySelector('#modeSeg [data-v="map"]').click(); });
  await view('map ' + layers[0], async () => { state.layer = layers[0]; await P.refresh(P.paint); });
  await view('globe again ' + layers[0], async () => { document.querySelector('#modeSeg [data-v="globe"]').click(); });
  await view('globe 3D relief ' + layers[0], async () => { document.getElementById('relief3d').click(); });
  await view('globe 3D relief ' + layers[1], async () => { state.layer = layers[1]; await P.refresh(P.paint); });
  await view('map 3D relief ' + layers[1], async () => { document.querySelector('#modeSeg [data-v="map"]').click(); });
  return out;
}
"""

# --layerhash: a hash of every layer of the open world as the viewer holds it (as float64; a [cells, 3] layer flat),
# to check that a change to how worlds are stored or read gives the viewer the same numbers (PW-1209)
LAYERHASH = r"""
async () => {
  const L = window.__pv.V.layers, out = {};
  const h = (a) => { const f = Float64Array.from(a.flat ? a.flat() : a), u = new Uint8Array(f.buffer); let x = 2166136261 >>> 0;
    for (let i = 0; i < u.length; i++) { x ^= u[i]; x = Math.imul(x, 16777619) >>> 0; } return x.toString(16) + ':' + f.length; };
  for (const k of Object.keys(L).sort()) out[k] = h(L[k]);
  return out;
}
"""

# --heap: the JS heap (after a full GC) after each step, to find what keeps memory
HEAP = r"""
async ([layers]) => {
  const P = window.__pv, { state } = P, out = [], raf = () => new Promise((r) => requestAnimationFrame(() => r()));
  const mb = (k) => { gc(); gc(); out.push([k, +(performance.memory.usedJSHeapSize / 1e6).toFixed(0)]); };
  const click = async (sel) => { document.querySelector(sel).click(); await raf(); await raf(); };
  mb('loaded');
  for (let r = 0; r < 2; r++) {
    state.layer = layers[1]; await P.refresh(P.paint); await raf(); mb('layer ' + layers[1]);
    state.layer = layers[0]; await P.refresh(P.paint); await raf(); mb('layer ' + layers[0]);
    await click('#modeSeg [data-v="map"]'); mb('flat map');
    await click('#modeSeg [data-v="globe"]'); mb('globe');
    document.getElementById('relief3d').click(); await raf(); await raf(); mb('3D relief on');
    document.getElementById('relief3d').click(); await raf(); await raf(); mb('3D relief off');
    P.buildTopology(); P.paint(); await raf(); mb('buildTopology + paint');
  }
  return out;
}
"""

PROBE = r"""
async ([layers]) => {
  const P = window.__pv, { state } = P, V = P.V, out = {};
  const raf = () => new Promise((r) => requestAnimationFrame(() => r()));
  const T = (name, fn, n = 1) => { fn(); const t = performance.now(); for (let i = 0; i < n; i++) fn(i); out[name] = +((performance.now() - t) / n).toFixed(1); };
  out.cells = V.n; out.vertices = P.S.mesh.geometry.attributes.position.count; out.triangles = P.S.mesh.geometry.index.count / 3;
  gc(); out['heap after load, after a GC (MB)'] = +(performance.memory.usedJSHeapSize / 1e6).toFixed(0);
  // the world and grid files again (the browser's copy: a 304, so this is parse time mostly)
  const wurl = '../worlds/' + V.id + '.json', gurl = '../grids/L' + V.level + '.json';
  {
    let t = performance.now(); const txt = await (await fetch(wurl)).text(); out['world fetch as text (ms)'] = +(performance.now() - t).toFixed(0);
    out['world text (M chars)'] = +(txt.length / 1e6).toFixed(1);
    t = performance.now(); JSON.parse(txt); out['world JSON.parse (ms)'] = +(performance.now() - t).toFixed(0);
    t = performance.now(); await (await fetch(gurl)).json(); out['grid fetch+json (ms)'] = +(performance.now() - t).toFixed(0);
  }
  T('prepareGrid (ms)', () => P.prepareGrid(V.grid), 1);
  T('buildTopology (ms)', () => P.buildTopology(), 1);
  P.paint();
  for (const l of layers) { state.layer = l; T(`cellColors ${l} (ms)`, () => P.cellColors(l), 3); }
  state.layer = layers[0];
  T('paint (ms)', () => P.paint(), 3);
  T('buildOverlays forced (ms)', () => P.buildOverlays(), 3);
  T('renderLegend (ms)', () => P.renderLegend(), 3);
  // a layer switch as the picker does it (state.layer, refresh(paint)), to the next frame drawn
  await raf(); await raf();
  for (const l of [...layers.slice(1), layers[0]]) {
    const t0 = performance.now(); state.layer = l; await P.refresh(P.paint); await raf(); await raf();
    out[`switch to ${l}, to drawn (ms)`] = +(performance.now() - t0).toFixed(0);
  }
  // hover: pointer moves over the globe
  const cv = document.getElementById('c'), r = cv.getBoundingClientRect();
  let h0 = performance.now();
  for (let i = 0; i < 100; i++) cv.dispatchEvent(new PointerEvent('pointermove', { clientX: r.left + r.width / 2 + (i % 20) * 7, clientY: r.top + r.height / 2 + Math.floor(i / 20) * 9, bubbles: true }));
  out['pointermove (ms each)'] = +((performance.now() - h0) / 100).toFixed(2);
  // frames drawn with the camera turning (GPU time included: a pixel read back each frame)
  const { renderer, scene, camera, controls, fitClip } = P, gl = renderer.getContext(), px = new Uint8Array(4);
  const draw = () => { controls.update(); fitClip(); renderer.render(scene, camera); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
  const turn = (dist, m, key) => {
    camera.position.setLength(dist); draw(); draw();
    const off = camera.position.clone().sub(controls.target), t1 = performance.now();
    for (let k = 0; k < m; k++) { off.applyAxisAngle(new P.THREE.Vector3(0, 1, 0), 0.02); camera.position.copy(controls.target).add(off); draw(); }
    out[key] = +((performance.now() - t1) / m).toFixed(2);
  };
  const d0 = camera.position.length();
  turn(d0, 60, `frame turning, distance ${d0.toFixed(2)} (ms)`);
  turn(1.3, 60, 'frame turning, distance 1.30 (ms)');
  camera.position.setLength(d0);
  out.info = { renders: renderer.info.render, memory: renderer.info.memory };
  // the flat map (Equal Earth canvas by default) and back, a layer switch on it, the 3D relief on the globe
  const click = async (sel) => { const t0 = performance.now(); document.querySelector(sel).click(); await raf(); await raf(); return +(performance.now() - t0).toFixed(0); };
  out['to flat map, to drawn (ms)'] = await click('#modeSeg [data-v="map"]');
  { const t0 = performance.now(); state.layer = layers[1]; await P.refresh(P.paint); await raf(); await raf(); out[`flat map: switch to ${layers[1]} (ms)`] = +(performance.now() - t0).toFixed(0); }
  { const t0 = performance.now(); state.layer = layers[0]; await P.refresh(P.paint); await raf(); await raf(); out[`flat map: switch to ${layers[0]} (ms)`] = +(performance.now() - t0).toFixed(0); }
  out['back to globe, to drawn (ms)'] = await click('#modeSeg [data-v="globe"]');
  const r3 = document.getElementById('relief3d');
  if (r3) {
    let t0 = performance.now(); r3.click(); await raf(); await raf(); out['3D relief on, to drawn (ms)'] = +(performance.now() - t0).toFixed(0);
    t0 = performance.now(); state.layer = layers[1]; await P.refresh(P.paint); await raf(); await raf(); out[`3D relief: switch to ${layers[1]} (ms)`] = +(performance.now() - t0).toFixed(0);
    t0 = performance.now(); r3.click(); await raf(); await raf(); out['3D relief off, to drawn (ms)'] = +(performance.now() - t0).toFixed(0);
    state.layer = layers[0]; await P.refresh(P.paint);
  }
  camera.position.set(0, 0.6, 3.4);
  // the live loop: rAF gaps while the camera turns 3 s (OrbitControls' own loop, frameChanged and all)
  const gaps = []; let last = performance.now(); const p0 = last;
  await new Promise((res) => { const tick = (now) => { const off = camera.position.clone(); off.applyAxisAngle(new P.THREE.Vector3(0, 1, 0), 0.01); camera.position.copy(off);
    gaps.push(now - last); last = now; if (now - p0 < 3000) requestAnimationFrame(tick); else res(); }; requestAnimationFrame(tick); });
  gaps.shift();
  gaps.sort((a, b) => a - b);
  out.live_turn_3s = { rafs: gaps.length, median_ms: +gaps[gaps.length >> 1].toFixed(1), p95_ms: +gaps[Math.floor(gaps.length * 0.95)].toFixed(1), max_ms: +gaps[gaps.length - 1].toFixed(1) };
  gc(); out['heap at the end, after a GC (MB)'] = +(performance.memory.usedJSHeapSize / 1e6).toFixed(0);
  return out;
}
"""


def top_self(profile, k=22):
    nodes = {n["id"]: n for n in profile["nodes"]}
    acc = {}
    for nid, dt in zip(profile["samples"], profile["timeDeltas"]):
        cf = nodes[nid]["callFrame"]
        key = f"{cf['functionName'] or '(anon)'} {cf['url'].rsplit('/', 1)[-1]}:{cf['lineNumber'] + 1}"
        acc[key] = acc.get(key, 0) + dt / 1000
    for key, ms in sorted(acc.items(), key=lambda x: -x[1])[:k]:
        print(f"  {ms:9.0f}  {key}")


def renderer_rss(browser) -> int:
    """The renderer processes' resident memory: unlike the JS heap, it counts typed arrays' buffers."""
    info = browser.new_browser_cdp_session().send("SystemInfo.getProcessInfo")["processInfo"]
    rss = 0
    for p in info:
        if p["type"] == "renderer":
            try:
                rss += int(next(x for x in open(f"/proc/{p['id']}/status") if x.startswith("VmRSS")).split()[1]) * 1024
            except (OSError, StopIteration):
                pass
    return rss


def main():
    port, world = sys.argv[1], sys.argv[2]
    layer = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--layer=")), "biome")
    extra = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--url=")), "")  # e.g. --url='&proj=equirect'

    prof = "--profile" in sys.argv
    gpu = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] if "--sw" in sys.argv else ["--use-gl=angle", "--use-angle=gl", "--enable-gpu"]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), headless=True,
                              args=["--headless=new", "--ignore-gpu-blocklist", "--enable-precise-memory-info", "--js-flags=--expose-gc", *gpu, *os.environ.get("CHROME_ARGS", "").split()])
        pg = b.new_page(viewport={"width": 1600, "height": 1000})
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Network.enable")
        enc, reqs, errs = {}, {}, []
        cdp.on("Network.loadingFinished", lambda e: enc.__setitem__(e["requestId"], e["encodedDataLength"]))
        cdp.on("Network.requestWillBeSent", lambda e: reqs.__setitem__(e["requestId"], e["request"]["url"]))
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append("console: " + m.text[:300]))

        def inject(route):
            r = route.fetch()
            mods = sorted(f.stem for f in GLOBE.glob("*.js") if f.name != "main.js")
            head = "".join(f"import * as __{m} from './{m}.js';\n" for m in mods) + "import * as __THREE from 'three';\n"
            hook = (f"window.__pv = Object.assign({{ THREE: __THREE }}, {', '.join('__' + m for m in mods)}, "
                    "{ S: __state.S, state: __state.state }); "
                    "Object.defineProperty(window.__pv, 'V', { get() { return __state.S.V; } });")
            body = head + r.text().replace("window.planetViewer.diag = DIAG;", "window.planetViewer.diag = DIAG; " + hook)
            route.fulfill(response=r, body=body)
        pg.route(re.compile(r"/viewer/globe/main\.js$"), inject)
        if prof:
            cdp.send("Profiler.enable")
            cdp.send("Profiler.setSamplingInterval", {"interval": 200})
            cdp.send("Profiler.start")
        t0 = time.time()
        pg.goto(f"http://127.0.0.1:{port}/viewer/?world={world}.json&layer={layer}&spin=0{extra}")
        try:
            pg.wait_for_function("window.__pv && window.__pv.V && window.__pv.S.mesh && window.__pv.V.id && window.planetViewer.diag.n.renders > 0",
                                 timeout=float(os.environ.get("LOAD_TIMEOUT_S", 300)) * 1000, polling=50)
        except Exception:
            print("not loaded; page errors:", errs[:5])
            print(pg.evaluate("({ pv: !!window.__pv, V: !!window.__pv?.V, mesh: !!window.__pv?.S?.mesh, info: document.getElementById('infoText')?.textContent.slice(0, 300), "
                              "renders: window.planetViewer?.diag?.n?.renders })"))
            raise
        load = time.time() - t0
        marks = pg.evaluate("[...(planetViewer.diag.load || []), ['seen drawn', Math.round(performance.now())]]")
        print("load stages (ms since the page opened):", ", ".join(f"{k} {v}" for k, v in marks))
        tot, nl = {}, 0  # (a world's layer files, PW-1209, as one entry)
        for rid, u in reqs.items():
            if rid in enc and ("/worlds/" in u or "/grids/" in u):
                k = "layer files" if "/worlds/layers/" in u else u.rsplit("/", 1)[-1]
                nl += k == "layer files"
                tot[k] = tot.get(k, 0) + enc[rid]
        print(f"load to first globe drawn: {load:.2f} s; data on the wire {sum(tot.values()) / 1e6:.1f} MB:",
              ", ".join(f"{k}{f' ({nl})' if k == 'layer files' else ''} {v / 1e6:.1f} MB" for k, v in tot.items()))
        pg.evaluate("gc()")
        print(f"after load: JS heap {pg.evaluate('performance.memory.usedJSHeapSize') / 1e6:.0f} MB (limit {pg.evaluate('performance.memory.jsHeapSizeLimit') / 1e6:.0f}); renderer memory "
              f"(RSS, typed arrays included) {renderer_rss(b) / 1e6:.0f} MB")
        if prof:
            print("load, top self time (ms):")
            top_self(cdp.send("Profiler.stop")["profile"])
        if "--load-only" in sys.argv:
            return b.close()
        pg.wait_for_timeout(1500)
        gl = pg.evaluate("(() => { const gl = window.__pv.renderer.getContext(), e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : ''; })()")
        print("GPU:", gl)
        if prof:
            cdp.send("Profiler.start")
        layers = [layer, "elevation", "temperature"]
        res = (pg.evaluate(LAYERHASH) if "--layerhash" in sys.argv else
               pg.evaluate(FINGERPRINT if "--fingerprint" in sys.argv else HEAP if "--heap" in sys.argv else PROBE, [layers, "--equirect" in sys.argv]))
        snap = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--snapdir=")), None)  # (the canvases as PNGs)
        for k, v in (res.items() if isinstance(res, dict) else []):
            png = v.pop("png", None) if isinstance(v, dict) else None
            if png and snap:
                import base64
                Path(snap, re.sub(r"\W+", "_", k) + ".png").write_bytes(base64.b64decode(png.split(",", 1)[1]))
        print(json.dumps(res, indent=None if "--heap" in sys.argv else 1))
        if prof:
            print("probe, top self time (ms):")
            top_self(cdp.send("Profiler.stop")["profile"])
        print("page errors", errs[:5])
        b.close()


main()
