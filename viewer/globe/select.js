import * as THREE from 'three';
import { S, state } from './state.js';
import { $, DIAG, camera, controls, fitMap, group } from './scene.js';
import { setSeason } from './colours.js';
import { unitVec } from './geometry.js';
import { favKeyOf, worldTitle } from './provenance.js';
import { canRotate, goToLatLon } from './pick.js';
import { OVERLAY_IDS, applyProjUrl, setLights } from './map2d.js';
import { HL_CATS, turnTo } from './highlights.js';
import { LoadError, beginLoad, loadFailed, loadRun, setWorld } from './load.js';
// ------------------------------------------------------------ index / URL
export async function loadSelection(value) {
  const [kind, id] = value.split(':');
  const u = new URL(location);
  ['world', 'run', 't'].forEach((k) => u.searchParams.delete(k));
  u.searchParams.set(kind, id); history.replaceState(null, '', u);
  if (kind === 'run') await loadRun(id);
  else {
    const tok = beginLoad();
    DIAG.mark('world: fetch');
    const r = await fetch('../worlds/' + id, { cache: 'no-cache' });
    const what = `world "${id.replace(/\.json$/, '')}"`;
    if (r.status === 404) throw new LoadError(`There is no ${what}. It may have been deleted, or the link has a typo.`);
    if (!r.ok) throw new LoadError(`The server could not send ${what} (HTTP ${r.status}).`);
    const w = await r.json().catch(() => { throw new LoadError(`The file of ${what} could not be read.`); });
    DIAG.mark('world: parsed');
    await setWorld(w, tok);
  }
}
$('worldSel').addEventListener('change', (e) => loadSelection(e.target.value).catch(loadFailed));
addPickerFilter($('worldSel'), { placeholder: 'filter: run / world id or name' });  // (pickfilter.js, PW-407)

// drag & drop (works even when opened as a plain file://)
addEventListener('dragover', (e) => { e.preventDefault(); $('drop').style.display = 'flex'; });
addEventListener('dragleave', (e) => { if (e.target === $('drop')) $('drop').style.display = 'none'; });
addEventListener('drop', async (e) => {
  e.preventDefault(); $('drop').style.display = 'none';
  const f = e.dataTransfer.files[0]; if (f) await setWorld(JSON.parse(await f.text()));
});

// URL options, e.g. ?run=19385e&t=120&layer=rainfall&arrows=1  or  ?world=ae28af.json&mode=map&pentas=1
// (&lat=..&lon=..: turn to that place and pick its cell; clicking a cell copies such a link)
// (&hl=N: open highlight number N once its list is found or cached)
// (&settle=mines&lat=..&lon=..&dist=1.3: the mining districts around a place, e.g. a dwarf mining colony)
// (6-hex ids; world= is the file name with .json; layer= is a viewer layer name, spaces URL-encoded: crust%20age)
export function applyUrlOptions() {
  const p = urlp;
  if (p.get('mode')) { state.mode = p.get('mode'); [...$('modeSeg').children].forEach((b) => b.classList.toggle('on', b.dataset.v === state.mode)); controls.enableRotate = state.mode === 'globe'; if (state.mode === 'map') fitMap(); }
  // (&tilt=deg: the flat map seen from the south at that angle, for screenshots of the 3D relief)
  if (p.get('layer')) state.layer = p.get('layer');
  if (p.get('anthro') === '0') state.anthro = false;  // (peoples runs: no tint of cleared land)
  if (p.get('peopleswhole') === '1') state.peoplesWhole = true;  // (peoples runs: a people with groups as a whole)
  if (p.get('obs')) { state.obs = p.get('obs'); [...$('obsSeg').children].forEach((b) => b.classList.toggle('on', b.dataset.v === state.obs)); }
  // (&settle=mines: the settlements overlay showing only its mining districts ('only the mines'), for links to the mines; &settle=all: everything)
  if (p.get('settle')) { $('settlements').checked = true; $('settleMines').checked = true; $('settleMinesOnly').checked = p.get('settle') === 'mines'; }
  for (const id of [...OVERLAY_IDS, 'smooth', 'spin']) if (p.has(id)) $(id).checked = p.get(id) === '1';
  if (p.get('relief')) $('relief').value = p.get('relief');
  if (p.get('relief3d') === '1') {
    $('relief3d').checked = true;
    if (p.get('ex')) $('reliefEx').value = p.get('ex');
    const sn = (p.get('sun') || '').split(',').map(Number);
    if (sn.length === 2 && sn.every(Number.isFinite)) { $('sunAz').value = sn[0]; $('sunEl').value = sn[1]; }
    if (p.get('sea') === '0') $('seaFloor').checked = false;
    setLights(); canRotate();
  }
  if (p.get('season')) setSeason(p.get('season'));
  if (p.get('pft')) state.pft = p.get('pft');
  if (p.get('tech')) state.tech = p.get('tech');  // (the 'technology' layer's tech and colour mode, PW-913)
  if (p.get('techcol')) state.techCol = p.get('techcol');
  if (p.get('embed')) document.body.classList.add('embed');  // (?embed=tech: inside the workbench's Technology tab)
  if (p.get('res')) state.res = p.get('res');
  if (HL_CATS[p.get('hlcat')]) state.hlCat = p.get('hlcat');  // a highlights category: landscape, water, climate, travel, geology, vegetation  // jul | jan: the winds' half-year and the temperature / rain season
  return p;
}
export const urlp = new URLSearchParams(location.search);  // (the address's options: applyUrlOptions, at boot)

