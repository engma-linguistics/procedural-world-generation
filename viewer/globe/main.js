// The globe viewer (index.html): three.js globe and flat map of a run's frame or a finished world. ES modules, no build:
//   state.js     the shared state (S: what is shown, the mesh, the pick...; state: the view's choices)
//   scene.js     renderer, camera, controls, lights, the clip planes
//   draw.js      drawing helpers (text label sprites)
//   layers.js    LAYERS: every colour layer's label, group, ramp, units, hint, legend, the run layers it needs, which menus show it;
//                cellColors, availableLayers and the lookups derived from the table
//   colours.js   colour helpers the layers use: peoples / tech / resources / fuels colours, lakes, the tints
//   geometry.js  the globe and map meshes (paint), cell positions, ribbons
//   overlays.js  rivers, winds, currents, volcanoes, events, clouds, the overturning
//   axis.js      spin axis and tilt, continent names
//   panel.js     layer buttons, legend, summaries, the layer tooltip
//   timezoom.js  glacial time zooms and finished worlds (jobs)
//   provenance.js where a run / world / zoom came from, the timeline's marks
//   describe.js  the cell's description (info box, More detail)
//   pick.js      hover and click on the globe, the side panel's sections
//   map2d.js     the flat map's projections (projmap.js), overlay switches, the 3D relief controls
//   zoom.js      regional zooms (pick, size, jobs)
//   highlights.js highlights: fetch, list, markers
//   tabs.js      globe | regional zoom tabs, the world navigator (navigator.js)
//   load.js      opening a world or a run, run layers loaded as needed
//   playback.js  the replay
//   select.js    the run / world picker, URL options, favourites
//   main.js      boot, planetViewer (headless checks), the render loop
// every module runs its own top-level code once (its controls' wiring, its defaults), then the boot below
import './scene.js';
import './layers.js';
import './colours.js';
import './geometry.js';
import './overlays.js';
import './axis.js';
import './panel.js';
import './timezoom.js';
import './provenance.js';
import './describe.js';
import './pick.js';
import './map2d.js';
import './zoom.js';
import './highlights.js';
import './tabs.js';
import './load.js';
import './playback.js';
import './select.js';
import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { $, DIAG, camera, controls, fitClip, fitMap, group, relief3d, renderer, resize, scene } from './scene.js';
import { drawTint } from './provenance.js';
import { mouse, pickGlobeCell, ray } from './pick.js';
import { OVERLAY_IDS, reliefLabels } from './map2d.js';
import { showTab } from './tabs.js';
import { loadFailed, setFrame } from './load.js';
import { stop } from './playback.js';
import { paletteReport } from './palettes.js';
import { RAMP_CHANGES } from './layers.js';
import { applyUrlOptions, init, navBarHide, urlp } from './select.js';
// ------------------------------------------------------------ boot
// (after every module has run its own top-level code: the URL's options override their defaults)
addEventListener('resize', () => { resize(); if (state.mode === 'map') fitMap(); if (S.V?.kind === 'run') drawTint(); });
resize();
OVERLAY_IDS.push('hlMarks');  // (highlights.js's markers: ?hlMarks=0 works in the URL)
applyUrlOptions();
// ?legend=dock (PW-1029, a preview for the owner, not a default): the legend docked in the right-hand column above the summary
if (urlp.get('legend') === 'dock') { document.body.classList.add('dockLegend'); $('rightCol').insertBefore($('legend'), $('summary')); }
if (urlp.get('tab') === 'zoom') showTab('zoom', urlp.get('zoom'));
$('reliefVal').textContent = $('relief').value + '×';
reliefLabels();
// With nothing in the address to open, the start screen (start.js, PW-472): the planets made so far and a
// New planet form. It opens things by reloading with ?run= / ?world= / ?world=&tab=zoom&zoom=.
const startScreen = !['run', 'world', 'tab', 'zoom'].some((k) => urlp.has(k));
if (startScreen) {
  navBarHide();
  import('../start.js').then((m) => m.showStart()).then((s) => { if (location.hash === '#new') s.tab('new'); })
    .catch((err) => { console.error(err); document.body.insertAdjacentHTML('beforeend', `<div class="panel" style="top:60px;left:12px">Start screen failed: ${esc(err.message)}</div>`); });
} else init().catch(loadFailed);  // (a plain error card, PW-1044)

