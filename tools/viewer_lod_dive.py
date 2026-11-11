"""A scripted dive on the globe from orbit to the ground (25 m tiles) and back out, in headless Chrome (PW-1688, PW-1673).

    uv run --with playwright python tools/viewer_lod_dive.py PORT WORLD_ID OUT_DIR [--view=lat,lon] [--cursor=fx,fy] [--slow=ms] [--wait=s]
        [--layer=satellite] [--flight=s] [--q=&k=v...] [--embed] [--sw] [--video]

Needs `planet serve --port PORT --no-open` already running (never the owner's port) on a data root with WORLD_ID. The
server builds the tiles in view on demand (planet/tiles.py, PW-1690): with --wait=S, on a world with nothing built,
the dive stops where each level (1 to 4) is first wanted, shoots the view while it builds (the globe, then the parent
stretched, and the "sharpening" badge), waits up to S seconds for the first tile of that level to be drawn, shoots it
arriving, and goes on. --layer: the colour layer (it follows onto the tiles where it has a fine twin). Each shot also
records the hover readout at the screen's centre (the tile's own reading there). --flight=S: after the dive, S seconds
of flying (down, panning low, out, panning across, again), sampling renderer memory every 10 s (report "flight").
Scrolls the wheel over a point a little off the screen's centre, notch by notch, and writes to OUT_DIR:
  *.webm               with --video: the screen recording (Playwright's video; needs `playwright install ffmpeg`)
  NN_<what>.png        screenshots: orbit, each level appearing, a parent showing while its child loads (--slow delays
                       each tile by that many ms), 20 km, the ground at ~1 km (tilted toward the horizon, PW-1696), tilted
                       back to straight down and up again with a right-drag, back at orbit (--q adds to the address, e.g.
                       --q=&outlines=1)
  report.json          memory: the Chrome renderer and GPU processes' resident memory (MB, /proc, the processes under
                       this script) with each shot and flight sample; waits: per level, the seconds from the stop to the first tile drawn and the badge seen; per notch: height over the ground (km), the drawn tiles per level; per frame while moving: the
                       camera's step (largest single-frame turn of its position and of its view direction, and height
                       ratio: a jump shows as an outlier), the tilt per notch, how far the line overlays stand off the
                       drawn ground at each shot (float_km: as built and eased, and draped), fps while
                       moving, renderer memory (geometries, textures, the tiles' bytes, the JS heap)
"""
import json
import os
import sys
import time
from pathlib import Path


