"""A scripted dive on the globe from orbit to ~1 km over the ground and back out, in headless Chrome (PW-1688).

    uv run --with playwright python tools/viewer_lod_dive.py PORT WORLD_ID OUT_DIR [--view=lat,lon] [--cursor=fx,fy] [--slow=ms] [--wait=s] [--embed] [--sw] [--video]

Needs `planet serve --port PORT --no-open` already running (never the owner's port) on a data root with WORLD_ID. The
server builds the tiles in view on demand (planet/tiles.py, PW-1690): with --wait=S, on a world with nothing built,
the dive stops where level 1 and then level 2 are first wanted, shoots the view while they build (the globe, then the
parent stretched, and the "sharpening" badge), waits up to S seconds for the first tile of that level to be drawn,
shoots it arriving, and goes on.
Scrolls the wheel over a point a little off the screen's centre, notch by notch, and writes to OUT_DIR:
  *.webm               with --video: the screen recording (Playwright's video; needs `playwright install ffmpeg`)
  NN_<what>.png        screenshots: orbit, each level appearing, a parent showing while its child loads (--slow delays
                       each tile by that many ms), the ground at ~1 km, back at orbit
  report.json          waits: per level, the seconds from the stop to the first tile drawn and the badge seen; per notch: height over the ground (km), the drawn tiles per level; per frame while moving: the
                       camera's step (largest single-frame turn and height ratio: a jump shows as an outlier), fps while
                       moving, renderer memory (geometries, textures, the tiles' bytes, the JS heap)
"""
import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

