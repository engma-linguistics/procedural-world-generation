// The globe camera from orbit down to the ground (PW-1688, PW-1696; lod-plan-v2.md section 4), Google-Earth-like:
//   - the wheel zooms toward the point under the cursor, by a share of the height above the drawn ground (so the last
//     kilometres take as many notches as the first thousands); never below MIN_KM over the ground;
//   - a plain drag turns the globe (OrbitControls about the centre) by an amount that follows the height, so the ground
//     keeps up with the pointer near the surface;
//   - below 200 km the camera tilts toward the horizon as it comes down (75 degrees by 1.5 km: lodmath.js::autoTilt),
//     turning about the ground point at the screen's centre; a right-drag, middle-drag or Shift/Ctrl/Alt-drag tilts it
//     (drag up: toward the horizon; down: back to straight down) within a cap of 80 degrees that closes to 0 between
//     200 and 1,000 km (capTilt), so scrolling out always comes back to the straight-down orbit. The tilt moves at most
//     TILT_RATE a second unless the user drags it (no jumps).
// How: OrbitControls keeps a straight-down camera (the "nadir" pose, target the centre); each frame the tilt is put on
// it (camera turned about the ground point under the nadir camera, same distance from it) after controls.update(), and
// taken off before the next one, so OrbitControls never sees the tilted pose. Anything else that moves the camera
// between frames (a view from the address, a highlight) is taken as the new nadir pose.
import * as THREE from 'three';
import { state } from './state.js';
import { camera, controls, group, renderer, setClipGround, setWheelHook } from './scene.js';
import { LOD, groundRadius } from './lodtiles.js';
import { autoTilt, capTilt } from '../lodmath.js';

const MIN_KM = 0.3, R_KM = 6371, D2R = Math.PI / 180;
const TILT_RATE = 30 * D2R, DRAG_RAD_PER_PX = 0.3 * D2R;
// the least distance from the pivot: MIN_KM over it once tilted (the camera is h cos(tilt) above the ground there)
const minH = () => MIN_KM / R_KM / Math.max(Math.cos(CAM.tilt), 0.25);
// the camera's tilt state (planetViewer.cam: tools/viewer_lod_dive.py): tilt now (rad), the user's share on top of the
// automatic one, the nadir camera's height over the ground (km)
export const CAM = { tilt: 0, user: 0, nadirKm: Infinity };
const active = () => state.mode === 'globe' && state.tab !== 'zoom' && LOD.on;

const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), sphere = new THREE.Sphere(new THREE.Vector3(), 1), hit = new THREE.Vector3();
const q = new THREE.Quaternion(), loc = new THREE.Vector3(), m4 = new THREE.Matrix4(), Y = new THREE.Vector3(0, 1, 0), O = new THREE.Vector3();
const nadir = { pos: new THREE.Vector3(), quat: new THREE.Quaternion(), ok: false };
const applied = { pos: new THREE.Vector3(), quat: new THREE.Quaternion() };
const d = new THREE.Vector3(), G = new THREE.Vector3(), up = new THREE.Vector3(), p = new THREE.Vector3();

// the drawn ground's radius under a world-space point (the group only spins about y: radii are the same in both)
function groundW(v) { loc.copy(v); group.worldToLocal(loc); return groundRadius(loc); }
function cursorHit(g, out) {
  ray.setFromCamera(ndc, camera);
  sphere.center.setFromMatrixPosition(group.matrixWorld); sphere.radius = g;
  return ray.ray.intersectSphere(sphere, out);
}
// the nadir camera at its position: looking at the centre, north up (as OrbitControls.update leaves it)
function nadirLook() { nadir.quat.setFromRotationMatrix(m4.lookAt(nadir.pos, O, Y)); }
function toNadir() { camera.position.copy(nadir.pos); camera.quaternion.copy(nadir.quat); camera.updateMatrixWorld(); }
function saveNadir() { nadir.pos.copy(camera.position); nadir.quat.copy(camera.quaternion); nadir.ok = true; }
// put the tilt on the nadir pose: the camera turned by CAM.tilt about G, the ground under the nadir camera, toward the
// nadir camera's screen-down, at the same distance from G
function applyTilt() {
  const t = CAM.tilt;
  if (!(t > 1e-6)) toNadir();
  else {
    const r = nadir.pos.length();
    d.copy(nadir.pos).divideScalar(r);
    const g = groundW(d), h = r - g;
    G.copy(d).multiplyScalar(g);
    up.copy(Y).applyQuaternion(nadir.quat);
    p.copy(d).multiplyScalar(Math.cos(t)).addScaledVector(up, -Math.sin(t)).multiplyScalar(h).add(G);
    const gc = groundW(p), lo = gc + MIN_KM / R_KM;  // (never into a hill beside the pivot)
    if (p.length() < lo) p.setLength(lo);
    camera.position.copy(p);
    camera.quaternion.setFromRotationMatrix(m4.lookAt(p, G, up));
    camera.updateMatrixWorld();
  }
  applied.pos.copy(camera.position); applied.quat.copy(camera.quaternion);
}
// set the tilt (the user's drag): within the cap at this height; the user's share is what is above the automatic tilt
function setTilt(t) {
  const h = CAM.nadirKm, cap = capTilt(h);
  CAM.tilt = Math.min(cap, Math.max(0, t));
  CAM.user = CAM.tilt - autoTilt(h);
  applyTilt();
  LOD.dirty = true;
}