def chrome_mb():
    """Resident memory (MB) of the Chrome processes under this script, by kind (renderer, gpu, other): /proc only."""
    out, todo, seen = {}, [os.getpid()], set()
    while todo:
        pid = todo.pop()
        if pid in seen:
            continue
        seen.add(pid)
        for task in Path(f"/proc/{pid}/task").glob("*"):
            try:
                todo += [int(c) for c in (task / "children").read_text().split()]
            except OSError:
                pass
        if pid == os.getpid():
            continue
        try:
            cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            rss = next(int(l.split()[1]) for l in Path(f"/proc/{pid}/status").read_text().splitlines() if l.startswith("VmRSS:"))
        except (OSError, StopIteration):
            continue
        if "chrom" not in cmd:
            continue
        kind = "renderer" if "--type=renderer" in cmd else "gpu" if "--type=gpu-process" in cmd else "other"
        out[kind] = out.get(kind, 0) + rss / 1024
    return {k: round(v, 1) for k, v in out.items()}

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
        url = f"http://127.0.0.1:{port}/viewer/?world={world}.json&view={view}&layer={opt.get('layer', 'satellite')}" + (f"&lodslow={slow}" if slow else "") + ("&embed=1" if "--embed" in sys.argv else "") + opt.get("q", "")
        pg.goto(url)
        pg.wait_for_function("window.planetViewer?.lod?.src && window.planetViewer.diag.n.renders > 0", timeout=120000)
        pg.evaluate("""async () => { const m = await import('/viewer/globe/scene.js');
          window.__scene = m; const f = new m.camera.position.constructor();
          window.__cam = () => { const p = m.camera.position; m.camera.getWorldDirection(f); return [p.length(), p.x / p.length(), p.y / p.length(), p.z / p.length(), f.x, f.y, f.z]; }; }""")
        pg.evaluate("""() => { const P = window.planetViewer, out = window.__trace = []; let last = P.diag.n.renders;
          const tick = (now) => { const c = window.__cam(), r = P.diag.n.renders; out.push([now, ...c, r - last, P.lod.hgKm]); last = r; requestAnimationFrame(tick); };
          requestAnimationFrame(tick); }""")
        time.sleep(1.0)

        def state():
            return pg.evaluate("""() => { const L = window.planetViewer.lod, m = window.__scene, info = m.renderer.info;
              const bd = document.getElementById('lod-badge');
              return { h_km: +L.hgKm.toFixed(3), drawn: L.stats.drawn, byLevel: L.stats.byLevel, kept: L.stats.kept, wanted: L.stats.wanted,
                       queued: L.stats.queued, building: L.stats.building, badge: !!bd && bd.style.opacity === '1',
                       tiles_mb: +(L.stats.bytes / 1e6).toFixed(1), records: L.stats.records, dropped: L.stats.dropped, sat_only: L.stats.satOnly, geometries: info.memory.geometries, textures: info.memory.textures,
                       heap_mb: performance.memory ? +(performance.memory.usedJSHeapSize / 1e6).toFixed(1) : null,
                       near: m.camera.near, far: m.camera.far, tilt_deg: +(window.planetViewer.cam.tilt * 180 / Math.PI).toFixed(2),
                       drape: (({ log, ...x }) => x)(window.planetViewer.drape) }; }""") | {"chrome_mb": chrome_mb()}

        def hover():
            """The info box's text with the pointer at the screen's centre (the tile's reading there, then the cell's)."""
            pg.mouse.move(W // 2 + 3, H // 2 + 3)
            pg.mouse.move(W // 2, H // 2)
            time.sleep(0.2)
            txt = pg.evaluate("document.getElementById('infoText')?.innerText || ''")
            pg.mouse.move(mx, my)
            return txt[:300]

        def bench(frames=60):
            """ms per frame drawn back to back, a pixel read back after each (so the GPU's time counts; no vsync cap)."""
            return pg.evaluate("""(frames) => { const m = window.__scene, gl = m.renderer.getContext(), px = new Uint8Array(4), t0 = performance.now();
              for (let k = 0; k < frames; k++) { m.renderer.render(m.scene, m.camera); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }
              const ms = (performance.now() - t0) / frames; return { frame_ms: +ms.toFixed(2), fps_uncapped: +(1000 / ms).toFixed(0) }; }""", frames)

        def shot(name, note=""):
            f = out / f"{len(rep['shots']):02d}_{name}.png"
            pg.screenshot(path=str(f))
            rep["shots"].append({"file": f.name, "note": note, **state(), **bench(), "hover": hover(),
                                 "float_km": pg.evaluate("window.planetViewer.drapeFloat ? window.planetViewer.drapeFloat() : null")})
            print(f.name, rep["shots"][-1])

        cx, cy = map(float, opt.get("cursor", "0.53,0.47").split(","))
        mx, my = int(W * cx), int(H * cy)  # (a little off the centre: the dive goes toward the cursor)
        pg.mouse.move(mx, my)
        shot("orbit", "the whole planet: cells, as today")
        t0 = time.time()
        marks = [(6000, "level1_appears"), (1500, "level1"), (700, "level2_arriving"), (150, "level2"), (110, "level3_arriving"),
                 (40, "level3"), (12, "level4_arriving"), (2.5, "level4"), (0.4, "ground_300m")]
        arriving = {"level1": 1, "level2_arriving": 2, "level3_arriving": 3, "level4_arriving": 4}
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
                if wait and marks[0][1] in arriving:
                    lv = arriving[marks[0][1]]
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
            if s["h_km"] <= 0.33 or time.time() - t0 > 300:
                break
            pg.mouse.wheel(0, -100)
            time.sleep(0.06)
        time.sleep(2.0)
        if marks:
            shot(marks[-1][1], "the lowest reached")
        if wait:  # (at the ground: until every tile in view is built, then the settled view)
            w0 = time.time()
            while time.time() - w0 < wait:
                s2 = state()
                if not s2["queued"] and not s2["building"] and not s2["badge"]:
                    break
                time.sleep(2.0)
            rep["ground_settle_s"] = round(time.time() - w0, 1)
            time.sleep(1.0)
            shot("ground_settled", f"the ground once the tiles in view were built ({rep['ground_settle_s']:.0f} s)")
        dive_trace = pg.evaluate("window.__trace.splice(0)")
        # the tilt by hand (PW-1696): a right-drag down tilts back to straight down, up toward the horizon again
        for name, dy in (("tilted_back", 400), ("tilted_up", -250)):
            pg.mouse.move(W // 2, H // 2)
            pg.mouse.down(button="right")
            for k in range(20):
                pg.mouse.move(W // 2, H // 2 + dy * (k + 1) // 20)
                time.sleep(0.02)
            pg.mouse.up(button="right")
            time.sleep(1.0)
            shot(name, "a right-drag " + ("down: back toward straight down" if dy > 0 else "up: toward the horizon"))
        pg.mouse.move(mx, my)
        pg.evaluate("window.__trace.splice(0)")
        # back out
        while state()["h_km"] < 15000:
            pg.mouse.wheel(0, 100)
            time.sleep(0.05)
        time.sleep(1.5)
        shot("back_at_orbit", "scrolled back out: the cells again")
        out_trace = pg.evaluate("window.__trace.splice(0)")
        flight = float(opt.get("flight", "0"))
        if flight:  # (down, pan low, out, pan across; memory every 10 s)
            rep["flight"], f0, last, k = [], time.time(), 0.0, 0

            def sample():
                s2 = state()
                rep["flight"].append({"t_s": round(time.time() - f0, 1), **{x: s2[x] for x in ("h_km", "drawn", "kept", "records", "dropped",
                                      "tiles_mb", "geometries", "textures", "heap_mb", "chrome_mb", "queued", "building")}})
                print("flight", rep["flight"][-1])

            def drag(dx, dy, steps=30):
                pg.mouse.move(W // 2, H // 2)
                pg.mouse.down()
                for j in range(steps):
                    pg.mouse.move(W // 2 + dx * (j + 1) // steps, H // 2 + dy * (j + 1) // steps)
                    time.sleep(0.03)
                pg.mouse.up()

            while time.time() - f0 < flight:
                k += 1
                pg.mouse.move(int(W * (0.3 + 0.4 * (k % 3) / 2)), int(H * (0.35 + 0.3 * (k % 2))))
                for _ in range(300):  # down
                    if state()["h_km"] < 0.5 or time.time() - f0 > flight:
                        break
                    pg.mouse.wheel(0, -100)
                    time.sleep(0.05)
                    if time.time() - last > 10:
                        sample(); last = time.time()
                for j in range(8):  # pan low
                    drag(-300 if k % 2 else 300, 120 * (1 if j % 2 else -1))
                    time.sleep(1.5)
                    if time.time() - last > 10:
                        sample(); last = time.time()
                for j in range(40):  # out a way
                    pg.mouse.wheel(0, 100)
                    time.sleep(0.05)
                for j in range(4):  # pan across
                    drag(400, 200 if k % 2 else -200)
                    time.sleep(1.0)
                if time.time() - last > 10:
                    sample(); last = time.time()
            sample()
            shot("after_flight", f"after a {flight:.0f} s flight")
        rep["drape_log"] = pg.evaluate("window.planetViewer.drape.log")  # (each rebuild of the draped overlays: [km, ms, segments, pieces, region km])
        ctx.close()
        b.close()

    def steps(tr):
        """Per drawn frame while the camera moved: the turn (deg) and the height ratio; fps over the moving frames."""
        import math
        turns, views, ratios, dts = [], [], [], []
        prev = None
        for now, r, x, y, z, fx, fy, fz, drawn, hg in tr:
            if prev and (abs(r - prev[1]) > 1e-12 or abs(x - prev[2]) > 1e-12 or abs(fx - prev[7]) > 1e-12):
                dot = max(-1, min(1, x * prev[2] + y * prev[3] + z * prev[4]))
                turns.append(math.degrees(math.acos(dot)))
                views.append((math.degrees(math.acos(max(-1, min(1, fx * prev[7] + fy * prev[8] + fz * prev[9])))), round(hg or 0, 3)))
                if hg and prev[6]:
                    ratios.append(max(hg / prev[6], prev[6] / hg))
                dts.append(now - prev[0])
            prev = (now, r, x, y, z, drawn, hg, fx, fy, fz)
        dts.sort()
        return {"moving_frames": len(dts), "fps_median": round(1000 / dts[len(dts) // 2], 1) if dts else None,
                "fps_p10_frame": round(1000 / dts[int(len(dts) * 0.9)], 1) if dts else None,
                "max_turn_deg": round(max(turns), 4) if turns else None, "max_view_turn_deg": round(max(views)[0], 4) if views else None,
                "view_turns_top": [[round(a, 3), hk] for a, hk in sorted(views, reverse=True)[:5]],
                "max_height_ratio": round(max(ratios), 3) if ratios else None}

    rep["dive"] = steps(dive_trace)
    rep["out"] = steps(out_trace)
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    print("dive", rep["dive"], "out", rep["out"])


if __name__ == "__main__":
    main()
