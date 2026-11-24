#!/usr/bin/env python3
"""Write ../player.html: original video, Gemini 4 Carbon's page and the Human code version, locked to one frame.

usage: build_player.py <player shell.html>   (the shell is player_shell.html in this folder)
"""
import sys, base64, os, re
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(sys.argv[1]).read()
rep = [
('<title>__TITLE__</title>', '<title>Valley Flyover: original, Gemini 4 Carbon and human</title>'),
("  /* layout: two frames filling the space above one transport bar; side by side when wide, stacked when tall */", "  /* layout: three frames filling the space above one transport bar; side by side when wide, stacked when tall */"),
("  .frame video,.frame canvas{position:absolute;inset:0;width:100%;height:100%;display:block}", "  .frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block;background:var(--panel)}\n  .frame video,.frame canvas{position:absolute;inset:0;width:100%;height:100%;display:block}"),
('  <figure><figcaption><b>Code version</b></figcaption>', '  <figure><figcaption><b>Gemini 4 Carbon</b></figcaption>\n    <div class="frame"><iframe id="carbon" title="Gemini 4 Carbon version" tabindex="-1"></iframe></div></figure>\n  <figure><figcaption><b>Human</b></figcaption>'),
('The original video could not be loaded here. The code version still plays.', 'The original video could not be loaded here. The code versions still play.'),
('<script>\n__CORE__\n', '<script src="scene.js"></script>\n<script>\n'),
]
for a, b in rep:
    assert s.count(a) == 1, a; s = s.replace(a, b)
s = s.replace('__NF1__', '463')
i = s.index("function resize() {"); j = s.index("// ---- transport:")
s = s[:i] + '''function resize() {
  // landscape footage: put the frames side by side when the window is wide, stack them when it is tall
  const n = frames.length, cap = frames[0].previousElementSibling.offsetHeight + 6, vw = views.clientWidth, vh = views.clientHeight, ar = FW / FH;
  const sideW = Math.min((vw - 12 * (n - 1)) / n, (vh - cap) * ar), stackW = Math.min(vw, ((vh - 12 * (n - 1)) / n - cap) * ar);
  const stacked = stackW > sideW, w = Math.max(120, stacked ? stackW : sideW), h = w / ar;
  views.style.flexDirection = stacked ? 'column' : 'row';
  for (const f of frames) { f.style.width = w + 'px'; f.style.height = h + 'px'; }
  setCanvasSize(w, h);
}
// Gemini 4 Carbon's answer to "transform this video into code, be the more realistic as you can"
// (OpenRouter, google/gemini-4-carbon), unchanged. Its own play bar is hidden and this player moves its scrub bar.
const CARBON_B64 = "__CARBON__", CARBON_SECONDS = 18.5;
const carbon = document.getElementById('carbon');
carbon.addEventListener('load', () => {
  try { const st = carbon.contentDocument.createElement('style'); st.textContent = '#hud{display:none!important}'; carbon.contentDocument.head.appendChild(st); setCarbon(curF); } catch (e) {}
});
carbon.srcdoc = new TextDecoder().decode(Uint8Array.from(atob(CARBON_B64), c => c.charCodeAt(0)));
function setCarbon(f) {                   // Carbon's clip runs 18.5 s, so it holds its last frame for the final 20 frames
  try { const sc = carbon.contentDocument.getElementById('scrubber'); if (!sc) return; sc.value = Math.min(f / FPS, CARBON_SECONDS); sc.dispatchEvent(new Event('input')); } catch (e) {}
}
''' + s[j:]
a = "  draw(f); seek.value = f;"
assert s.count(a) == 1; s = s.replace(a, "  draw(f); setCarbon(f); seek.value = f;")
s = s.replace('__CARBON__', base64.b64encode(open(os.path.join(D, 'carbon.html'), 'rb').read()).decode())
i = s.index('</style>\n') + len('</style>\n'); hd, body = s[:i], s[i:]
hd = hd.replace('  html,body{height:100%}', '  html,body{height:100%}\n  [hidden]{display:none!important}')
doc = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + hd + '</head>\n<body>\n' + body + '</body>\n</html>\n'
assert not re.findall(r'__[A-Z0-9]+__', doc)
open(os.path.join(D, 'player.html'), 'w').write(doc); print('player.html', len(doc), 'bytes')
