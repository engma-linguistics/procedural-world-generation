// Type-to-filter for the run / world / zoom pickers (PW-407): a search box above a <select> that narrows its
// options to those whose text, value, title or group label contains every typed word (an id such as b3c260, part
// of a name, a run id in the zoom picker). Enter opens the single match (or drops the list open when several
// match); Escape clears. Picking an option clears the filter again, so the list is whole whenever it's not in use.
// The page fills the <select> as before; a MutationObserver keeps the full option list this filters from.
'use strict';
(() => {
  const css = document.createElement('style');
  css.textContent = `.pickFilter { display: flex; gap: 6px; align-items: center; margin: 0 0 4px; }
    .pickFilter input { flex: 1; min-width: 0; background: #111827; color: var(--text, #dfe6f0);
      border: 1px solid var(--border, #2a3446); border-radius: 4px; padding: 3px 6px; font: inherit; font-size: 12px; }
    .pickFilter input:focus { outline: none; border-color: var(--accent, #7cc4ff); }
    .pickFilter .n { color: var(--muted, #8b97a8); font-size: 11px; white-space: nowrap; }
    .pickFilter .n:empty { display: none; }`;
  document.head.appendChild(css);

  window.addPickerFilter = (sel, { placeholder = 'filter: part of an id or name' } = {}) => {
    const wrap = document.createElement('div');
    wrap.className = 'pickFilter';
    wrap.innerHTML = '<input type="search" spellcheck="false" autocomplete="off"><span class="n"></span>';
    const box = wrap.firstChild, count = wrap.lastChild;
    box.placeholder = placeholder;
    box.title = 'Type part of an id (e.g. b3c260) or a name to narrow the list; Enter opens the single match, Esc clears';
    const row = sel.closest('.row') || sel;
    row.parentNode.insertBefore(wrap, row);

    let all = [];        // the full list (clones of the page's optgroups / options)
    let open = '';       // the value the page has open (kept while a filter hides it)
    let built = [];      // the nodes of our last rewrite (to tell it from the page refilling the list)
    const snap = () => { all = [...sel.children].map((n) => n.cloneNode(true)); if (sel.value) open = sel.value; };
    new MutationObserver(() => {
      const kids = [...sel.children];
      if (kids.length === built.length && kids.every((k, i) => k === built[i])) return;
      snap();
      if (box.value.trim()) apply();
    }).observe(sel, { childList: true });
    snap();

    const hay = (o, g) => `${o.value} ${o.textContent} ${o.title || ''} ${g ? g.label : ''}`.toLowerCase();
    const matches = () => {
      const words = box.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const out = [];
      for (const n of all) {
        if (n.tagName === 'OPTGROUP') {
          const os = [...n.children].filter((o) => words.every((w) => hay(o, n).includes(w)));
          if (os.length) out.push([n, os]);
        } else if (words.every((w) => hay(n, null).includes(w))) out.push([null, [n]]);
      }
      return out;
    };
    const total = () => all.reduce((s, n) => s + (n.tagName === 'OPTGROUP' ? n.children.length : 1), 0);

    function apply() {
      if (sel.value) open = sel.value;
      if (!box.value.trim()) {
        built = all.map((n) => n.cloneNode(true));
        sel.replaceChildren(...built);
        sel.value = open;
        count.textContent = '';
        return;
      }
      const m = matches(), n = m.reduce((s, [, os]) => s + os.length, 0);
      const kids = m.map(([g, os]) => {
        if (!g) return os[0].cloneNode(true);
        const ng = g.cloneNode(false);
        ng.append(...os.map((o) => o.cloneNode(true)));
        return ng;
      });
      const hasOpen = m.some(([, os]) => os.some((o) => o.value === open));
      if (!hasOpen) {  // a heading, so that picking any match is a change (and the open item isn't shown as picked)
        const h = document.createElement('option');
        h.value = ''; h.disabled = true;
        h.textContent = n ? `${n} match${n > 1 ? 'es' : ''}: pick one` : 'no match';
        kids.unshift(h);
      }
      built = kids;
      sel.replaceChildren(...kids);
      sel.value = hasOpen ? open : '';
      count.textContent = `${n} / ${total()}`;
    }

    const clear = () => { if (box.value) { box.value = ''; apply(); } };
    box.addEventListener('input', apply);
    box.addEventListener('keydown', (e) => {
      e.stopPropagation();  // (the pages' key shortcuts: N, space, Escape)
      if (e.key === 'Escape') { clear(); box.blur(); }
      if (e.key !== 'Enter') return;
      const m = matches().flatMap(([, os]) => os);
      if (m.length === 1) {
        const v = m[0].value;
        box.value = ''; apply();
        if (v !== open) { sel.value = v; open = v; sel.dispatchEvent(new Event('change', { bubbles: true })); }
      } else if (m.length > 1) {
        sel.focus();
        try { sel.showPicker(); } catch { /* (older browsers: the list stays narrowed, pick from it) */ }
      }
    });
    // a pick from the narrowed list: let the page open it, then show the whole list again
    sel.addEventListener('change', () => {
      if (sel.value) open = sel.value;
      if (box.value) setTimeout(clear, 0);
    });
    return box;
  };
})();
