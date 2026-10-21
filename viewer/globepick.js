// The start screen's globe picker (PW-546): one planet as a slowly turning 3D globe with prev/next buttons,
// left/right arrow keys, its name and an Open button. three.js and the planet's texture (the server's
// equirect thumbnail, /api/thumb?...&proj=equirect&w=1024) are loaded only when the picker is first shown,
// one texture at a time; the previous planet's texture is disposed when stepping, everything when hidden.

const CSS = `
#start .gp { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 14px; padding: 8px; }
#start .gp .stage { display: grid; grid-template-columns: 44px 1fr 44px; align-items: center; gap: 6px; }
#start .gp .stage button { height: 56px; font-size: 22px; }
#start .gp .view { position: relative; height: min(46vh, 340px); min-height: 200px; outline: none; }
#start .gp canvas { width: 100%; height: 100%; display: block; touch-action: pan-y; }
#start .gp .view .msg { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--muted); text-align: center; padding: 12px; }
#start .gp .cap { display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap; margin-top: 6px; }
#start .gp .cap .nm { font-weight: 600; overflow-wrap: anywhere; }
#start .gp .cap .meta { color: var(--muted); font-size: 12px; }
`;

let cssDone = false;
let threeP = null;
const loadThree = () => (threeP ||= import('three'));

// getPlanets() -> the planets list; opener(planet) -> URL to open; meta(planet) -> a short text.
export function createGlobePicker(host, getPlanets, opener, meta) {
  if (!cssDone) { cssDone = true; const st = document.createElement('style'); st.textContent = CSS; document.head.append(st); }
  const box = document.createElement('div');
  box.className = 'gp'; box.hidden = true;
  box.innerHTML = `<div class="stage"><button class="pl-btn" data-d="-1" aria-label="Previous planet" title="Previous (left arrow)">&#8249;</button>
    <div class="view" tabindex="0" aria-label="Planet globe: left and right arrow keys step through the planets"><div class="msg">Loading...</div></div>
    <button class="pl-btn" data-d="1" aria-label="Next planet" title="Next (right arrow)">&#8250;</button></div>
    <div class="cap"><span class="nm"></span><span class="meta"></span><button class="pl-btn primary" data-open>Open</button></div>`;
  host.append(box);
  const view = box.querySelector('.view'), nm = box.querySelector('.nm'), mt = box.querySelector('.meta');
  let idx = 0, gl = null, shown = false, token = 0, raf = 0, ro = null;

  const say = (t) => { let m = view.querySelector('.msg'); if (!m) { m = document.createElement('div'); m.className = 'msg'; view.append(m); } m.textContent = t; };
  const unsay = () => view.querySelector('.msg')?.remove();

  let glP = null;  // (concurrent callers share one setup)
  const ensureGl = () => (glP ||= setupGl().catch((e) => { glP = null; throw e; }));
  async function setupGl() {
    const THREE = await loadThree();
    if (!shown) throw new Error('hidden');  // (hidden while three.js was loading)
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    view.append(renderer.domElement);
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(32, 1, 0.1, 20);
    camera.position.set(0, 0.25, 3.6); camera.lookAt(0, 0, 0);
    const geo = new THREE.SphereGeometry(1, 64, 48);
    const mat = new THREE.MeshBasicMaterial({ color: 0x223044 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.z = 0.2;  // a gentle axial tilt
    scene.add(mesh);
    const g = gl = { THREE, renderer, scene, camera, mesh, mat, geo, tex: null, last: performance.now(), dead: false };
    const fit = () => { const w = view.clientWidth, h = view.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
      camera.position.set(0, 0.25, 1.12 / Math.sin(camera.fov * Math.PI / 360) / Math.min(1, camera.aspect)); camera.lookAt(0, 0, 0); };  // (the whole globe fits a narrow view too)
    ro = new ResizeObserver(fit); ro.observe(view); fit();
    const tick = (t) => {
      if (g.dead) return;
      raf = requestAnimationFrame(tick);
      if (document.hidden) { g.last = t; return; }
      g.mesh.rotation.y += (t - g.last) / 1000 * 0.35; g.last = t;
      renderer.render(scene, camera);
    };
    raf = requestAnimationFrame(tick);
    return g;
  }

  async function showCurrent() {
    const planets = getPlanets();
    if (!planets.length) { say('No planets yet.'); nm.textContent = ''; mt.textContent = ''; return; }
    idx = (idx % planets.length + planets.length) % planets.length;
    const p = planets[idx], my = ++token;
    nm.textContent = p.name; mt.textContent = `${idx + 1} / ${planets.length} · ${meta(p)}`;
    if (!String(p.thumb || '').startsWith('/api/thumb')) { say('No preview for this planet.'); return; }
    let g;
    try { g = await ensureGl(); } catch (e) { if (shown) say('The globe needs WebGL, which is not available here.'); return; }
    const url = p.thumb + '&proj=equirect&w=1024';
    try {
      const tex = await new Promise((ok, no) => new g.THREE.TextureLoader().load(url, ok, undefined, no));
      if (my !== token || !shown) { tex.dispose(); return; }  // stepped on or hidden while loading
      tex.colorSpace = g.THREE.SRGBColorSpace; tex.anisotropy = 4;
      g.tex?.dispose(); g.tex = tex;
      g.mat.map = tex; g.mat.color.set(0xffffff); g.mat.needsUpdate = true;
      unsay();
    } catch { if (my === token) say('Could not load this planet\'s picture.'); }
  }

  function dispose() {
    cancelAnimationFrame(raf); ro?.disconnect(); ro = null;
    glP = null;
    if (gl) { gl.dead = true; gl.tex?.dispose(); gl.mat.dispose(); gl.geo.dispose(); gl.renderer.dispose(); gl.renderer.domElement.remove(); gl = null; }
  }
  const step = (d) => { idx += d; showCurrent(); };
  box.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.d) step(+b.dataset.d);
    if (b.dataset.open !== undefined) { const p = getPlanets()[idx]; if (p) location.href = opener(p); }
  });
  const onKey = (e) => {
    if (!shown || e.altKey || e.ctrlKey || e.metaKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    if (box.closest('[hidden]') || document.querySelector('#start .modal')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
  };
  document.addEventListener('keydown', onKey);

  return {
    show() { if (shown) return; shown = true; box.hidden = false; showCurrent(); },
    hide() { shown = false; token++; box.hidden = true; dispose(); },  // (frees the WebGL context too)
    refresh() { if (shown) showCurrent(); },
  };
}
