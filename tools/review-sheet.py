#!/usr/bin/env python3
"""Build a self-contained review sheet for one language.

    python3 tools/review-sheet.py zh_CN
    python3 tools/review-sheet.py zh_CN zh_TW      # two side by side

Writes review-<locale>.html: every string with the screen it appears on, editable
in any browser with no internet, and a Download button that hands back a finished
catalogue you can drop into lang/ and open a pull request with.
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Link Robins — __TITLE__ review</title>
<style>
:root{color-scheme:light dark;--bg:#fff;--fg:#16181d;--muted:#6b7280;--line:#e5e7eb;--card:#fff;
--accent:#2563eb;--warn:#b45309;--warnbg:#fff7ed;--edited:#ecfdf5;--chip:#f3f4f6;}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--fg:#e6e8ee;--muted:#9aa1ad;--line:#262a33;
--card:#161922;--accent:#7aa2f7;--warn:#f3b055;--warnbg:#2a2114;--edited:#10241b;--chip:#1e222b;}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB",
"Microsoft YaHei","Noto Sans CJK SC","Noto Sans KR",Roboto,Helvetica,Arial,sans-serif;}
header{padding:28px 20px 18px;border-bottom:1px solid var(--line);max-width:1400px;margin:0 auto}
h1{font-size:21px;margin:0 0 6px}
header p{margin:6px 0;color:var(--muted);max-width:72ch}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
padding:10px 20px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.bar input[type=search],.bar select{background:var(--card);color:var(--fg);border:1px solid var(--line);
border-radius:8px;padding:7px 10px;font:inherit;font-size:13px}
.bar input[type=search]{min-width:220px;flex:1;max-width:340px}
.bar label{font-size:13px;color:var(--muted);display:flex;align-items:center;gap:5px}
.bar .sp{flex:1}
button.act{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:7px 12px;
font:inherit;font-size:13px;cursor:pointer}
button.ghost{background:var(--card);color:var(--fg);border:1px solid var(--line)}
#count{font-size:13px;color:var(--muted)}
main{max-width:1400px;margin:0 auto;padding:14px 20px 80px}
.grp{margin:26px 0 8px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:6px}
.row{content-visibility:auto;contain-intrinsic-size:auto 130px;border:1px solid var(--line);
border-radius:10px;background:var(--card);padding:12px 14px;margin:10px 0}
.row.edited{background:var(--edited)}
.meta{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;font-size:12px;color:var(--muted);margin-bottom:6px}
.meta .num{font-variant-numeric:tabular-nums}
.chip{background:var(--chip);border-radius:999px;padding:1px 8px}
.en{font-size:15px;margin:2px 0 10px;white-space:pre-wrap;word-break:break-word}
.en var{color:var(--accent);font-style:normal;font-weight:600}
.note{background:var(--warnbg);border-left:3px solid var(--warn);padding:6px 10px;border-radius:0 6px 6px 0;
font-size:13px;margin:0 0 10px;color:var(--fg)}
.pair{display:grid;grid-template-columns:repeat(__NCOLS__,1fr);gap:10px}
@media (max-width:760px){.pair{grid-template-columns:1fr}}
.fld label{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
textarea,input.cm{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--line);
border-radius:8px;padding:8px 10px;font:inherit;font-size:14px;resize:vertical}
textarea{min-height:52px}
textarea:focus,input.cm:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:transparent}
.cmwrap{margin-top:8px}
.hide{display:none!important}
footer{max-width:1400px;margin:0 auto;padding:0 20px 60px;color:var(--muted);font-size:13px}
</style>
</head>
<body>
<header>
  <h1>Link Robins dashboard — __TITLE__ review</h1>
  <p>Every string in the signed-in dashboard and the public status pages, with the screen it appears on.
  Type over anything that reads wrong; leaving a box untouched means “this one is fine”. Your edits save in
  this browser as you type, so you can close the file and come back to it.</p>
  <p>When you are done — or partway through — press <b>Download</b>. You get back finished catalogue files
  that drop straight into <code>lang/</code>, plus a CSV of your comments.</p>
  <p><b>Placeholders</b> like <var style="color:var(--accent);font-style:normal;font-weight:600">:count</var>
  are filled in by the app at runtime and must survive into the translation, spelled the same way. Rows marked
  <i>KEEP ENGLISH</i> are product or format names and stay in English on purpose.</p>
</header>

<div class="bar">
  <input type="search" id="q" placeholder="Search…">
  <select id="area"><option value="">All screens</option>__AREAOPTS__</select>
  <label><input type="checkbox" id="onlyNotes"> only rows with a note</label>
  <label><input type="checkbox" id="onlyEdits"> only my edits</label>
  <span id="count"></span>
  <span class="sp"></span>
  <button class="act" id="dl">Download</button>
  <button class="act ghost" id="reset">Clear my edits</button>
</div>

<main>
  <div id="strings"></div>
</main>
<footer>Generated from github.com/linkrobins/Languages · __NROWS__ strings</footer>

<script>
const ROWS = __ROWS__;
const LOCALES = __LOCALES__;
const KEY = 'lr-review-' + LOCALES.map(l => l.code).join('-');
let edits = {}, persists = true;
try { edits = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { edits = {}; persists = false; }
const save = () => {
  if (!persists) return;
  try { localStorage.setItem(KEY, JSON.stringify(edits)); } catch (e) { persists = false; warnNoSave(); }
};
function warnNoSave() {
  if (document.getElementById('nosave')) return;
  const p = document.createElement('p');
  p.id = 'nosave'; p.className = 'note';
  p.textContent = 'This browser will not let a local file store anything, so your edits live only in this ' +
    'tab — press Download before closing it.';
  document.querySelector('main').prepend(p);
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const markPh = s => esc(s).replace(/:[a-zA-Z_][a-zA-Z0-9_]*/g, m => '<var>' + m + '</var>');

const strings = document.getElementById('strings');
const frag = document.createDocumentFragment();
let lastArea = null;
for (const r of ROWS) {
  if (r.a !== lastArea) {
    const h = document.createElement('div');
    h.className = 'grp'; h.textContent = r.a;
    frag.appendChild(h); lastArea = r.a;
  }
  const e = edits[r.n] || {};
  const div = document.createElement('div');
  div.className = 'row' + (Object.keys(e).length ? ' edited' : '');
  div.dataset.n = r.n; div.dataset.area = r.a;
  div.dataset.hay = (r.e + ' ' + r.v.join(' ') + ' ' + r.w).toLowerCase();
  div.dataset.note = (r.o || r.k) ? '1' : '';
  const note = [r.k ? 'KEEP ENGLISH — this is a product or format name' : '', r.o].filter(Boolean).join(' · ');
  div.innerHTML =
    '<div class="meta"><span class="num">#' + r.n + '</span><span class="chip">' + esc(r.a) + '</span>' +
      '<span>' + esc(r.w) + '</span>' + (r.p ? '<span class="chip">' + esc(r.p) + '</span>' : '') + '</div>' +
    '<div class="en">' + markPh(r.e) + '</div>' +
    (note ? '<p class="note">' + esc(note) + '</p>' : '') +
    '<div class="pair">' + LOCALES.map((l, i) =>
      '<div class="fld"><label>' + esc(l.name) + '</label><textarea data-f="' + i + '" spellcheck="false">' +
      esc(e[i] !== undefined ? e[i] : r.v[i]) + '</textarea></div>').join('') + '</div>' +
    '<div class="cmwrap"><input class="cm" data-f="m" placeholder="Comment (optional)" value="' +
      esc(e.m || '') + '"></div>';
  frag.appendChild(div);
}
strings.appendChild(frag);

strings.addEventListener('input', ev => {
  const el = ev.target, row = el.closest('.row');
  if (!row) return;
  const n = row.dataset.n, f = el.dataset.f, orig = ROWS[n - 1];
  const base = f === 'm' ? '' : orig.v[+f];
  const e = edits[n] || (edits[n] = {});
  if (el.value === base || (f === 'm' && !el.value.trim())) delete e[f]; else e[f] = el.value;
  if (!Object.keys(e).length) delete edits[n];
  row.classList.toggle('edited', !!edits[n]);
  save(); refresh();
});

const q = document.getElementById('q'), area = document.getElementById('area');
const onlyNotes = document.getElementById('onlyNotes'), onlyEdits = document.getElementById('onlyEdits');
const countEl = document.getElementById('count');
function refresh() {
  const term = q.value.trim().toLowerCase(), a = area.value;
  let shown = 0;
  for (const row of strings.querySelectorAll('.row')) {
    const ok = (!term || row.dataset.hay.includes(term)) &&
               (!a || row.dataset.area === a) &&
               (!onlyNotes.checked || row.dataset.note) &&
               (!onlyEdits.checked || edits[row.dataset.n]);
    row.classList.toggle('hide', !ok); if (ok) shown++;
  }
  for (const h of strings.querySelectorAll('.grp')) {
    let any = false;
    for (let s = h.nextElementSibling; s && s.classList.contains('row'); s = s.nextElementSibling)
      if (!s.classList.contains('hide')) { any = true; break; }
    h.classList.toggle('hide', !any);
  }
  const n = Object.keys(edits).length;
  countEl.textContent = shown + ' shown · ' + n + ' edit' + (n === 1 ? '' : 's') + ' saved';
}
[q, area].forEach(el => el.addEventListener('input', refresh));
[onlyNotes, onlyEdits].forEach(el => el.addEventListener('change', refresh));
refresh();

function drop(name, text, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], {type: type + ';charset=utf-8'}));
  a.download = name; a.click(); URL.revokeObjectURL(a.href);
}
document.getElementById('dl').onclick = () => {
  LOCALES.forEach((l, i) => {
    const out = {};
    for (const r of ROWS) {
      const e = edits[r.n] || {};
      out[r.e] = e[i] !== undefined ? e[i] : r.v[i];
    }
    drop(l.code + '.json', JSON.stringify(out, null, 4) + '\n', 'application/json');
  });
  const qt = s => '"' + String(s == null ? '' : s).replace(/"/g, '""') + '"';
  const head = ['#', 'Screen', 'English'];
  LOCALES.forEach(l => head.push(l.name + ' before', l.name + ' after'));
  head.push('Comment');
  const lines = [head.map(qt).join(',')];
  for (const r of ROWS) {
    const e = edits[r.n]; if (!e) continue;
    const cells = [r.n, r.a + ' · ' + r.w, r.e];
    LOCALES.forEach((l, i) => cells.push(r.v[i], e[i] !== undefined ? e[i] : r.v[i]));
    cells.push(e.m || '');
    lines.push(cells.map(qt).join(','));
  }
  drop('comments.csv', '﻿' + lines.join('\r\n'), 'text/csv');
};
document.getElementById('reset').onclick = () => {
  if (!confirm('Clear every edit stored in this browser?')) return;
  edits = {}; save(); location.reload();
};
</script>
</body>
</html>
"""


