#!/usr/bin/env python3
"""Write ../../valley-flyover.html (the viewer's sample page) from rubric_human.json and rubric_carbon.json.

Run from anywhere after re-grading:  python3 valley-flyover/grading/build_sample_page.py
"""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
rub = lambda f: json.load(open(os.path.join(HERE, '..', f)))
GRADERS = [('human', 'Human', rub('rubric_human.json')), ('carbon', 'Gemini 4 Carbon', rub('rubric_carbon.json'))]
d = GRADERS[0][2]
esc = html.escape
ICON_BOOK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 7v14"/><path d="M16 12h2"/><path d="M16 8h2"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/><path d="M6 12h2"/><path d="M6 8h2"/></svg>'
ICON_FILM = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M3 7.5h4"/><path d="M3 12h18"/><path d="M3 16.5h4"/><path d="M17 3v18"/><path d="M17 7.5h4"/><path d="M17 16.5h4"/></svg>'
word = {True: ('Pass', 'yes'), False: ('Fail', 'no'), None: ('Unverified', 'unv')}
VERS = [('m', 'mc', "Gemini 4 Carbon's version"), ('r', 'rc', 'Human version')]   # the two code versions being graded
G = {gid: {r['n']: r for r in data['rubric']} for gid, _, data in GRADERS}
n = len(d['rubric'])
# one table: a row per criterion, and for each version one cell per grader
COLS = [(k, kc, gid) for k, kc, _ in VERS for gid, _, _ in GRADERS]
passed = {(k, gid): sum(G[gid][r['n']][k] is True for r in d['rubric']) for k, _, gid in COLS}
head1 = ''.join(f'<th colspan="{len(GRADERS)}" class="ver">{esc(name)}</th>' for _, _, name in VERS)
head2 = ''.join(f'<th class="g{" first" if gid == GRADERS[0][0] else ""}">{esc(gname)} grade<span>{passed[(k, gid)]} of {n} passed</span></th>' for k, _, _ in VERS for gid, gname, _ in GRADERS)
rows = []; ndiff = 0; last = None
for r in d['rubric']:
    if r['d'] != last:
        last = r['d']; grp = [x for x in d['rubric'] if x['d'] == last]
        same = all(G[GRADERS[0][0]][x['n']][k] == G[GRADERS[1][0]][x['n']][k] for x in grp for k, _, _ in VERS)
        gate = ' <span class="tag">Gate</span>' if any(x['n'].startswith('G') for x in grp) else ''
        rows.append(f'<tr class="grp{" same" if same else ""}"><th colspan="{2 + len(COLS)}">{esc(last)}{gate}</th></tr>')
    differs = {k: len({G[gid][r['n']][k] for gid, _, _ in GRADERS}) > 1 for k, _, _ in VERS}
    ndiff += any(differs.values())
    cells = ''
    for k, kc, gid in COLS:
        x = G[gid][r['n']]; w = word[x[k]]
        cells += (f'<td class="v{" first" if gid == GRADERS[0][0] else ""}{" diff" if differs[k] else ""}"><b class="{w[1]}">{w[0]}</b>'
                  + (f'<p>{esc(x[kc])}</p>' if x[kc] else '') + '</td>')
    rows.append(f'<tr class="{"" if any(differs.values()) else "same"}"><td class="n">{esc(r["n"])}</td><td class="crit">{esc(r["c"])}</td>{cells}</tr>')
