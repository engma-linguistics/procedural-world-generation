import * as THREE from 'three';
import { S, state } from './state.js';
import { $, camera, controls, fitMap, group } from './scene.js';
import { disposeObj, lineObj, llPos } from './geometry.js';
// ------------------------------------------------------------ spin axis and tilt
// The globe is drawn with north up (+Y), so the spin axis is the Y axis. The
// tilt (angle between the spin axis and the orbit's axis) comes from the
// run/world params; it sets the tropics (sun overhead at midsummer) and the
// polar circles (midnight sun).
function planetTilt() {
  const p = S.V.kind === 'run' ? S.V.run.meta.params : S.V.meta && S.V.meta.params;
  return p && p.tilt != null ? +p.tilt : 23.4;
}

export function textSprite(text, color) {
  const cv = document.createElement('canvas'); cv.width = cv.height = 64;
  const g = cv.getContext('2d');
  g.font = 'bold 44px -apple-system, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 6; g.strokeStyle = '#0b0f17'; g.strokeText(text, 32, 34);
  g.fillStyle = color; g.fillText(text, 32, 34);
  // (PW-839: drawn after the 3D relief's translucent sea (renderOrder 1), which would otherwise blend over it; the transparent
  // corners of the square canvas neither write depth nor hide what is behind: alphaTest, depthWrite false)
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthWrite: false, alphaTest: 0.05 }));
  sp.renderOrder = 5;
  sp.scale.set(0.11, 0.11, 1);
  return sp;
}

// Continent names (PW-867): a label at each continent's centre. A world's own summary (landmasses[].name, centre; the owner's names from
// worlds/names/<id>.json replace the generated ones, `planet name`), or a peoples run's present landmasses (the names its history used).
export const lmGroup = new THREE.Group();
group.add(lmGroup);
export const rankLetter = (r) => { let s = '', i = r + 1; while (i) { const k = (i - 1) % 26; s = String.fromCharCode(65 + k) + s; i = Math.floor((i - 1) / 26); } return s; };
function wordSprite(text, color) {
  const cv = document.createElement('canvas'); cv.width = 512; cv.height = 96;
  const g = cv.getContext('2d');
  g.font = 'bold 56px -apple-system, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 9; g.lineJoin = 'round'; g.strokeStyle = 'rgba(8,12,20,0.85)'; g.strokeText(text, 256, 50);
  g.fillStyle = color; g.fillText(text, 256, 50);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthWrite: false, alphaTest: 0.05, transparent: true, opacity: 0.92 }));
  sp.renderOrder = 6;
  return sp;
}
function landmassLabels() {  // [{name, lat, lon, area}] of the continents (a share of the surface of at least ~1%)
  if (!S.V) return [];
  if (S.V.kind === 'world' && S.V.summary?.landmasses?.length)
    return S.V.summary.landmasses.filter((m) => m.pct_of_surface >= 1).map((m) => ({ name: m.name, lat: m.center_lat, lon: m.center_lon, area: m.pct_of_surface }));
  const pl = S.V.run?.meta?.present?.landmasses;
  if (pl) return pl.filter((m) => m.kind === 'continent' && m.called).map((m) => ({ name: m.called, lat: m.lat, lon: m.lon, area: m.area_mkm2 / 5.1 }));
  return [];
}
export function buildLandmassNames() {
  lmGroup.children.forEach(disposeObj);
  lmGroup.clear();
  if (!$('lmNames').checked) return;
  const globe = state.mode === 'globe';
  for (const m of landmassLabels()) {
    if (!m.name || m.lat == null) continue;
    const sp = wordSprite(m.name, '#f4f1e6');
    const w = (globe ? 0.6 : 1.1) * Math.min(0.75, 0.4 + 0.05 * Math.sqrt(m.area));  // (a little bigger for the bigger land; the canvas is 512 x 96)
    sp.scale.set(w, w * 96 / 512, 1);
    sp.position.set(...(globe ? llPos(m.lat, m.lon, 1.025) : llPos(m.lat, m.lon, 1, 0.012)));
    sp.userData.px = Math.min(44, 24 + 4 * Math.sqrt(m.area));  // (the projected map draws it this high, css px)
    lmGroup.add(sp);
  }
}