def main():
    port, world, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    opt = dict(a[2:].split("=", 1) for a in sys.argv[4:] if a.startswith("--") and "=" in a)
    view = opt.get("view", "4,88")
    slow = int(opt.get("slow", "0"))
    out.mkdir(parents=True, exist_ok=True)
    gpu = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] if "--sw" in sys.argv else ["--use-gl=angle", "--use-angle=gl", "--enable-gpu"]
    W, H = 1600, 1000
    wait = float(opt.get("wait", "0"))
    rep = {"world": world, "view": view, "slow_ms": slow, "wait_s": wait, "notches": [], "shots": [], "waits": []}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), headless=True,
                              args=["--headless=new", "--ignore-gpu-blocklist", "--enable-precise-memory-info", *gpu])
        video = {"record_video_dir": str(out), "record_video_size": {"width": W // 2, "height": H // 2}} if "--video" in sys.argv else {}
        ctx = b.new_context(viewport={"width": W, "height": H}, **video)
        pg = ctx.new_page()
        pg.on("console", lambda m: m.type in ("error", "warning") and print("[page]", m.text))
        pg.on("pageerror", lambda e: print("[pageerror]", e))
        pg.on("response", lambda r: r.status >= 400 and print("[http]", r.status, r.url))
        # the camera, reached through the module graph (the page's scene module is not on window)
        pg.add_init_script("window.__cam = () => [0, 0, 0];")
        url = f"http://127.0.0.1:{port}/viewer/?world={world}.json&view={view}&layer=satellite" + (f"&lodslow={slow}" if slow else "") + ("&embed=1" if "--embed" in sys.argv else "")
        pg.goto(url)
        pg.wait_for_function("window.planetViewer?.lod?.src && window.planetViewer.diag.n.renders > 0", timeout=120000)
        pg.evaluate("""async () => { const m = await import('/viewer/globe/scene.js');
          window.__scene = m; window.__cam = () => { const p = m.camera.position; return [p.length(), p.x / p.length(), p.y / p.length(), p.z / p.length()]; }; }""")
        pg.evaluate("""() => { const P = window.planetViewer, out = window.__trace = []; let last = P.diag.n.renders;
          const tick = (now) => { const c = window.__cam(), r = P.diag.n.renders; out.push([now, ...c, r - last, P.lod.hgKm]); last = r; requestAnimationFrame(tick); };
          requestAnimationFrame(tick); }""")
        time.sleep(1.0)

        def state():
            return pg.evaluate("""() => { const L = window.planetViewer.lod, m = window.__scene, info = m.renderer.info;
              const bd = document.getElementById('lod-badge');
              return { h_km: +L.hgKm.toFixed(3), drawn: L.stats.drawn, byLevel: L.stats.byLevel, kept: L.stats.kept, wanted: L.stats.wanted,
                       queued: L.stats.queued, building: L.stats.building, badge: !!bd && bd.style.opacity === '1',
                       tiles_mb: +(L.stats.bytes / 1e6).toFixed(1), geometries: info.memory.geometries, textures: info.memory.textures,
                       heap_mb: performance.memory ? +(performance.memory.usedJSHeapSize / 1e6).toFixed(1) : null,
                       near: m.camera.near, far: m.camera.far }; }""")

        def bench(frames=60):
            """ms per frame drawn back to back, a pixel read back after each (so the GPU's time counts; no vsync cap)."""
            return pg.evaluate("""(frames) => { const m = window.__scene, gl = m.renderer.getContext(), px = new Uint8Array(4), t0 = performance.now();
              for (let k = 0; k < frames; k++) { m.renderer.render(m.scene, m.camera); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }
              const ms = (performance.now() - t0) / frames; return { frame_ms: +ms.toFixed(2), fps_uncapped: +(1000 / ms).toFixed(0) }; }""", frames)

        def shot(name, note=""):
            f = out / f"{len(rep['shots']):02d}_{name}.png"
            pg.screenshot(path=str(f))
            rep["shots"].append({"file": f.name, "note": note, **state(), **bench()})
            print(f.name, rep["shots"][-1])

        cx, cy = map(float, opt.get("cursor", "0.53,0.47").split(","))
        mx, my = int(W * cx), int(H * cy)  # (a little off the centre: the dive goes toward the cursor)
        pg.mouse.move(mx, my)
        shot("orbit", "the whole planet: cells, as today")
        t0 = time.time()
        marks = [(6000, "level1_appears"), (1500, "level1"), (700, "level2_arriving"), (150, "level2"), (20, "low"), (1.5, "ground_1km")]
        while True:
            s = state()
            rep["notches"].append(s)
            if marks and s["h_km"] < marks[0][0]:
                time.sleep(0.15 if slow else 1.0)
                shot(marks[0][1], f"below {marks[0][0]} km")
                if slow and marks[0][1] == "level2_arriving":  # (the parent stretched while its children load, then their fade-in)
                    time.sleep(slow / 1000 + 0.15)
                    shot("level2_fading_in", "the first children arriving, fading in over the parent")
                    time.sleep(2.0)
                    shot("level2_arrived", "children in")
                if wait and marks[0][1] in ("level1", "level2_arriving"):
                    lv = 1 if marks[0][1] == "level1" else 2
                    w0, badge = time.time(), False
                    while time.time() - w0 < wait:
                        s2 = state()
                        badge |= s2["badge"]
                        if (s2["byLevel"] or {}).get(str(lv), 0) > 0:
                            break
                        if not badge or time.time() - w0 < 3:
                            time.sleep(1.0)
                            if time.time() - w0 >= 2 and not any(x["file"].endswith(f"level{lv}_building.png") for x in rep["shots"]):
                                shot(f"level{lv}_building", f"level {lv} wanted and building: " +
                                     ("the globe's cells" if lv == 1 else "the level-1 parent stretched") + ", the badge on")
                            continue
                        time.sleep(2.0)
                    got = time.time() - w0
                    rep["waits"].append({"level": lv, "seconds": round(got, 1), "badge_seen": badge,
                                         "arrived": (state()["byLevel"] or {}).get(str(lv), 0) > 0})
                    time.sleep(1.0)  # (the fade-in)
                    shot(f"level{lv}_arrived", f"the first level-{lv} tile drawn, {got:.0f} s after the stop")
                    t0 += got
                marks.pop(0)
            if s["h_km"] <= 0.35 or time.time() - t0 > 300:
                break
            pg.mouse.wheel(0, -100)
            time.sleep(0.06)
        time.sleep(2.0)
        if marks:
            shot(marks[-1][1], "the lowest reached")
        dive_trace = pg.evaluate("window.__trace.splice(0)")
        # back out
        while state()["h_km"] < 15000:
            pg.mouse.wheel(0, 100)
            time.sleep(0.05)
        time.sleep(1.5)
        shot("back_at_orbit", "scrolled back out: the cells again")
        out_trace = pg.evaluate("window.__trace.splice(0)")
        ctx.close()
        b.close()

    def steps(tr):
        """Per drawn frame while the camera moved: the turn (deg) and the height ratio; fps over the moving frames."""
        import math
        turns, ratios, dts = [], [], []
        prev = None
        for now, r, x, y, z, drawn, hg in tr:
            if prev and (abs(r - prev[1]) > 1e-12 or abs(x - prev[2]) > 1e-12):
                dot = max(-1, min(1, x * prev[2] + y * prev[3] + z * prev[4]))
                turns.append(math.degrees(math.acos(dot)))
                if hg and prev[6]:
                    ratios.append(max(hg / prev[6], prev[6] / hg))
                dts.append(now - prev[0])
            prev = (now, r, x, y, z, drawn, hg)
        dts.sort()
        return {"moving_frames": len(dts), "fps_median": round(1000 / dts[len(dts) // 2], 1) if dts else None,
                "fps_p10_frame": round(1000 / dts[int(len(dts) * 0.9)], 1) if dts else None,
                "max_turn_deg": round(max(turns), 4) if turns else None, "max_height_ratio": round(max(ratios), 3) if ratios else None}

    rep["dive"] = steps(dive_trace)
    rep["out"] = steps(out_trace)
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    print("dive", rep["dive"], "out", rep["out"])


if __name__ == "__main__":
    main()
