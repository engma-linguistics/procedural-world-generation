import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import * as Relief from '../relief.js';
import { wheelZoom } from '../wheelzoom.js';
import { S, state } from './state.js';
export const $ = (id) => document.getElementById(id);
export const R_EARTH = 6371000;
export const CMYR = 637.1;  // rad/Myr on the unit sphere -> cm/yr

// ------------------------------------------------------------ three setup
// MSAA is off by default: on the owner's Chrome (Linux, NVIDIA, ANGLE on OpenGL) it made rivers
// and marks shimmer while the view sat still, and ?noaa=1 alone cured it (PW-415; Firefox never
// shimmered). ?aa=1 turns it back on. Other diagnostic switches, all off by default: ?logdepth=1
// (logarithmic depth buffer), ?pdb=1 (preserveDrawingBuffer: Chrome then
// copies the frame instead of swapping buffers), ?dpr=1 (pixel ratio), ?nodamp=1 (no orbit
// damping), ?fixclip=1 (the old fixed near 0.01 / far 100), ?offset=1 (polygon offset pushes
// the ground back), ?always=1 (draw every frame even when nothing changed), ?dbg=1 (a corner
// readout: depth bits, GPU string, near/far, per-second counters), ?blur=1 (the panels'
// backdrop blur back), ?rehover=1 (rewrite the info box on every mouse move, as before).
export const DIAG = (() => {
  const p = new URLSearchParams(location.search), on = (k) => p.get(k) === '1';
  return { logdepth: on('logdepth'), noaa: !on('aa'), pdb: on('pdb'), dpr: p.has('dpr') ? +p.get('dpr') : 0, nodamp: on('nodamp'),
           fixclip: on('fixclip'), offset: on('offset'), always: on('always'), dbg: on('dbg'), blur: on('blur'), rehover: on('rehover'), wheel: on('wheel'),
           n: { frames: 0, renders: 0, cam: 0, clip: 0, paints: 0, overlays: 0, uploads: 0, info: 0 } };
})();
export const renderer = new THREE.WebGLRenderer({ canvas: $('c'), antialias: !DIAG.noaa, logarithmicDepthBuffer: DIAG.logdepth, preserveDrawingBuffer: DIAG.pdb });
renderer.setPixelRatio(DIAG.dpr || Math.min(devicePixelRatio, 2));
if (DIAG.blur) document.body.classList.add('blur');
export const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0f17);
export const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
camera.position.set(0, 0.6, 3.4);
export const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = !DIAG.nodamp;
controls.minDistance = 1.15; controls.maxDistance = 10;
wheelZoom(controls, renderer.domElement);
if (DIAG.wheel) {  // ?wheel=1: log each wheel event and the zoom it causes (Firefox over-zoom report)
  renderer.domElement.addEventListener('wheel', (e) => {
    const before = camera.position.length();
    requestAnimationFrame(() => console.log('[wheel]', { deltaY: e.deltaY, deltaMode: e.deltaMode, dpr: window.devicePixelRatio,
      dprInt: window.devicePixelRatio | 0, distBefore: +before.toFixed(3), distAfter: +camera.position.length().toFixed(3) }));
  }, { capture: true, passive: true });
}
const hemi = new THREE.HemisphereLight(0xffffff, 0x334455, 1.4);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
camera.add(sun); sun.position.set(-1.5, 1.5, 1);
scene.add(camera);
export const group = new THREE.Group();
scene.add(group);
export const lights = new Relief.Lights(hemi, sun);
// the 3D relief (relief.js): on or off, and its sea surface (one per view mode, kept across frames)
export const relief3d = () => $('relief3d').checked;
export const seaFloorOn = () => relief3d() && $('seaFloor').checked;

export const RIBBON_MATS = new Map();  // (the overlays' line materials, ribbonMat: their resolution follows the window)
export function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  RIBBON_MATS.forEach((m) => m.resolution.set(innerWidth, innerHeight));
}
// The camera's near and far planes hug what can be in view (PW-408). The depth buffer's
// precision goes with the near plane (a step of ~d^2 / (near * 2^bits) at distance d): with
// near fixed at 0.01, a 16-bit depth buffer (which some browsers and displays give) steps
// ~0.014 globe radii at the default distance, more than the rivers' lift over the 3D relief
// (~0.002-0.003) and about the marks' (~0.012), so rivers, and less often volcano and hotspot
// marks, z-fought the ground and shimmered (with near 256x smaller headless, as 24 -> 16 bits
// would: 20-50% of the river pixels lost and changing as the camera moves). Nothing drawn is
// closer than half the camera's height over the highest thing on the globe (radius 1.35: the
// axis, event markers, the relief at 200x) or the map (its relief plus 0.15).
export function fitClip() {
  if (DIAG.fixclip) { if (camera.near !== 0.01 || camera.far !== 100) { camera.near = 0.01; camera.far = 100; camera.updateProjectionMatrix(); } return; }
  const ext = S.topo?.maxR || 1;
  let h, far;
  if (state.mode === 'globe') { const r = camera.position.length(); h = r - Math.max(1.35, ext * 1.1); far = r + 2; }
  else { h = camera.position.z - (relief3d() ? 2 / Math.PI * Math.max(ext - 1, 0) : 0) - 0.15; far = camera.position.distanceTo(controls.target) + 6; }
  const near = Math.max(0.01, 0.5 * h);
  if (Math.abs(near - camera.near) > 1e-4 * near || Math.abs(far - camera.far) > 1e-3) {
    camera.near = near; camera.far = far; camera.updateProjectionMatrix(); DIAG.n.clip++;
  }
}
// Map is 4 x 2 units (lon/90, lat/90); back the camera off until all of it fits.
export function fitMap() {
  const halfH = Math.max(1, 2 / camera.aspect) * 1.04;
  camera.position.set(0, 0, halfH / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)));
  controls.target.set(0, 0, 0);
}

