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
VERS = [('m', 'mc', 'Carbon', 'Gemini 4 Carbon'), ('r', 'rc', 'Human', 'Human')]   # the two code versions being graded
n = len(d['rubric'])

def panel(gid, gname, data, hidden):
    groups = []
    for r in data['rubric']:
        if not groups or groups[-1][0] != r['d']: groups.append((r['d'], []))
        groups[-1][1].append(r)
    secs = []
    for name, rows in groups:
        gate = any(r['n'].startswith('G') for r in rows)
        tally = ' &middot; '.join(f'{lab} {sum(r[k] is True for r in rows)}/{len(rows)}' for k, _, lab, _ in VERS)
        items = ''
        for r in rows:
            marks = ''.join(f'<span class="{word[r[k]][1]}"><i>{lab}</i> {word[r[k]][0]}</span>' for k, _, lab, _ in VERS)
            body = ''.join(f'<div class="k">{esc(full)} &middot; <span class="{word[r[k]][1]}">{word[r[k]][0]}</span></div>'
                           + (f'<p class="txt reply">{esc(r[kc])}</p>' if r[kc] else '') for k, kc, _, full in VERS)
            items += (f'<details class="acc"><summary><span class="n">{esc(r["n"])}</span><span class="p">{esc(r["c"])}</span>'
                      f'<span class="t">{marks}</span></summary><div class="body">{body}</div></details>')
        tag = '<span class="tag">Gate</span>' if gate else ''
        secs.append(f'<details class="sec"><summary><h2>{esc(name)}</h2>{tag}<span class="label">{tally}</span></summary><div class="accs">{items}</div></details>')
    cnt = {k: (sum(r[k] is True for r in data['rubric']), sum(r[k] is False for r in data['rubric'])) for k, _, _, _ in VERS}
    rows = ''.join(f'<tr><td>{esc(full)}</td><td class="mono yes">{cnt[k][0]}</td><td class="mono no">{cnt[k][1]}</td></tr>' for k, _, _, full in VERS)
    table = f'<div class="tally table-wrap"><table class="rubric plain"><thead><tr><th>Version</th><th class="num">Passed</th><th class="num">Failed</th></tr></thead><tbody>{rows}</tbody></table></div>'
    return f'<div class="grader" id="by-{gid}" role="tabpanel"{" hidden" if hidden else ""}>{table}{"".join(secs)}</div>', cnt

panels = []; counts = {}
for i, (gid, gname, data) in enumerate(GRADERS):
    h, counts[gid] = panel(gid, gname, data, i > 0); panels.append(h)
tabs = ''.join(f'<button type="button" role="tab" data-g="{gid}" aria-selected="{"true" if i == 0 else "false"}">{esc(gname)}</button>' for i, (gid, gname, _) in enumerate(GRADERS))
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
/* rubric accordion: one section per dimension, one row per criterion */
.doc.wide > section.rub > h2 {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid var(--line); }}
.rub-head {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 16px; margin: 12px 0 8px; }}
.tally {{ max-width: 420px; margin: 0 0 14px; }}
.seg {{ display: inline-flex; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
.seg button {{ font: 500 12px/1 var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-2); background: transparent; border: 0; padding: 9px 12px; cursor: pointer; }}
.seg button + button {{ border-left: 1px solid var(--line); }}
.seg button[aria-selected="true"] {{ background: var(--side); color: var(--ink); }}
.seg button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: -2px; }}
.rub-head .by {{ display: flex; align-items: center; gap: 10px; font: 400 11px/1 var(--mono); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-2); }}
.grader[hidden] {{ display: none; }}
.tally td.mono, .tally th.num {{ text-align: right; font-weight: 600; }}
.yes {{ color: #4ADE80; }} .no {{ color: #F87171; }}
.prompt {{ display: flex; gap: 14px; align-items: center; margin: 14px 0 0; padding: 12px 14px; background: var(--side); border: 1px solid var(--line); border-radius: 8px; }}
.prompt p {{ margin: 4px 0 0; font-size: 15px; color: var(--ink); }}
.unv {{ color: #E6B450; }}
.rub details.sec {{ margin-top: 0; }}
.rub details.sec:last-child {{ border-bottom: 1px solid var(--line); }}
.rub details.sec > summary {{ padding: 14px 4px; }}
.rub .tag {{ font: 500 10px/1 var(--mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-2); border: 1px solid #3A3A3A; border-radius: 4px; padding: 4px 6px; }}
.rub .accs {{ margin: 0 0 14px 24px; }}
.rub .acc .p {{ white-space: normal; overflow: visible; }}
.rub .acc[open] .p {{ color: var(--ink); }}
.rub .acc summary {{ grid-template-columns: 3em 1fr auto; }}
.rub .acc .t {{ display: flex; gap: 14px; font-weight: 600; text-transform: uppercase; }}
.rub .acc .t i {{ font-style: normal; font-weight: 400; color: var(--ink-2); }}
.rub .acc .k span {{ font-weight: 600; }}
.rub .acc .body {{ padding-top: 0; }}
.rub .acc .k {{ margin-top: 2px; }}
@media (max-width: 640px) {{ .rub .accs {{ margin-left: 0; }} .rub .acc summary {{ grid-template-columns: 2.4em 1fr; }} .rub .acc .t {{ display: flex; grid-column: 2; line-height: 1.4; }} .rub details.sec > summary {{ flex-wrap: wrap; }} }}
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
<div class="rub-head"><div class="by"><span>Graded by</span><div class="seg" role="tablist" aria-label="Grader">{tabs}</div></div><button class="btn" id="toggle" type="button" aria-expanded="false">Expand all</button></div>
{"".join(panels)}
</section>
</article></main>
<script>
const btn = document.getElementById('toggle'), tabs = [...document.querySelectorAll('.seg button')];
const shown = () => document.querySelector('.grader:not([hidden])');
const setOpen = open => {{ shown().querySelectorAll('details').forEach(el => {{ el.open = open; }}); btn.setAttribute('aria-expanded', open); btn.textContent = open ? 'Collapse all' : 'Expand all'; }};
btn.addEventListener('click', () => setOpen(btn.getAttribute('aria-expanded') !== 'true'));
tabs.forEach(t => t.addEventListener('click', () => {{
  const open = btn.getAttribute('aria-expanded') === 'true';
  tabs.forEach(x => x.setAttribute('aria-selected', x === t));
  document.querySelectorAll('.grader').forEach(g => {{ g.hidden = g.id !== 'by-' + t.dataset.g; }});
  setOpen(open);
}}));
</script>
</body>
</html>
'''
open(os.path.join(ROOT, 'valley-flyover.html'), 'w').write(page)
print('wrote valley-flyover.html:', n, 'criteria; pass/fail per grader', counts)
