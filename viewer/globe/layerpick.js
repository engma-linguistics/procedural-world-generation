// The grouped layer picker (PW-1026; the zoom page has the same sections in zoom.html).
// A search box, a row of the last few layers used, and one folding section per kind of layer (layers.js SECTIONS,
// from each layer's `group`). Crops, animals and body traits get one dropdown each instead of a button per item;
// a search lists the matching ones as buttons. Which sections are open, and the recent layers, are remembered
// in localStorage (guarded: it can be missing or throw).
import { esc } from '../planets.js';
import { state } from './state.js';
import { $ } from './scene.js';
import { FAMILY_NAMES, familyOf, layerDef, layerSections } from './layers.js';
import { animalStocks, cropStocks } from './colours.js';
import { refresh } from './load.js';
import { paint } from './geometry.js';

const OPEN_KEY = 'planetViewer.layerGroups', RECENT_KEY = 'planetViewer.recentLayers', RECENT_N = 4;
const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* not saved */ } };
let open = load(OPEN_KEY, {}), recent = load(RECENT_KEY, []);
if (!Array.isArray(recent)) recent = [];

// what a layer is called on its button: 'crop: foxtail millet' (the stock's own label when it has one)
export function layerLabel(l) {
  const fam = familyOf(l);
  if (!fam) return l;
  const id = l.slice(fam.length), st = fam === 'crop: ' ? cropStocks()[id] : fam === 'animal: ' ? animalStocks()[id] : null;
  return (st?.label || id).replace(/_/g, ' ');
}
const hintOf = (l) => { const d = layerDef(l); return d.hint ? d.hint + (d.units && d.hintUnits !== false ? ` Units: ${d.units}.` : '') : ''; };
const button = (l, text = l) => `<button data-v="${esc(l)}" class="${l === state.layer ? 'on' : ''}"${hintOf(l) ? ` title="${esc(hintOf(l))}"` : ''}>${esc(text)}</button>`;
const famText = (l) => { const f = familyOf(l); return f ? `${FAMILY_NAMES[f]}: ${layerLabel(l)}` : l; };

// the picker's skeleton (once): the search box stays put while the rest is redrawn
function skeleton() {
  if ($('layerPick')) return;
  const box = document.createElement('div');
  box.id = 'layerPick';
  box.innerHTML = `<input type="search" id="layerFind" placeholder="Find a layer (rain, wheat, soil…)" autocomplete="off"
      title="Type part of a layer's name or what it shows; Enter picks the first match, Esc clears">
    <div id="lpBody"></div>`;
  $('layerSeg').after(box);
  $('layerSeg').style.display = 'none';
  $('layerFind').addEventListener('input', () => render(lastLayers));
  $('layerFind').addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.target.value = ''; render(lastLayers); }
    if (e.key === 'Enter') { const b = $('lpBody').querySelector('button[data-v]'); if (b) pick(b.dataset.v); }
  });
  $('lpBody').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-v]');
    if (b) pick(b.dataset.v);
  });
  $('lpBody').addEventListener('change', (e) => { if (e.target.dataset.fam && e.target.value) pick(e.target.value); });
  $('lpBody').addEventListener('toggle', (e) => {
    const d = e.target;
    if (d.tagName !== 'DETAILS' || !d.dataset.g || $('layerFind').value.trim()) return;  // (a search opens sections without remembering it)
    open[d.dataset.g] = d.open; save(OPEN_KEY, open);
  }, true);
}

let lastLayers = [];
function pick(l) {
  if (!l) return;
  recent = [l, ...recent.filter((x) => x !== l)].slice(0, 8); save(RECENT_KEY, recent);
  state.layer = l;
  render(lastLayers);
  refresh(paint);
}

// draws the picker for these available layers (panel.js renderLayerButtons)
export function renderGroupedPicker(layers) {
  skeleton();
  render(layers);
}

function render(layers) {
  lastLayers = layers;
  const q = $('layerFind').value.trim().toLowerCase(), have = new Set(layers);
  const secs = layerSections(layers);
  let html = '';
  if (q) {  // a search: every matching layer, family items too, as buttons under their section's title
    const hit = (l) => (famText(l) + ' ' + hintOf(l)).toLowerCase().includes(q);
    let n = 0;
    for (const s of secs) {
      const ls = [...s.layers, ...Object.values(s.families).flat()].filter(hit);
      if (!ls.length) continue;
      n += ls.length;
      html += `<div class="lpHit"><div class="lpHead">${esc(s.title)}</div><div class="row seg">${ls.map((l) => button(l, famText(l))).join('')}</div></div>`;
    }
    $('lpBody').innerHTML = html || `<div class="muted">No layer matches "${esc(q)}".</div>`;
    return n;
  }
  const rec = recent.filter((l) => have.has(l)).slice(0, RECENT_N);
  if (rec.length) html += `<div class="lpRecent"><span class="muted">recent</span> <span class="seg">${rec.map((l) => button(l, famText(l))).join('')}</span></div>`;
  for (const s of secs) {
    const fams = Object.entries(s.families), mine = s.layers.includes(state.layer) || fams.some(([, ls]) => ls.includes(state.layer));
    const isOpen = s.id in open ? open[s.id] : mine;
    const count = s.layers.length + fams.reduce((a, [, ls]) => a + ls.length, 0);
    const peek = [...s.layers.slice(0, 3), ...fams.map(([f]) => FAMILY_NAMES[f] + 's')].slice(0, 4).join(', ');
    html += `<details class="lpGroup${mine ? ' mine' : ''}" data-g="${s.id}"${isOpen ? ' open' : ''}><summary><b>${esc(s.title)}</b>
      <span class="muted">${mine && !isOpen ? `<span class="lpOn">${esc(famText(state.layer))}</span> · ` : ''}${count > 4 ? `${count} layers: ` : ''}${esc(peek)}${count > 4 ? '…' : ''}</span></summary>
      ${s.layers.length ? `<div class="row seg">${s.layers.map((l) => button(l)).join('')}</div>` : ''}
      ${fams.map(([f, ls]) => `<label class="lpFam">${FAMILY_NAMES[f]} <select data-fam="${esc(f)}">
        ${ls.includes(state.layer) ? '' : `<option value="">pick one of ${ls.length}…</option>`}
        ${ls.map((l) => `<option value="${esc(l)}"${l === state.layer ? ' selected' : ''}>${esc(layerLabel(l))}</option>`).join('')}</select></label>`).join('')}
    </details>`;
  }
  $('lpBody').innerHTML = html;
  return layers.length;
}
