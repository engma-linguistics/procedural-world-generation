// The globe camera from orbit down to the ground (PW-1688, lod-plan-v2.md section 4): the wheel zooms toward the point
// under the cursor, by a share of the height above the drawn ground (so the last kilometres take as many notches as
// the first thousands); the camera never goes below MIN_KM over the ground under it; dragging turns the globe by an
// amount that follows the height, so the ground keeps up with the pointer near the surface. The orbit still turns
// about the planet's centre (OrbitControls, target at the origin): no camera jumps, scrolling out returns to the globe.
// Not yet: the tilt toward the horizon below ~200 km (the plan's step 4 camera, left for step 5).
import * as THREE from 'three';
import { state } from './state.js';
import { camera, controls, group, renderer, setClipGround, setWheelHook } from './scene.js';
import { LOD, groundRadius } from './lodtiles.js';

const MIN_KM = 0.3, R_KM = 6371;
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), sphere = new THREE.Sphere(new THREE.Vector3(), 1), hit = new THREE.Vector3();
const q = new THREE.Quaternion(), loc = new THREE.Vector3();

function cursorHit(g, out) {
  ray.setFromCamera(ndc, camera);
  sphere.center.setFromMatrixPosition(group.matrixWorld); sphere.radius = g;
  return ray.ray.intersectSphere(sphere, out);
}
// the camera's ground radius (group space -> the same in world space: the group only spins about y)
function ground() { loc.copy(camera.position); group.worldToLocal(loc); return groundRadius(loc); }

function wheel(e, dy) {
  if (state.mode !== 'globe' || !LOD.on) return false;
  const rect = renderer.domElement.getBoundingClientRect();
  ndc.set((e.clientX - rect.left) / rect.width * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1);
  const g = ground(), r = camera.position.length(), h = Math.max(r - g, MIN_KM / R_KM);
  const hNew = Math.min(controls.maxDistance - g, Math.max(MIN_KM / R_KM, h * Math.exp(dy * 0.0011)));
  camera.updateMatrixWorld();
  const p0 = cursorHit(g, new THREE.Vector3());
  camera.position.multiplyScalar((g + hNew) / r);
  camera.lookAt(controls.target); camera.updateMatrixWorld();
  // keep the point under the cursor under it: turn the camera about the centre until the cursor's ray meets it again
  if (p0) for (let k = 0; k < 3; k++) {
    if (!cursorHit(g, hit)) break;
    q.setFromUnitVectors(hit.clone().normalize(), p0.clone().normalize());
    camera.position.applyQuaternion(q); camera.lookAt(controls.target); camera.updateMatrixWorld();
  }
  controls.minDistance = Math.min(controls.minDistance, camera.position.length());
  controls.update();
  return true;
}
setWheelHook(wheel);
setClipGround(() => (LOD.on ? ground() : 1));

// each frame, before controls.update(): the least distance follows the ground; the drag speed follows the height
export function updateDive() {
  if (state.mode !== 'globe') { controls.minDistance = 1.15; controls.rotateSpeed = 1; return; }
  if (!LOD.on) return;
  const g = ground(), r = camera.position.length(), h = r - g;
  controls.minDistance = g + MIN_KM / R_KM;
  controls.rotateSpeed = Math.min(1, Math.max(1e-5, 0.4 * h));
}