async function getJSON(url) { try { const r = await fetch(url, { cache: 'no-store' }); return r.ok ? r.json() : []; } catch { return []; } }
// fills the run/world dropdown from the indexes; returns false when there's nothing
export async function fillSelector() {
  const [runs, worlds, zooms] = await Promise.all([getJSON('../runs/index.json'), getJSON('../worlds/index.json'),
                                                  getJSON('../zooms/index.json')]);
  S.IDX = { runs, worlds, zooms };
  try { S.FAVS = new Set(((await (await fetch('../api/favourites', { cache: 'no-store' })).json()).favourites || []).map((e) => `${e.kind}:${e.id}`)); } catch { S.FAVS = new Set(); }
  if (!runs.length && !worlds.length) return false;
  const was = $('worldSel').value || (urlp.get('run') ? 'run:' + urlp.get('run') : urlp.get('world') ? 'world:' + urlp.get('world') : '');
  const isFav = (v) => S.FAVS.has(favKeyOf(v));
  const mode = S.FAVS.size ? $('favMode').value : 'all';  // (with no favourite yet, every mode lists everything)
  const opt = (v, label) => `<option value="${v}">${isFav(v) ? '\u2605 ' : ''}${label}</option>`;
  const when = (c) => (c || '').slice(5, 16);  // "MM-DD HH:MM"
  const all = [
    ...runs.filter((r) => r.kind !== 'timezoom').map((r) => ['main', 'run:' + r.dir, `${r.id} · ${r.name} · ${r.myr} Myr · ${when(r.created)}`]),
    ...runs.filter((r) => r.kind === 'timezoom').map((r) => ['tz', 'run:' + r.dir, `${r.id} · ${r.name} · ${r.kyr} kyr · ${when(r.created)}`]),
    ...worlds.map((w) => ['world', 'world:' + w.file, `${w.id} · ${worldTitle(w)}${w.name !== worldTitle(w) ? ' — ' + w.name : ''} · ${when(w.created)}`])];
  const LABEL = { main: 'Tectonic timelines (newest first)', tz: 'Glacial time zooms (newest first)', world: 'Worlds (newest first)' };
  const group = (label, items) => (items.length ? `<optgroup label="${label}">${items.map(([, v, l]) => opt(v, l)).join('')}</optgroup>` : '');
  const groups = (items) => ['main', 'tz', 'world'].map((g) => group(LABEL[g], items.filter((x) => x[0] === g))).join('');
  const favItems = all.filter((x) => isFav(x[1]));
  // favourites first: a group of them on top (the rest below, each once); only: just those, plus the item on show so it stays selectable
  $('worldSel').innerHTML = mode === 'first' ? group('\u2605 Favourites', favItems) + groups(all.filter((x) => !isFav(x[1])))
    : mode === 'only' ? group('\u2605 Favourites', favItems) + group('Not a favourite (on show)', all.filter((x) => !isFav(x[1]) && x[1] === was))
    : groups(all);
  if (was && [...$('worldSel').options].some((o) => o.value === was)) $('worldSel').value = was;
  syncFav();
  return true;
}
// the star button shows whether the run or world on show is a favourite; a click stars or unstars it (POST /api/favourites)
export function syncFav() {
  const v = $('worldSel').value, b = $('favBtn'), on = !!v && S.FAVS.has(favKeyOf(v));
  b.disabled = !v; b.textContent = on ? '\u2605' : '\u2606'; b.style.color = on ? 'var(--star)' : ''; b.setAttribute('aria-pressed', String(on));
}
$('favBtn').addEventListener('click', async () => {
  const v = $('worldSel').value; if (!v) return;
  const [kind, ...id] = favKeyOf(v).split(':');
  const r = await fetch('../api/favourites', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ kind, id: id.join(':'), starred: !S.FAVS.has(favKeyOf(v)) }) }).catch(() => null);
  if (!r || !r.ok) { alert('Could not save the favourite. Is the viewer running via planet serve?'); return; }
  await fillSelector();
});
$('worldSel').addEventListener('change', syncFav);
$('favMode').addEventListener('change', async () => {
  try { localStorage.setItem('planet.favMode', $('favMode').value); } catch { /* private window */ }
  await fillSelector();
});
// open a run (e.g. a time zoom just made, or a time zoom's source) at time t
export async function openRun(id, t) {
  await fillSelector();
  $('worldSel').value = 'run:' + id; syncFav();
  const u = new URL(location);
  ['world', 'run', 't'].forEach((k) => u.searchParams.delete(k));
  u.searchParams.set('run', id); history.replaceState(null, '', u);
  await loadRun(id, t);
}