function wheel(e, dy) {
  if (!active()) return false;
  const rect = renderer.domElement.getBoundingClientRect();
  ndc.set((e.clientX - rect.left) / rect.width * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1);
  if (!nadir.ok) saveNadir();
  camera.updateMatrixWorld();
  // the point under the cursor, on a sphere through the ground at the screen's centre (the pivot)
  d.copy(nadir.pos).normalize();
  const gp = groundW(d), p0 = cursorHit(gp, new THREE.Vector3());
  const r = nadir.pos.length(), h = Math.max(r - gp, minH());
  const hNew = Math.min(controls.maxDistance - gp, Math.max(minH(), h * Math.exp(dy * 0.0011)));
  nadir.pos.multiplyScalar((gp + hNew) / r); nadirLook();
  applyTilt();
  // keep the point under the cursor under it: turn the camera about the centre until the cursor's ray meets it again
  if (p0) for (let k = 0; k < 3; k++) {
    if (!cursorHit(gp, hit)) break;
    q.setFromUnitVectors(hit.clone().normalize(), p0.clone().normalize());
    nadir.pos.applyQuaternion(q); nadirLook(); applyTilt();
  }
  controls.minDistance = Math.min(controls.minDistance, nadir.pos.length());
  toNadir(); controls.update(); saveNadir(); applyTilt();
  return true;
}
setWheelHook(wheel);
setClipGround(() => (LOD.on ? groundW(camera.position) : 1));

// the tilt drag: right button, middle button, or the left with Shift, Ctrl or Alt (OrbitControls never sees it)
const canvas = renderer.domElement;
let drag = null;
canvas.addEventListener('pointerdown', (e) => {
  if (!active() || !(e.button === 2 || e.button === 1 || (e.button === 0 && (e.shiftKey || e.ctrlKey || e.altKey)))) return;
  e.preventDefault(); e.stopImmediatePropagation();
  canvas.setPointerCapture(e.pointerId);
  drag = { id: e.pointerId, y: e.clientY, moved: 0, button: e.button };
}, { capture: true });
canvas.addEventListener('pointermove', (e) => {
  if (!drag || e.pointerId !== drag.id) return;
  e.stopImmediatePropagation();
  const dyPx = drag.y - e.clientY; drag.y = e.clientY; drag.moved += Math.abs(dyPx);
  if (dyPx) setTilt(CAM.tilt + dyPx * DRAG_RAD_PER_PX);
}, { capture: true });
const endDrag = (e) => {
  if (!drag || e.pointerId !== drag.id) return;
  e.stopImmediatePropagation();
  if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId);
  // (a modifier-drag ends in a click: not a pick)
  if (drag.button === 0 && drag.moved > 3) addEventListener('click', (c) => { c.stopImmediatePropagation(); c.preventDefault(); }, { capture: true, once: true });
  drag = null;
};
canvas.addEventListener('pointerup', endDrag, { capture: true });
canvas.addEventListener('pointercancel', endDrag, { capture: true });
canvas.addEventListener('contextmenu', (e) => { if (active()) e.preventDefault(); });

// each frame, before controls.update(): the tilt off (back to the nadir pose, unless something else moved the camera);
// the least distance follows the ground; the drag speed follows the height
export function updateDive() {
  const same = nadir.ok && camera.position.equals(applied.pos) && camera.quaternion.equals(applied.quat);
  if (same) toNadir();
  else if (nadir.ok) { nadir.ok = false; CAM.tilt = Math.min(CAM.tilt, capTilt(heightKm(camera.position))); }  // (moved by someone else)
  if (state.mode !== 'globe') { controls.minDistance = 1.15; controls.rotateSpeed = 1; return; }
  if (!LOD.on) return;
  d.copy(camera.position).normalize();
  const g = groundW(d), r = camera.position.length(), h = r - g;
  controls.minDistance = g + Math.min(minH(), Math.max(h, MIN_KM / R_KM));  // (afterControls raises a tilted camera gently)
  controls.rotateSpeed = Math.min(1, Math.max(1e-5, 0.4 * h));
}
const heightKm = (v) => { d.copy(v).normalize(); return Math.max(1e-3, (v.length() - groundW(d)) * R_KM); };
// each frame, after controls.update(): the nadir pose kept, the tilt eased toward the automatic one plus the user's
// share (within the cap) and put on
let lastNow = 0;
export function afterControls(now) {
  const dt = lastNow ? Math.min(0.1, (now - lastNow) / 1000) : 0; lastNow = now;
  saveNadir();
  if (!active()) { CAM.tilt = 0; CAM.user = 0; CAM.nadirKm = Infinity; applied.pos.copy(camera.position); applied.quat.copy(camera.quaternion); return; }
  let h = CAM.nadirKm = heightKm(nadir.pos);
  if (h < minH() * R_KM) {  // (tilted further at the least height: up to MIN_KM over the pivot, 5% a frame)
    const g = nadir.pos.length() - h / R_KM;
    nadir.pos.setLength(g + Math.min(minH(), h * 1.05 / R_KM)); nadirLook();
    h = CAM.nadirKm = heightKm(nadir.pos);
  }
  const cap = capTilt(h);
  if (cap <= 0) CAM.user = 0;
  if (!drag) {
    const target = Math.min(cap, Math.max(0, autoTilt(h) + CAM.user));
    CAM.tilt += Math.max(-TILT_RATE * dt, Math.min(TILT_RATE * dt, target - CAM.tilt));
  }
  applyTilt();
}