// headless timing (console: planetViewer.bench()): replay keyframes back to back, each
// painted (setFrame) and drawn, a pixel read back after each so the GPU's time counts;
// then frames drawn with the camera turning and nothing repainted
window.planetViewer = {
  rampReport: () => RAMP_CHANGES,  // (?ramps=new: the ramps rebuilt to run one way in lightness, before and after; PW-1027)
  paletteReport,  // (the peoples' colours on screen: neighbours alike, colours lost in the ocean; PW-1032)
  // random pointer positions: the globe's fast pick against three's full raycast (PW-679); {tested, hits, mismatches}
  pickCheck(count = 400) {
    const out = { tested: 0, hits: 0, mismatches: 0, undefinedPicks: 0, examples: [] };
    group.updateMatrixWorld(true);
    for (let k = 0; k < count; k++) {
      mouse.set(Math.random() * 1.3 - 0.65, Math.random() * 1.3 - 0.65);
      ray.setFromCamera(mouse, camera);
      const fast = pickGlobeCell(), hit = ray.intersectObject(S.mesh)[0], slow = hit ? S.topo.triCell[hit.faceIndex] : -1;
      if (fast === undefined) { out.undefinedPicks++; continue; }
      out.tested++; if (slow >= 0) out.hits++;
      if (fast !== slow) { out.mismatches++; if (out.examples.length < 5) out.examples.push({ fast, slow, mx: mouse.x, my: mouse.y }); }
    }
    return out;
  },
  bench(frames = 30) {
    const gl = renderer.getContext(), px = new Uint8Array(4), out = {};
    const draw = () => { controls.update(); fitClip(); renderer.render(scene, camera); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
    if (S.V?.kind === 'run') {
      stop();
      const f0 = S.V.frame, nf = S.V.run.frames.length;
      let tp = 0, td = 0;
      state.playing = true;  // (as in a replay: the relief flat-shaded)
      for (let k = 0; k < frames; k++) {
        const t0 = performance.now(); setFrame((f0 + 1 + k) % nf); const t1 = performance.now(); draw();
        tp += t1 - t0; td += performance.now() - t1;
      }
      state.playing = false;
      const ts = performance.now(); setFrame(f0); draw();  // (a still frame: scrubbing, or the replay paused)
      out.still_keyframe_ms = +(performance.now() - ts).toFixed(1);
      Object.assign(out, { keyframe_ms: +((tp + td) / frames).toFixed(1), paint_ms: +(tp / frames).toFixed(1), draw_ms: +(td / frames).toFixed(2),
                           keyframes_per_s: +(1000 * frames / (tp + td)).toFixed(1) });
    }
    const off = camera.position.clone().sub(controls.target), t0 = performance.now(), m = 4 * frames;
    for (let k = 0; k < m; k++) { off.applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.02); camera.position.copy(controls.target).add(off); draw(); }
    const ms = (performance.now() - t0) / m;
    return { ...out, still_frame_ms: +ms.toFixed(2), fps: +(1000 / ms).toFixed(0), relief: relief3d(), mode: state.mode,
             vertices: S.mesh.geometry.attributes.position.count, pixels: [renderer.domElement.width, renderer.domElement.height] };
  },
};