export const axisGroup = new THREE.Group();
group.add(axisGroup);
export function buildAxis() {
  axisGroup.children.forEach(disposeObj);
  axisGroup.clear();
  const tilt = planetTilt(), globe = state.mode === 'globe';
  if ($('axis').checked && globe) {
    const end = 1.15;  // stays in view at the default camera distance
    axisGroup.add(lineObj([0, -end, 0, 0, end, 0], 0xffffff, 0.8));
    for (const [y, label, color] of [[1, 'N', '#ff8a6b'], [-1, 'S', '#9fd8ff']]) {
      const cone = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.06, 12), new THREE.MeshBasicMaterial({ color }));
      cone.position.set(0, y * end, 0);
      if (y < 0) cone.rotation.x = Math.PI;
      const sp = textSprite(label, color);
      sp.center.set(-0.15, 0.5);  // label just right of the tip, whichever way the globe is turned
      sp.position.set(0, y * end, 0);
      axisGroup.add(cone, sp);
    }
  }
  if ($('tropics').checked) {
    // [latitude, colour, opacity]: equator, tropics at +-tilt, polar circles at +-(90 - tilt)
    const circles = [[0, 0xffffff, 0.5], [tilt, 0xffc864, 0.75], [-tilt, 0xffc864, 0.75],
                     [90 - tilt, 0x9fd8ff, 0.7], [tilt - 90, 0x9fd8ff, 0.7]];
    for (const [la, color, op] of circles) {
      const pts = [];
      if (globe) {
        for (let k = 0; k < 128; k++) pts.push(...llPos(la, k / 128 * 360, 1.006), ...llPos(la, (k + 1) / 128 * 360, 1.006));
      } else pts.push(-2, la / 90, 0.004, 2, la / 90, 0.004);
      axisGroup.add(lineObj(pts, color, op));
    }
  }
  renderTiltInset(tilt);
}

// small side view: the orbit plane (dashed), the planet, and its axis leaning by the tilt
function renderTiltInset(tilt) {
  const el = $('tiltInset');
  el.style.display = $('axis').checked ? '' : 'none';
  const a = tilt * Math.PI / 180, cx = 72, cy = 36, L = 30, r = 13;
  const ax = L * Math.sin(a), ay = L * Math.cos(a), ex = r * Math.cos(a), ey = r * Math.sin(a);
  const arcR = 22, arcEnd = [cx + arcR * Math.sin(a), cy - arcR * Math.cos(a)];
  el.innerHTML = `<svg width="116" height="72" viewBox="0 0 116 72">
    <line x1="2" y1="${cy}" x2="114" y2="${cy}" stroke="#8b97a8" stroke-dasharray="3 3"/>
    <text x="2" y="${cy - 4}" fill="#8b97a8" font-size="8">orbit plane</text>
    <line x1="${cx}" y1="3" x2="${cx}" y2="69" stroke="#8b97a8" stroke-width=".6" stroke-dasharray="1 2"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="#2d68a3" stroke="#6aa7d8"/>
    <line x1="${cx - ex}" y1="${cy - ey}" x2="${cx + ex}" y2="${cy + ey}" stroke="#ffffff" stroke-opacity=".5"/>
    <path d="M ${cx} ${cy - arcR} A ${arcR} ${arcR} 0 0 1 ${arcEnd[0]} ${arcEnd[1]}" fill="none" stroke="#ffc864"/>
    <line x1="${cx - ax}" y1="${cy + ay}" x2="${cx + ax}" y2="${cy - ay}" stroke="#ffffff" stroke-width="1.5"/>
    <text x="${cx + ax + 1}" y="${cy - ay + 1}" fill="#ff8a6b" font-size="9" font-weight="bold">N</text>
  </svg>tilt ${+tilt.toFixed(1)}°`;
}

export function northUp() {
  if (state.mode !== 'globe') { fitMap(); return; }
  // keep the camera's longitude and distance, put it level with the equator
  const p = camera.position, d = p.distanceTo(controls.target);
  const az = Math.atan2(p.x - controls.target.x, p.z - controls.target.z);
  controls.target.set(0, 0, 0);
  camera.position.set(d * Math.sin(az), 0, d * Math.cos(az));
  camera.lookAt(0, 0, 0);
}
$('northUp').addEventListener('click', northUp);
