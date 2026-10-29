'use strict';
// Shared by the five tech-tree mockups: the data (tech-data.js, window.TT), the viewer's colours and a few helpers.
const D = window.TT;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function fmt(k) {  // (as viewer/lineages.html)
  if (k >= 1000) return `${+(k / 1000).toFixed(k >= 10000 ? 0 : 2)} Myr`;
  if (k >= 1) return `${+k.toFixed(k >= 100 ? 0 : 1)} kyr`;
  return `${Math.round(k * 1000)} yr`;
}
const ago = (k) => (k <= 0 ? 'the present' : fmt(k) + ' ago');
// how a people came to know a tech: the Technology tab's colours
const HOW_COL = { invented: '#ffd27a', contact: '#7fb0ff', kit: '#c79bff', inherited: '#8fa0b4', tamed: '#6bd6a0', shared: '#6bd6d0' };
const howCol = (how) => HOW_COL[how] || (String(how).startsWith('with') ? '#6bd6a0' : '#aaa');
const HOW_TEXT = { invented: 'invented', contact: 'by contact', kit: 'brought along (kit)', inherited: 'inherited at the split', tamed: 'by taming', shared: 'shared with its people' };
const howText = (how) => HOW_TEXT[how] || how;
const TRACK_COL = { communication: '#7cc4ff', fire: '#ff9d6b', tools: '#c9b08a', food: '#9fd18b', shelter: '#e3c26b', travel: '#6bd6d0', social: '#ff8fc8', arcane: '#c79bff' };
const ERAS = ['stone age', 'bronze age', 'classical', 'medieval', 'renaissance', 'industrial'];
const TECH = Object.fromEntries(D.techs.map((t) => [t.id, t]));
const LINE = Object.fromEntries(D.lines.map((l) => [l.id, l]));
const TRACK = Object.fromEntries(D.tracks.map((k) => [k.id, k]));
const short = (id) => (LINE[id]?.name || id);
const tname = (id) => (TECH[id]?.name || id).split(' (')[0];
const sw = (id) => `<span class="sw" style="background:${LINE[id]?.color || '#888'}"></span>`;
const startOf = (l) => l.started_kyr ?? 0;
// peoples with a tech record, oldest first; "now": alive at the present
const PEOPLES = D.lines.filter((l) => l.in_tree).sort((a, b) => startOf(b) - startOf(a));
const alive = (l) => l.leaf && l.ended_kyr == null;
// everything a tech needs, all the way down
function closure(ids) {
  const out = new Set(), todo = [...ids];
  while (todo.length) { const i = todo.pop(); if (!out.has(i)) { out.add(i); todo.push(...(TECH[i]?.needs || [])); } }
  return out;
}
const users = {};  // tech -> the techs that need it directly
for (const t of D.techs) for (const n of t.needs) (users[n] ||= []).push(t.id);
// a log time axis, kyr ago -> 0..1 (0 the oldest, 1 the present)
function logAxis(oldest, near = 0.1) {
  const lo = Math.log10(near), hi = Math.log10(oldest);
  const f = (k) => 1 - (Math.log10(Math.max(k, near)) - lo) / (hi - lo);
  f.inv = (u) => 10 ** (lo + (1 - u) * (hi - lo));
  f.ticks = [0.1, 1, 10, 100, 1000, 10000].filter((k) => k <= oldest * 1.01 && k >= near);
  return f;
}
// the floating tip
const tip = document.createElement('div');
tip.className = 'tip';
document.addEventListener('DOMContentLoaded', () => document.body.appendChild(tip));
function showTip(e, html) {
  tip.innerHTML = html; tip.style.display = 'block';
  const r = tip.getBoundingClientRect();
  let x = e.clientX + 14, y = e.clientY + 12;
  if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 14;
  if (y + r.height > innerHeight - 8) y = Math.max(8, innerHeight - r.height - 8);
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}
const hideTip = () => { tip.style.display = 'none'; };
function techTip(id, extra = '') {
  const t = TECH[id], f = D.firsts[id];
  const land = [...t.env, ...(t.env_any.length ? ['one of ' + t.env_any.join(' / ')] : [])].join(', ');
  return `<b>${esc(t.name)}</b><div class="muted">${esc(TRACK[t.track].name)} · ${esc(t.era)}${t.fantasy ? ' · fantasy' : ''}</div>
    <div>needs: ${t.needs.length ? t.needs.map((n) => esc(tname(n))).join(', ') : '<span class="muted">nothing</span>'}</div>
    ${land ? `<div>land: ${esc(land)}</div>` : ''}
    <div>earliest ${t.earliest_kyr ?? '?'} kyr${t.elder_kyr ? ` (elder kinds ${t.elder_kyr})` : ''}</div>
    <div>first: ${f ? `${sw(f.line)}${esc(short(f.line))}, ${ago(f.ago_kyr)} (${esc(f.how)})` : '<span class="muted">nobody</span>'}</div>
    ${extra}<div class="muted src">${esc(t.source)}</div>`;
}
// the header strip linking the five views
function header(cur, extra = '') {
  const views = [['view1-civ-tree.html', 'Tree'], ['view2-timeline.html', 'Timeline'], ['view3-map.html', 'Map'],
    ['view4-inventory.html', 'Inventory'], ['view5-diffusion.html', 'Diffusion']];
  return `<b>Technology</b><span class="muted">mockup · run ${esc(D.run)} on world ${esc(D.world)} · ${esc(D.tree)} · ${D.techs.length} techs in ${D.tracks.length} tracks · ${PEOPLES.length} peoples · era cap ${esc(D.era)}</span>
    <span style="flex:1"></span>${views.map(([f, n]) => `<a href="${f}" class="${f.startsWith(cur) ? 'cur' : ''}">${n}</a>`).join(' ')} <a href="index.html">index</a>${extra}`;
}
