#!/usr/bin/env python3
"""Grade the Valley Flyover page against its rubric with a model on OpenRouter.

usage: grade.py <rubric.json> <evidence dir> <out.json> [model]
The API key is supplied by the environment's network proxy; set OPENROUTER_API_KEY to use your own.
"""
import base64, json, os, sys, urllib.request, urllib.error, time, re
RUB, EV, OUT = sys.argv[1:4]; MODEL = sys.argv[4] if len(sys.argv) > 4 else "google/gemini-4-carbon"
rub = json.load(open(RUB))
b64 = lambda p: base64.b64encode(open(os.path.join(EV, p), 'rb').read()).decode()
NOTES = open(os.path.join(EV, 'notes.txt')).read()
intro = f"""You are a senior 3D/technical art reviewer grading a submission strictly and independently.

TASK GIVEN TO THE AUTHOR: "{rub['prompt']}"
The author received the reference VIDEO (a {rub['reference']}) and produced a web PAGE that draws the scene live in the browser.

WHAT YOU ARE GIVEN, in this order:
1. The reference VIDEO (downscaled to 960x540).
2. A frame-by-frame capture of the PAGE (one captured frame per source frame, 24 fps, downscaled to 960x540). It shows exactly what the page draws at each frame; it does not show real-time performance.
3. Six stills, each with the VIDEO on the left and the PAGE on the right at the same moment.
4. Four 2x close-ups of difficult areas, VIDEO on the left and PAGE on the right.
5. Technical notes: facts you cannot see in the footage. They were measured by the author, so treat them as claims, weigh them, and say so in your comment where a verdict rests on them.

HOW TO GRADE
- Score every criterion in the rubric below as pass or fail on the PAGE. Judge the PAGE against the VIDEO, not against an ideal scene.
- Be strict. If a criterion is only partly met, fail it and say what is missing. Do not give credit for intent.
- Where the evidence cannot settle a criterion either way, set "m" to null and say what would be needed.
- Each comment is one or two plain sentences naming what you saw (where and when), like a designer's review note.

Return ONLY a JSON array, one object per criterion, in rubric order:
[{{"n": "<criterion id>", "m": true | false | null, "mc": "<comment>"}}, ...]

RUBRIC
{json.dumps(rub['rubric'], indent=1)}

TECHNICAL NOTES
{NOTES}
"""
content = [{"type": "text", "text": intro},
           {"type": "text", "text": "1. Reference VIDEO:"}, {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64('reference.mp4')}},
           {"type": "text", "text": "2. PAGE capture:"}, {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64('page.mp4')}},
           {"type": "text", "text": "3. Stills (VIDEO left, PAGE right):"}]
content += [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64(f'pair{i}.jpg')}} for i in range(6)]
content += [{"type": "text", "text": "4. Close-ups at 2x (VIDEO left, PAGE right):"}]
content += [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64(f'crop{i}.jpg')}} for i in range(4)]
body = {"model": MODEL, "messages": [{"role": "user", "content": content}], "temperature": 0}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                             headers={"Authorization": "Bearer " + os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-supplied-by-proxy"), "Content-Type": "application/json"})
t = time.time()
try:
    resp = json.load(urllib.request.urlopen(req, timeout=600))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode()[:1500]); sys.exit(1)
json.dump(resp, open(OUT.replace('.json', '_response.json'), 'w'), indent=1)
if 'choices' not in resp: print(json.dumps(resp)[:1500]); sys.exit(1)
text = resp['choices'][0]['message']['content']
m = re.search(r'\[.*\]', text, re.S); scores = json.loads(m.group(0))
by = {s['n']: s for s in scores}
out = [dict(r, m=by.get(r['n'], {}).get('m'), mc=by.get(r['n'], {}).get('mc', '(no score returned)')) for r in rub['rubric']]
json.dump(dict(scene=rub['scene'], prompt=rub['prompt'], grader=resp.get('model', MODEL), graded_at=time.strftime('%Y-%m-%d'), rubric=out), open(OUT, 'w'), indent=1)
print('model', resp.get('model'), '| %.0f s |' % (time.time() - t), 'usage', resp.get('usage'))
print('pass %d, fail %d, unverified %d of %d' % (sum(o['m'] is True for o in out), sum(o['m'] is False for o in out), sum(o['m'] is None for o in out), len(out)))
