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
VERS = [('m', 'mc', 'Carbon', "Gemini 4 Carbon's version"), ('r', 'rc', 'Human', 'Human version')]
secs = []
for name, rows in groups:
    gate = any(r['n'].startswith('G') for r in rows)
    tally = ' &middot; '.join(f'{lab} {sum(r[k] is True for r in rows)}/{len(rows)}' for k, _, lab, _ in VERS)
    items = ''
    for r in rows:
        marks = ''.join(f'<span class="{word[r[k]][1]}"><i>{lab}</i> {word[r[k]][0]}</span>' for k, _, lab, _ in VERS)
        body = ''.join(f'<div class="k">{esc(full)} &middot; <span class="{word[r[k]][1]}">{word[r[k]][0]}</span></div><p class="txt reply">{esc(r[kc])}</p>' for k, kc, _, full in VERS)
        items += (f'<details class="acc"><summary><span class="n">{esc(r["n"])}</span><span class="p">{esc(r["c"])}</span>'
                  f'<span class="t">{marks}</span></summary><div class="body">{body}</div></details>')
    tag = '<span class="tag">Gate</span>' if gate else ''
    secs.append(f'<details class="sec"><summary><h2>{esc(name)}</h2>{tag}<span class="label">{tally}</span></summary><div class="accs">{items}</div></details>')
n = len(d['rubric'])
cnt = {k: (sum(r[k] is True for r in d['rubric']), sum(r[k] is False for r in d['rubric']), sum(r[k] is None for r in d['rubric'])) for k, _, _, _ in VERS}
tally_rows = ''.join(f'<tr><td>{esc(full)}</td><td class="mono yes">{cnt[k][0]}</td><td class="mono no">{cnt[k][1]}</td><td class="mono unv">{cnt[k][2]}</td></tr>' for k, _, _, full in VERS)
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
.tally {{ max-width: 460px; flex: 1 1 320px; }}
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
  <a href="sample.html">{ICON_FILM}<span>Dusk Flock</span></a>
  <a href="valley-flyover.html" aria-current="page">{ICON_FILM}<span>Valley Flyover</span></a>
</nav>
<main class="main"><article class="doc wide">
<header class="title-row"><div><h1>Valley Flyover</h1><div class="label">19.3 s &middot; 464 frames &middot; 3 versions</div></div><a class="btn" href="valley-flyover/player.html" target="_blank" rel="noopener">Open full screen</a></header>
<div class="player"><iframe src="valley-flyover/player.html" title="Original video, Gemini 4 Carbon version and Human version, side by side" allow="autoplay"></iframe></div>
<p class="note" style="margin-top:12px">Left to right: the original video, Gemini 4 Carbon's version (one prompt, 35 KB, a landscape generated by a shader) and the Human version (a 3D scene rebuilt from the footage, 28 MB). All three are locked to the same frame. Space plays or pauses; the arrow keys step one frame, Shift + arrow ten. Carbon's version runs 18.5 s, so it holds its last frame for the final 20 frames.</p>
<div class="prompt"><div><div class="label">Prompt sent to Gemini 4 Carbon, with the video</div><p>{esc(d["prompt"])}</p></div></div>
<section class="rub">
<h2>Rubric</h2>
<p class="note">{n} criteria written for this clip, scored on both code versions by Gemini 4 Carbon, which is also the author of one of them. For each version it was sent a capture of the page, six paired stills, four close-ups and short technical notes; it could not run the pages, so the frame-rate gate is unverified. One grading run per version.</p>
<div class="rub-head"><div class="tally table-wrap"><table class="rubric plain"><thead><tr><th>Version</th><th class="num">Passed</th><th class="num">Failed</th><th class="num">Unverified</th></tr></thead><tbody>{tally_rows}</tbody></table></div><button class="btn" id="toggle" type="button" aria-expanded="false">Expand all</button></div>
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
print('wrote valley-flyover.html:', n, 'criteria in', len(groups), 'sections; pass/fail/unverified', cnt)