def main():
    codes = sys.argv[1:]
    if not codes:
        print(__doc__.strip())
        return 1

    cats = []
    for code in codes:
        path = os.path.join(ROOT, 'lang', code + '.json')
        if not os.path.exists(path):
            print('no such catalogue: lang/%s.json' % code)
            return 1
        with open(path, encoding='utf-8') as f:
            cat = json.load(f)
        cats.append({'code': code, 'name': cat.get('lang_name', code), 'strings': cat})

    with open(os.path.join(ROOT, 'context', 'strings.csv'), encoding='utf-8') as f:
        context = list(csv.DictReader(f))

    rows = []
    for i, c in enumerate(context, 1):
        key = c['English']
        rows.append({
            'n': i, 'a': c['Where it appears'], 'w': c['Screen / file'], 'e': key,
            'p': c['Placeholders'], 'o': c['Note'], 'k': 1 if c['Keep English'] else 0,
            'v': [cat['strings'].get(key, '') for cat in cats],
        })

    areas = sorted({r['a'] for r in rows})
    title = ' / '.join(c['name'] for c in cats)
    html = (TEMPLATE
            .replace('__ROWS__', json.dumps(rows, ensure_ascii=False))
            .replace('__LOCALES__', json.dumps([{'code': c['code'], 'name': c['name']} for c in cats],
                                               ensure_ascii=False))
            .replace('__AREAOPTS__', ''.join('<option>%s</option>' % a for a in areas))
            .replace('__NCOLS__', str(len(cats)))
            .replace('__NROWS__', str(len(rows)))
            .replace('__TITLE__', title))

    out = os.path.join(ROOT, 'review-%s.html' % '-'.join(codes))
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote %s — %d strings, %s' % (os.path.relpath(out, ROOT), len(rows), title))
    return 0


if __name__ == '__main__':
    sys.exit(main())
