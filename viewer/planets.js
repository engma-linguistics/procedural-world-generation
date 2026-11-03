// Shared by the start screen (start.js) and the world navigator (navigator.js): the planets
// (GET /api/planets: planet/family.py), their provenance tree as HTML, and server jobs.
// Styles use the viewer's own variables (--panel, --border, --accent, --muted).

// the viewer's number formats (numfmt.js: a plain script, shared with the classic pages)
import './numfmt.js';
export const { num, count, kyr, ago } = globalThis.NumFmt;

export const esc = (t) => String(t ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const CSS = `
.pl-thumb { display: block; width: 100%; aspect-ratio: 2 / 1; object-fit: cover; background: var(--ctl); border-radius: 4px; }
.pl-tree { margin: 0; padding: 0; list-style: none; }
.pl-tree ul { margin: 0 0 0 14px; padding: 0 0 0 8px; list-style: none; border-left: 1px solid var(--border); }
.pl-node { display: flex; gap: 8px; align-items: flex-start; padding: 4px; border-radius: 6px; margin: 2px 0; }
.pl-node:hover { background: #1d2738; }
.pl-node.cur { background: #223652; outline: 1px solid var(--accent); }
.pl-node img { width: 64px; height: 32px; flex: none; object-fit: cover; border-radius: 3px; background: var(--ctl); cursor: pointer; }
.pl-node .tx { min-width: 0; flex: 1; }
.pl-node .tt { font-weight: 600; cursor: pointer; overflow-wrap: anywhere; }
.pl-node .tt:hover { color: var(--accent); }
.pl-node .sub { color: var(--muted); font-size: 11px; }
.pl-node .acts { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 3px; align-items: center; }
.pl-kind { display: inline-block; font-size: 10px; text-transform: uppercase; letter-spacing: .06em; padding: 0 5px; border-radius: 8px;
  border: 1px solid var(--border); color: var(--muted); margin-right: 5px; vertical-align: 1px; }
.pl-kind.run { color: #ffd27c; } .pl-kind.timezoom { color: #9fd3ff; } .pl-kind.peoples { color: #ffb4a0; } .pl-kind.world { color: #b6f0a0; } .pl-kind.zoom, .pl-kind.fine { color: #e0b0ff; }
.pl-bar { height: 6px; background: var(--ctl); border: 1px solid var(--border); border-radius: 3px; margin: 4px 0; }
.pl-bar > div { height: 100%; background: var(--accent); border-radius: 2px; transition: width .4s; }
.pl-err { color: #ff8a80; }
.pl-btn { background: var(--ctl); color: var(--text); border: 1px solid var(--border); padding: 4px 10px; border-radius: 4px; cursor: pointer; font: inherit; font-size: 12px; }
.pl-btn:hover:not(:disabled) { border-color: var(--accent); }
.pl-btn:disabled { opacity: .5; cursor: default; }
.pl-btn.primary { background: var(--accent); color: var(--on-accent); border-color: var(--accent); font-weight: 600; }
.pl-btn.danger:hover:not(:disabled) { border-color: #ff8a80; color: #ff8a80; }
.pl-btn.sm { padding: 1px 7px; font-size: 11px; }
.pl-btn.star.on { color: var(--star); border-color: var(--star); }
`;
let cssDone = false;
export function injectCss() {
  if (cssDone) return;
  cssDone = true;
  const s = document.createElement('style');
  s.textContent = CSS;
  document.head.append(s);
}

export async function getPlanets() {
  try { return (await (await fetch('../api/planets', { cache: 'no-store' })).json()).planets || []; } catch { return []; }
}

const KIND_NAME = { run: 'run', timezoom: 'time zoom', peoples: 'peoples run', world: 'world', zoom: 'zoom', fine: 'fine zoom' };
export const kindName = (n) => (n.kind === 'world' && n.timezoom_kyr != null ? 'finished world' : KIND_NAME[n.kind]);

// the place of a node in its planet's story, in a few words
export function nodeWhen(n) {
  if (n.kind === 'run') return `${n.myr} Myr · seed ${n.seed} · level ${n.level}`;
  if (n.kind === 'peoples') return `peoples${n.world ? ` on world ${n.world}` : ''}`;
  if (n.kind === 'timezoom') return `${n.kyr} kyr of ice ages after ${n.at_myr} Myr`;
  if (n.kind === 'world') return n.timezoom_kyr != null ? `+${n.timezoom_kyr} kyr, sea ${n.sea_level_change_m > 0 ? '+' : ''}${Math.round(n.sea_level_change_m)} m`
    : n.t_myr != null ? `at ${n.t_myr} Myr` : 'generated directly';
  const c = n.center || {};
  return `${n.size_km} km at ${(+c.lat).toFixed(1)}, ${(+c.lon).toFixed(1)}`;
}
export const nodeTitle = (n) => `${kindName(n)[0].toUpperCase()}${kindName(n).slice(1)} ${n.id}`;

export function treeOf(planet) {
  const keys = new Set(planet.nodes.map((n) => n.key)), kids = new Map();
  for (const n of planet.nodes) {
    const p = n.parent && keys.has(n.parent) ? n.parent : '';
    kids.set(p, [...(kids.get(p) || []), n]);
  }
  const order = { run: 0, timezoom: 1, world: 2, zoom: 3, fine: 4 };
  for (const a of kids.values()) a.sort((x, y) => order[x.kind] - order[y.kind] || (x.at_myr ?? x.t_myr ?? 0) - (y.at_myr ?? y.t_myr ?? 0)
    || (x.timezoom_kyr ?? 0) - (y.timezoom_kyr ?? 0) || x.created.localeCompare(y.created));
  return kids;
}

// the planet's nodes as a nested list; actions(node) gives extra HTML (buttons) for a node
export function treeHtml(planet, currentKey, actions = () => '') {
  const kids = treeOf(planet);
  const walk = (parent) => {
    const a = kids.get(parent);
    if (!a) return '';
    return '<ul class="pl-tree">' + a.map((n) => `<li><div class="pl-node${n.key === currentKey ? ' cur' : ''}" data-key="${esc(n.key)}">
      <img src="${esc(n.thumb)}" alt="" loading="lazy" data-open="${esc(n.key)}" onerror="this.style.visibility='hidden'">
      <div class="tx"><div class="tt" data-open="${esc(n.key)}"><span class="pl-kind ${n.kind}">${kindName(n)}</span>${esc(n.id)}</div>
        <div class="sub">${esc(nodeWhen(n))}</div><div class="acts">${actions(n)}</div></div></div>${walk(n.key)}</li>`).join('') + '</ul>';
  };
  return walk('');
}

// the address that opens a node in the viewer
export function openUrl(planet, n) {
  const world = (id) => planet.nodes.find((x) => x.key === `world:${id}`)?.file || `${id}.json`;
  if (n.kind === 'run' || n.kind === 'timezoom' || n.kind === 'peoples') return `?run=${encodeURIComponent(n.id)}`;
  if (n.kind === 'world') return `?world=${encodeURIComponent(n.file)}`;
  return `?world=${encodeURIComponent(world(n.world))}&tab=zoom&zoom=${encodeURIComponent(n.id)}`;
}

// the node a planet card opens: its finished world, else a world, else its run
export function primaryNode(planet) {
  const w = planet.nodes.filter((n) => n.kind === 'world').sort((a, b) => (b.timezoom_kyr != null) - (a.timezoom_kyr != null) || b.created.localeCompare(a.created));
  return w[0] || planet.nodes.find((n) => n.kind === 'run') || planet.nodes[0];
}

// POST /api/<path>: the server's answer ({job: id}), or {error}. what (optional, e.g. 'zoom'): a server that answers
// 501, or 404 with no error of its own, predates that API, and the error says to restart it.
export async function postJob(path, body, what) {
  try {
    const r = await fetch('../api/' + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const out = await r.json().catch(() => ({}));
    if (what && (r.status === 501 || (r.status === 404 && !out.error))) return { error: `The server has no ${what} API. Restart it: uv run python -m planet serve` };
    return r.ok ? out : { error: out.error || `HTTP ${r.status}` };
  } catch (e) { return { error: 'The server is not reachable: ' + e.message }; }
}

// a job's state from the server. While it can't be reached (restarting: its jobs survive that, PW-085) keep
// asking, every 1.5 s for up to a minute.
async function fetchJob(id) {
  for (let k = 0; ; k++) {
    try { return await (await fetch(`../api/jobs/${id}`, { cache: 'no-store' })).json(); }
    catch (err) {
      if (k >= 40) return { status: 'error', error: 'lost the server: ' + err.message };
      await new Promise((ok) => setTimeout(ok, 1500));
    }
  }
}

// polls a job until it ends (returns its last state, done or error); onUpdate(job) on every poll, every `every` ms.
// alive (optional): checked before each poll; once it says no (another job took this one's place), stops and returns null.
export async function trackJob(id, onUpdate, every = 1500, alive = () => true) {
  while (alive()) {
    const j = await fetchJob(id);
    onUpdate(j);
    if (j.status === 'done' || j.status === 'error') return j;
    await new Promise((ok) => setTimeout(ok, every));
  }
  return null;
}

// stops a queued or running job (DELETE /api/jobs/<id>); what a make job already finished stays
export async function cancelJob(id) {
  try { const r = await fetch(`../api/jobs/${id}`, { method: 'DELETE' }); return r.ok ? await r.json() : null; } catch { return null; }
}

export const fmtDuration = (s) => (s < 90 ? `${Math.max(1, Math.round(s))} s` : s < 5400 ? `${Math.round(s / 60)} min` : `${(s / 3600).toFixed(1)} h`);

export async function deleteNode(n) {
  const dir = { run: 'runs', timezoom: 'runs', peoples: 'runs', world: 'worlds', zoom: 'zooms', fine: 'zooms' }[n.kind];
  const r = await fetch(`../${dir}/${n.id}`, { method: 'DELETE' });
  return r.ok;
}

// Favourites (planet/favourites.py): the owner's stars, kept by the server (GET / POST /api/favourites), never in the browser.
// A key is "<kind>:<id>" with kind run | world | zoom (time zooms are runs, fine zooms are zooms).
export const favKey = (n) => `${{ run: 'run', timezoom: 'run', peoples: 'run', world: 'world', zoom: 'zoom', fine: 'zoom' }[n.kind]}:${n.id}`;
export async function getFavourites() {
  try { return new Set(((await (await fetch('../api/favourites', { cache: 'no-store' })).json()).favourites || []).map((e) => `${e.kind}:${e.id}`)); } catch { return new Set(); }
}
export async function setFavourite(key, starred) {
  const [kind, ...id] = key.split(':');
  try { return (await fetch('../api/favourites', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ kind, id: id.join(':').replace(/\.json$/, ''), starred }) })).ok; } catch { return false; }
}
export const starHtml = (on, attrs = '') => `<button class="pl-btn sm star${on ? ' on' : ''}" ${attrs} title="${on ? 'Favourite: click to remove the star' : 'Star as a favourite (the default world for peoples runs)'}" aria-pressed="${on}">${on ? '\u2605' : '\u2606'}</button>`;
