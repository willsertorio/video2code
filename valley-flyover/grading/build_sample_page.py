#!/usr/bin/env python3
"""Write ../../valley-flyover.html (the viewer's sample page) from rubric_carbon.json.

Run from anywhere after re-grading:  python3 valley-flyover/grading/build_sample_page.py
"""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
d = json.load(open(os.path.join(HERE, '..', 'rubric_carbon.json')))
esc = html.escape
ICON_BOOK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 7v14"/><path d="M16 12h2"/><path d="M16 8h2"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/><path d="M6 12h2"/><path d="M6 8h2"/></svg>'
ICON_FILM = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M3 7.5h4"/><path d="M3 12h18"/><path d="M3 16.5h4"/><path d="M17 3v18"/><path d="M17 7.5h4"/><path d="M17 16.5h4"/></svg>'
groups = []
for r in d['rubric']:
    if not groups or groups[-1][0] != r['d']: groups.append((r['d'], []))
    groups[-1][1].append(r)
word = {True: ('Pass', 'yes'), False: ('Fail', 'no'), None: ('Unverified', 'unv')}
secs = []
for name, rows in groups:
    npass = sum(r['m'] is True for r in rows); gate = any(r['n'].startswith('G') for r in rows)
    tally = f'{npass} of {len(rows)} passed'
    items = ''.join(
        f'<details class="acc"><summary><span class="n">{esc(r["n"])}</span><span class="p">{esc(r["c"])}</span>'
        f'<span class="t {word[r["m"]][1]}">{word[r["m"]][0]}</span></summary>'
        f'<div class="body"><div class="k">Gemini 4 Carbon</div><p class="txt reply">{esc(r["mc"])}</p></div></details>' for r in rows)
    tag = '<span class="tag">Gate</span>' if gate else ''
    secs.append(f'<details class="sec"><summary><h2>{esc(name)}</h2>{tag}'
                f'<span class="label{" bad" if npass < len(rows) else ""}">{tally}</span></summary><div class="accs">{items}</div></details>')
n = len(d['rubric']); p = sum(r['m'] is True for r in d['rubric']); f = sum(r['m'] is False for r in d['rubric']); u = n - p - f
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
.tally {{ display: flex; flex-wrap: wrap; gap: 6px 18px; font: 400 13px/1.4 var(--mono); color: var(--ink-2); }}
.tally b {{ font-weight: 600; }}
.unv {{ color: #E6B450; }}
.rub details.sec {{ margin-top: 0; }}
.rub details.sec:last-child {{ border-bottom: 1px solid var(--line); }}
.rub details.sec > summary {{ padding: 14px 4px; }}
.rub details.sec > summary .label.bad {{ color: var(--ink); }}
.rub .tag {{ font: 500 10px/1 var(--mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-2); border: 1px solid #3A3A3A; border-radius: 4px; padding: 4px 6px; }}
.rub .accs {{ margin: 0 0 14px 24px; }}
.rub .acc .p {{ white-space: normal; overflow: visible; }}
.rub .acc[open] .p {{ color: var(--ink); }}
.rub .acc .t {{ font-weight: 600; text-transform: uppercase; }}
.rub .acc .t.yes {{ color: #4ADE80; }} .rub .acc .t.no {{ color: #F87171; }} .rub .acc .t.unv {{ color: #E6B450; }}
.rub .acc .body {{ padding-top: 0; }}
.rub .acc .k {{ margin-top: 2px; }}
@media (max-width: 640px) {{ .rub .accs {{ margin-left: 0; }} .rub .acc summary {{ grid-template-columns: 2.4em 1fr auto; }} .rub .acc .t {{ display: inline; }} }}
</style>
</head>
<body>
<nav class="side" aria-label="Pages">
  <a href="index.html">{ICON_BOOK}<span>Overview</span></a>
  <span class="group">Samples</span>
  <a href="sample.html">{ICON_FILM}<span>Dusk Flock</span></a>
  <a href="valley-flyover.html" aria-current="page">{ICON_FILM}<span>Valley Flyover</span></a>
</nav>
<main class="main"><article class="doc wide">
<header class="title-row"><div><h1>Valley Flyover</h1><div class="label">19.3 s &middot; 464 frames &middot; 2 versions</div></div><a class="btn" href="valley-flyover/player.html" target="_blank" rel="noopener">Open full screen</a></header>
<div class="player"><iframe src="valley-flyover/player.html" title="Original video and Human code version, side by side" allow="autoplay"></iframe></div>
<p class="note" style="margin-top:12px">Left: original video. Right: Human code version, a 3D scene drawn live. Space plays or pauses; the arrow keys step one frame, Shift + arrow ten.</p>
<section class="rub">
<h2>Rubric</h2>
<p class="note">{n} criteria written for this clip, scored on the Human code version by Gemini 4 Carbon. Carbon judged a frame-by-frame capture of the page with stills and close-ups; it could not run the page, so the frame-rate gate is unverified. One grading run.</p>
<div class="rub-head"><div class="tally"><span><b class="yes">{p}</b> passed</span><span><b class="no">{f}</b> failed</span><span><b class="unv">{u}</b> unverified</span></div><button class="btn" id="toggle" type="button" aria-expanded="false">Expand all</button></div>
{"".join(secs)}
</section>
</article></main>
<script>
const all = [...document.querySelectorAll('.rub details')], btn = document.getElementById('toggle');
btn.addEventListener('click', () => {{
  const open = btn.getAttribute('aria-expanded') !== 'true';
  all.forEach(el => {{ el.open = open; }});
  btn.setAttribute('aria-expanded', open); btn.textContent = open ? 'Collapse all' : 'Expand all';
}});
</script>
</body>
</html>
'''
open(os.path.join(ROOT, 'valley-flyover.html'), 'w').write(page)
print('wrote valley-flyover.html:', n, 'criteria in', len(groups), 'sections;', p, 'pass,', f, 'fail,', u, 'unverified')