export async function init() {
  if (!await fillSelector()) {
    S.infoHtml = null; $('infoText').innerHTML = `No planets yet. <a href="./#new">Make one on the start page</a>, or drop a world .json here.`;
    return;
  }
  let want = urlp.get('run') ? 'run:' + urlp.get('run') : urlp.get('world') ? 'world:' + urlp.get('world') : $('worldSel').value;
  $('worldSel').value = want; syncFav();
  if (want.startsWith('run:')) await loadRun(want.slice(4), urlp.has('t') ? +urlp.get('t') : null);
  else await loadSelection(want);
  if (urlp.has('lat') && urlp.has('lon')) { goToLatLon(+urlp.get('lat'), +urlp.get('lon')); urlp.delete('lat'); urlp.delete('lon'); }
  // ?view=lat,lon: turn the globe there without picking a cell (screenshots)
  if (urlp.has('view')) {  // (at once, no animation)
    const [la, lo] = urlp.get('view').split(',').map(Number);
    $('spin').checked = false;
    if (state.mode !== 'globe') turnTo(la, lo);
    else {
      const d = camera.position.distanceTo(controls.target);
      controls.target.set(0, 0, 0);
      camera.position.copy(new THREE.Vector3(...unitVec(Math.max(-80, Math.min(80, la)), lo)).applyQuaternion(group.quaternion).normalize().multiplyScalar(d));
      camera.lookAt(0, 0, 0);
    }
  }
  // ?dist=: the camera's distance from the centre; ?tilt=deg: the flat map seen from the south at that angle (screenshots)
  const d = +urlp.get('dist') || camera.position.distanceTo(controls.target), tl = +urlp.get('tilt') || 0;
  if (urlp.has('dist') || tl) {
    if (state.mode === 'map') {
      const a = THREE.MathUtils.degToRad(tl), tg = controls.target;
      camera.position.set(tg.x, tg.y - d * Math.sin(a), d * Math.cos(a));
    } else camera.position.setLength(d);
    camera.lookAt(controls.target);
  }
  applyProjUrl();
}
$('delBtn').addEventListener('click', async () => {
  const v = $('worldSel').value; if (!v) return;
  const [kind, id] = v.split(':');
  const label = $('worldSel').selectedOptions[0].textContent;
  if (!confirm(`Delete ${label}?\nThis removes it from disk.`)) return;
  const r = await fetch(`../${kind === 'run' ? 'runs' : 'worlds'}/${id.replace(/\.json$/, '')}`, { method: 'DELETE' });
  if (!r.ok) { alert(`Delete failed (HTTP ${r.status}). Is the viewer running via 'python -m planet serve'?`); return; }
  const u = new URL(location); ['world', 'run', 't'].forEach((k) => u.searchParams.delete(k)); history.replaceState(null, '', u);
  urlp.delete('run'); urlp.delete('world'); urlp.delete('t');
  await init();
});
export function navBarHide() { $('navBar')?.setAttribute('hidden', ''); }