table = (f'<div class="table-wrap big"><table class="rubric grades"><thead><tr><th rowspan="2" class="n">#</th><th rowspan="2">Criterion</th>{head1}</tr><tr>{head2}</tr></thead>'
         f'<tbody>{"".join(rows)}</tbody></table></div>')
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Valley Flyover</title>
<link rel="stylesheet" href="css/docs.css">
<style>
.doc p.note {{ color: var(--ink-2); margin: 0 0 4px; max-width: 68ch; }}
.player {{ position: relative; width: 100%; height: clamp(430px, 31vw, 560px); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: #0b0f14; }}
.player iframe {{ position: absolute; inset: 0; width: 100%; height: 100%; border: 0; display: block; }}
.title-row .btn {{ text-decoration: none; }}
@media (max-width: 760px) {{ .player {{ height: 620px; }} }}
/* rubric: one table, a row per criterion; for each version, the human grade then Gemini 4 Carbon's */
.doc.wide > section.rub > h2 {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid var(--line); }}
.rub-head {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 16px; margin: 12px 0 8px; }}
.rub-head .count {{ font: 400 12px/1.4 var(--mono); color: var(--ink-2); }}
.btn[aria-pressed="true"] {{ border-color: var(--accent); color: var(--accent); }}
.yes {{ color: #4ADE80; }} .no {{ color: #F87171; }} .unv {{ color: #E6B450; }}
table.grades {{ min-width: 1040px; table-layout: fixed; }}
table.grades th, table.grades td {{ padding: 10px 12px; }}
table.grades thead th {{ vertical-align: bottom; }}
table.grades thead th.ver {{ text-align: left; color: var(--ink); border-left: 1px solid var(--line); }}
table.grades thead th.g span {{ display: block; margin-top: 4px; letter-spacing: 0.04em; text-transform: none; }}
table.grades thead th.g.first, table.grades td.v.first {{ border-left: 1px solid var(--line); }}
table.grades th.n, table.grades td.n {{ width: 44px; font: 400 11px/2 var(--mono); color: var(--ink-2); }}
table.grades td:first-child {{ width: 44px; }}
table.grades td.crit {{ width: 24%; font-size: 14px; line-height: 1.5; }}
table.grades td.v b {{ font: 600 11px/1.6 var(--mono); letter-spacing: 0.1em; text-transform: uppercase; }}
table.grades td.v p {{ margin: 4px 0 0; font-size: 13.5px; line-height: 1.5; color: var(--ink-2); }}
table.grades tr.grp th {{ text-align: left; }}
table.grades .tag {{ font: 500 10px/1 var(--mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-2); border: 1px solid #3A3A3A; border-radius: 4px; padding: 3px 5px; margin-left: 8px; }}
.rub.only-diff tr.same {{ display: none; }}
.rub.only-diff td.v.diff {{ background: rgba(230, 180, 80, 0.07); }}
</style>
</head>
<body>
<nav class="side" aria-label="Pages">
  <a href="index.html">{ICON_BOOK}<span>Overview</span></a>
  <span class="group">Samples</span>
  <a href="valley-flyover.html" aria-current="page">{ICON_FILM}<span>Valley Flyover</span></a>
</nav>
<main class="main"><article class="doc wide">
<header class="title-row"><div><h1>Valley Flyover</h1></div><a class="btn" href="valley-flyover/player.html" target="_blank" rel="noopener">Open full screen</a></header>
<div class="player"><iframe src="valley-flyover/player.html" title="Original video, Gemini 4 Carbon version and Human version, side by side" allow="autoplay"></iframe></div>
<div class="prompt"><div><div class="label">Prompt sent to Gemini 4 Carbon, with the video</div><p>{esc(d["prompt"])}</p></div></div>
<section class="rub">
<h2>Rubric</h2>
<div class="rub-head"><span class="count" id="count">{n} criteria</span><button class="btn" id="diff" type="button" aria-pressed="false">Disagreements only ({ndiff})</button></div>
{table}
</section>
</article></main>
<script>
const diff = document.getElementById('diff'), rubEl = document.querySelector('.rub'), count = document.getElementById('count');
diff.addEventListener('click', () => {{
  const on = diff.getAttribute('aria-pressed') !== 'true';
  diff.setAttribute('aria-pressed', on); rubEl.classList.toggle('only-diff', on);
  count.textContent = on ? '{ndiff} of {n} criteria: the two graders disagree on the highlighted cells' : '{n} criteria';
}});
</script>
</body>
</html>
'''
open(os.path.join(ROOT, 'valley-flyover.html'), 'w').write(page)
print('wrote valley-flyover.html:', n, 'criteria,', ndiff, 'with a disagreement; passed', passed)
