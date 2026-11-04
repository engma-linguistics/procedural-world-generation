// The viewer's number formats, one copy for every page (PW-1047). A plain script, so the classic pages
// (lineages.html, techtab.js) load it with <script src>, and planets.js re-exports it to the ES modules.
//   num(v)    a measured value: 2,498 · 21.4 · 3.07 · 0.125 (thousands separated, about three significant figures)
//   count(n)  a head count or a big total, short: 310 M · 1.6 M · 12 k · 950
//   kyr(k)    a span of time given in kyr: 20 Myr · 1.25 Myr · 72 kyr · 3.5 kyr · 500 yr
//   ago(k)    a DATE, k kyr before the present (years everywhere, PW-1429): '12,400 years ago', 'the present'; once
//             setPresent(N) is called ("the present is year N"): 'year 1400', or 'N before year 1' before year 1.
//             Use it (or date) for every point in time a person reads; kyr() is only for spans ('lasted 3.5 kyr').
//   date(k)   the same, without the word 'ago' ('12,400 years' is not a date), for 'since X' / 'from X' phrases:
//             'since 12,400 years ago' is written since(k) -> 'since 12,400 years ago' / 'since year 1400'
//   since(k)  'since ' + ago(k)
//   parseDate(text, dflt)  what a person typed -> kyr ago (null if unreadable): 'year 1400', '300 before year 1',
//             '12400 years ago', '12400 yr', '12.4 kyr', '8 Myr'; a bare number counts as `dflt` ('kyr', 'year' or
//             'ago' = years ago; default 'kyr'); with a present set, 'year' is read as a calendar year.
//   setPresent(n, runId) / present(runId)  the optional 'present is year N' (null clears), kept in localStorage
//             per run (key 'pw-present-year:<run>', plus '*' = last chosen, the default for runs with none);
//             NumFmt.run is the run the page is showing (set it when a run opens). Pages re-draw after a change.
//   yearsAgo(k)  k kyr as 'N years' (3 significant figures, thousands separated): a span in plain years.
(function (g) {
  const trim = (x, d) => String(+x.toFixed(d));
  const num = (v) => {
    const a = Math.abs(v);
    return a >= 100 ? Math.round(v).toLocaleString('en') : a >= 10 ? v.toFixed(1) : a >= 1 ? v.toFixed(2) : v.toFixed(3);
  };
  const count = (n) => (n >= 1e9 ? `${+(n / 1e9).toPrecision(2)} G` : n >= 1e6 ? `${+(n / 1e6).toPrecision(2)} M` : n >= 1e3 ? `${+(n / 1e3).toPrecision(2)} k` : `${Math.round(n)}`);
  const kyr = (k) => (k >= 1000 ? `${trim(k / 1000, k >= 10000 ? 0 : 2)} Myr` : k >= 1 ? `${trim(k, k >= 100 ? 0 : 1)} kyr` : `${Math.round(k * 1000)} yr`);
  const KEY = 'pw-present-year:';
  const store = () => { try { return g.localStorage || null; } catch (e) { return null; } };
  const read = (k) => { try { return store()?.getItem(KEY + k) ?? null; } catch (e) { return null; } };
  const write = (k, v) => { try { if (v == null) store()?.removeItem(KEY + k); else store()?.setItem(KEY + k, v); } catch (e) { /* no storage: the setting just does not stick */ } };
  // the present year of a run: its own setting, else the one last chosen anywhere ('*'), so a freshly made run keeps it
  const present = (run) => {
    const v = read(run === undefined ? NumFmt.run : run) ?? read('*');
    return v == null || v === 'none' || v === '' || Number.isNaN(+v) ? null : +v;
  };
  const setPresent = (n, run) => {
    const none = n == null || n === '' || Number.isNaN(+n), v = none ? 'none' : String(Math.round(+n)), id = run === undefined ? NumFmt.run : run;
    if (id) write(id, v);
    write('*', none ? null : v);
  };
  const sig3 = (y) => { if (y < 1000) return Math.round(y); const m = 10 ** (Math.floor(Math.log10(y)) - 2); return Math.round(y / m) * m; };
  const yearsAgo = (k) => { const y = sig3(k * 1000); return `${y.toLocaleString('en')} ${y === 1 ? 'year' : 'years'}`; };
  const calendar = (k, p) => { const y = Math.round(p - k * 1000); return y >= 1 ? `year ${y.toLocaleString('en').replace(/,/g, '')}` : `${(1 - y).toLocaleString('en').replace(/,/g, '')} before year 1`; };
  const ago = (k, p) => {
    if (k == null || Number.isNaN(k)) return '?';
    p = p === undefined ? present() : p;
    if (p != null) return calendar(Math.max(k, 0), p);
    return k <= 0.0005 ? 'the present' : `${yearsAgo(k)} ago`;
  };
  const date = ago;
  const since = (k, p) => `since ${ago(k, p)}`;
  const parseDate = (text, dflt = 'kyr', p) => {
    if (typeof text === 'number') return text;
    const t = String(text ?? '').trim().toLowerCase().replace(/,/g, '');
    if (!t) return null;
    p = p === undefined ? present() : p;
    let m = t.match(/^(-?[0-9.]+)\s*before\s+year\s*1$/);  // N before year 1
    if (m) return p == null ? null : (p - (1 - +m[1])) / 1000;
    m = t.match(/^(?:year\s*)(-?[0-9.]+)$/) || (dflt === 'year' && t.match(/^(-?[0-9.]+)$/));  // year N
    if (m) return p == null ? null : (p - +m[1]) / 1000;
    if (t === 'the present' || t === 'now' || t === 'present') return 0;
    m = t.match(/^([0-9.]+(?:e[+-]?[0-9]+)?)\s*(myr|ma|mya|kyr|ka|kya|yr|y|years?|bp)?(?:\s*ago)?$/);
    if (!m || Number.isNaN(+m[1])) return null;
    const x = +m[1], u = m[2] || (dflt === 'ago' ? 'yr' : 'kyr');
    return ['myr', 'ma', 'mya'].includes(u) ? x * 1000 : ['yr', 'y', 'year', 'years', 'bp'].includes(u) ? x / 1000 : x;
  };
  g.NumFmt = { num, count, kyr, ago, date, since, yearsAgo, parseDate, present, setPresent, run: null };
})(globalThis);
