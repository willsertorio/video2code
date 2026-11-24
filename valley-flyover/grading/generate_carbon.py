#!/usr/bin/env python3
"""Ask a model on OpenRouter to turn the clip into code, in one call with no follow-up.

usage: generate_carbon.py <input.mp4> <out dir> [model]
Writes carbon.html (the answer's HTML, unchanged) and carbon_response.json (the raw reply).
The API key is supplied by the environment's network proxy; set OPENROUTER_API_KEY to use your own.
"""
import base64, json, os, re, sys, time, urllib.request, urllib.error
VIDEO, OUT = sys.argv[1:3]; MODEL = sys.argv[3] if len(sys.argv) > 3 else "google/gemini-4-carbon"
PROMPT = "transform this video into code, be the more realistic as you can"
def extract_html(text):
    fences = re.findall(r"```(?:html|HTML)?\s*\n(.*?)```", text, re.S)
    cands = [f for f in fences if "<html" in f.lower() or "<!doctype" in f.lower()]
    if cands: return max(cands, key=len).strip() + "\n"
    m = re.search(r"(<!DOCTYPE html.*?</html>)", text, re.S | re.I) or re.search(r"(<html.*?</html>)", text, re.S | re.I)
    return m.group(1).strip() + "\n" if m else None
body = {"model": MODEL, "messages": [{"role": "user", "content": [
    {"type": "text", "text": PROMPT},
    {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + base64.b64encode(open(VIDEO, 'rb').read()).decode()}}]}]}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                             headers={"Authorization": "Bearer " + os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-supplied-by-proxy"), "Content-Type": "application/json"})
t = time.time()
try: resp = json.load(urllib.request.urlopen(req, timeout=1200))
except urllib.error.HTTPError as e: print('HTTP', e.code, e.read().decode()[:1500]); sys.exit(1)
json.dump(resp, open(os.path.join(OUT, 'carbon_response.json'), 'w'), indent=1)
if 'choices' not in resp: print(json.dumps(resp)[:1500]); sys.exit(1)
ch = resp['choices'][0]; text = ch['message']['content'] or ''
html = extract_html(text)
print('model', resp.get('model'), '| %.0f s | finish' % (time.time() - t), ch.get('finish_reason'), '| usage', {k: resp.get('usage', {}).get(k) for k in ('prompt_tokens', 'completion_tokens', 'cost')})
if not html: print('no HTML document found in the reply; first 600 chars:', text[:600]); sys.exit(1)
open(os.path.join(OUT, 'carbon.html'), 'w').write(html); print('carbon.html', len(html), 'bytes; reply text outside the HTML:', len(text) - len(html), 'chars')
