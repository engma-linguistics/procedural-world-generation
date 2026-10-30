// The viewer's number formats, one copy for every page (PW-1047). A plain script, so the classic pages
// (lineages.html, techtab.js) load it with <script src>, and planets.js re-exports it to the ES modules.
//   num(v)    a measured value: 2,498 · 21.4 · 3.07 · 0.125 (thousands separated, about three significant figures)
//   count(n)  a head count or a big total, short: 310 M · 1.6 M · 12 k · 950
//   kyr(k)    a span of time given in kyr: 20 Myr · 1.25 Myr · 72 kyr · 3.5 kyr · 500 yr
//   ago(k)    a time before the present, in kyr: '72 kyr ago', 'the present'
(function (g) {
  const trim = (x, d) => String(+x.toFixed(d));
  const num = (v) => {
    const a = Math.abs(v);
    return a >= 100 ? Math.round(v).toLocaleString('en') : a >= 10 ? v.toFixed(1) : a >= 1 ? v.toFixed(2) : v.toFixed(3);
  };
  const count = (n) => (n >= 1e9 ? `${+(n / 1e9).toPrecision(2)} G` : n >= 1e6 ? `${+(n / 1e6).toPrecision(2)} M` : n >= 1e3 ? `${+(n / 1e3).toPrecision(2)} k` : `${Math.round(n)}`);
  const kyr = (k) => (k >= 1000 ? `${trim(k / 1000, k >= 10000 ? 0 : 2)} Myr` : k >= 1 ? `${trim(k, k >= 100 ? 0 : 1)} kyr` : `${Math.round(k * 1000)} yr`);
  const ago = (k) => (k <= 0 ? 'the present' : `${kyr(k)} ago`);
  g.NumFmt = { num, count, kyr, ago };
})(globalThis);