// Draw only when something drawn has changed (PW-415): the camera, any object's transform,
// visibility, geometry, attribute contents (their version), material or texture, or a light.
// Redrawing an unchanged scene every frame bought nothing, and on the owner's Chrome the
// idle redraws were when rivers and marks shimmered (never while the view moved).
let sigPrev = new Float64Array(0), sigNow = new Float64Array(4096), sigN = 0;
const sigPush = (v) => { if (sigN === sigNow.length) { const a = new Float64Array(2 * sigN); a.set(sigNow); sigNow = a; } sigNow[sigN++] = v; };
const sigMat = (m) => { for (const v of m.elements) sigPush(v); };
let attrPrev = new Map(), attrNow = new Map();
function frameChanged() {
  sigN = 0;
  camera.updateMatrixWorld(); scene.updateMatrixWorld();
  sigMat(camera.matrixWorld); sigMat(camera.projectionMatrix);
  const camN = sigN;
  sigPush(renderer.domElement.width); sigPush(renderer.domElement.height);
  attrNow.clear();
  scene.traverse((o) => {
    sigPush(o.id); sigPush(o.visible ? 1 : 0);
    if (!o.visible) return;
    sigMat(o.matrixWorld);
    const g = o.geometry;
    if (g) {
      sigPush(g.id); sigPush(g.drawRange.start); sigPush(g.drawRange.count);
      for (const k in g.attributes) { const a = g.attributes[k], v = a.isInterleavedBufferAttribute ? a.data.version : a.version; sigPush(v); attrNow.set(a, v); }
      if (g.index) { sigPush(g.index.version); attrNow.set(g.index, g.index.version); }
    }
    for (const m of [].concat(o.material || [])) {
      sigPush(m.id); sigPush(m.version); sigPush(m.visible ? 1 : 0); sigPush(m.opacity); sigPush(m.map ? m.map.version : -1);
      if (m.color) { sigPush(m.color.r); sigPush(m.color.g); sigPush(m.color.b); }
      if (m.resolution) { sigPush(m.resolution.x); sigPush(m.resolution.y); }
    }
    if (o.isLight) { sigPush(o.intensity); sigPush(o.color.r); sigPush(o.color.g); sigPush(o.color.b); if (o.groundColor) { sigPush(o.groundColor.r); sigPush(o.groundColor.g); sigPush(o.groundColor.b); } if (o.target) for (const v of o.target.position.toArray()) sigPush(v); }
  });
  sigPush(scene.background?.isColor ? scene.background.getHex() : -1);
  let same = sigN === sigPrev.length, camSame = same;
  for (let i = 0; same && i < sigN; i++) if (sigNow[i] !== sigPrev[i]) { same = false; if (i < camN) camSame = false; }
  if (!camSame && sigN === sigPrev.length) DIAG.n.cam++;
  for (const [a, v] of attrNow) if (attrPrev.get(a) !== undefined && attrPrev.get(a) !== v) DIAG.n.uploads++;
  [attrPrev, attrNow] = [attrNow, attrPrev];
  if (!same) sigPrev = sigNow.slice(0, sigN);
  return !same;
}
// ?dbg=1: a corner readout, refreshed twice a second (counters per second)
let dbgEl = null, dbgAt = 0, dbgN = null;
function dbgReadout(now) {
  if (now - dbgAt < 500) return;
  const gl = renderer.getContext(), dt = (now - dbgAt) / 1000, n = DIAG.n;
  if (!dbgEl) {
    dbgEl = document.createElement('div');
    dbgEl.style.cssText = 'position:fixed;left:6px;bottom:6px;z-index:99;font:11px/1.35 monospace;color:#cfe;background:rgba(0,0,0,.65);padding:4px 6px;pointer-events:none;white-space:pre';
    document.body.appendChild(dbgEl);
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    DIAG.gpu = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
  }
  const rate = (k) => dbgN ? ((n[k] - dbgN[k]) / dt).toFixed(0) : '-';
  const flags = ['logdepth', 'pdb', 'nodamp', 'fixclip', 'offset', 'always', 'blur', 'rehover'].filter((k) => DIAG[k]).join(' ') + (DIAG.noaa ? '' : ' aa') + (DIAG.dpr ? ` dpr=${DIAG.dpr}` : '');
  const cv = renderer.domElement;
  dbgEl.textContent = `${DIAG.gpu}\n${gl instanceof WebGL2RenderingContext ? 'webgl2' : 'webgl1'} depth ${gl.getParameter(gl.DEPTH_BITS)} bits, samples ${gl.getParameter(gl.SAMPLES)}, ` +
    `canvas ${cv.width}x${cv.height} css ${cv.clientWidth}x${cv.clientHeight} dpr ${devicePixelRatio}\n` +
    `near ${camera.near.toPrecision(4)} far ${camera.far.toPrecision(4)} cam ${camera.position.toArray().map((v) => v.toFixed(4)).join(',')}\n` +
    `per s: frames ${rate('frames')} renders ${rate('renders')} cam ${rate('cam')} clip ${rate('clip')} uploads ${rate('uploads')} paints ${rate('paints')} overlays ${rate('overlays')} infobox ${rate('info')}\n` +
    `flags: ${flags || 'none'}`;
  dbgN = { ...n }; dbgAt = now;
}
window.planetViewer.diag = DIAG;
renderer.setAnimationLoop((now) => {
  if (state.tab === 'zoom') { sigPrev = new Float64Array(0); return; }  // the globe is hidden (drawn afresh when it's back)
  if (state.playing && S.V?.kind === 'run' && now - S.lastAdvance > 1000 / +$('fps').value) {
    S.lastAdvance = now;
    if (S.V.frame >= S.V.run.frames.length - 1) stop(); else setFrame(S.V.frame + 1);
  }
  if ($('spin').checked && state.mode === 'globe') group.rotation.y += 0.0015;
  controls.update();
  fitClip();
  if (DIAG.offset && S.mesh) for (const m of S.mesh.userData.mats) if (!m.polygonOffset) Object.assign(m, { polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 4 });
  DIAG.n.frames++;
  if (frameChanged() || DIAG.always) { renderer.render(scene, camera); DIAG.n.renders++; }
  if (DIAG.dbg) dbgReadout(now);
});
