#!/usr/bin/env python3
"""Grade the Valley Flyover page against its rubric with a model on OpenRouter.

usage: grade.py <rubric.json> <evidence dir> <out.json> <m|r> [model]
m scores Gemini 4 Carbon's version (fields m, mc), r scores the Human version (fields r, rc); both go into the same out.json.
The evidence dir holds one version's page.mp4, pair0-5.jpg, crop0-3.jpg and notes.txt; reference.mp4 sits beside this script.
The API key is supplied by the environment's network proxy; set OPENROUTER_API_KEY to use your own.
"""
import base64, json, os, sys, urllib.request, urllib.error, time, re
RUB, EV, OUT, KEY = sys.argv[1:5]; MODEL = sys.argv[5] if len(sys.argv) > 5 else "google/gemini-4-carbon"
assert KEY in ('m', 'r')
rub = json.load(open(RUB))
HERE = os.path.dirname(os.path.abspath(__file__))
b64 = lambda p, d=None: base64.b64encode(open(os.path.join(d or EV, p), 'rb').read()).decode()
NOTES = open(os.path.join(EV, 'notes.txt')).read()
intro = f"""You are a senior 3D/technical art reviewer grading a submission strictly and independently.

TASK GIVEN TO THE AUTHOR: "{rub['prompt']}"
The author received the reference VIDEO (a {rub['reference']}) and produced a web PAGE that draws the scene live in the browser.

WHAT YOU ARE GIVEN, in this order:
1. The reference VIDEO (downscaled to 960x540).
2. A capture of the PAGE made by stepping it to the time of each source frame and taking a screenshot, shown at 960x540 and video speed (the technical notes say how many frames were captured and at what size). It shows what the page draws at each moment; it does not show real-time performance.
3. Six stills, each with the VIDEO on the left and the PAGE on the right at the same moment.
4. Four 2x close-ups of difficult areas, VIDEO on the left and PAGE on the right.
5. Technical notes: facts you cannot see in the footage, recorded by the person running this review. Say so in your comment where a verdict rests on them.

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
           {"type": "text", "text": "1. Reference VIDEO:"}, {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64('reference.mp4', HERE)}},
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
json.dump(resp, open(os.path.join(EV, 'response.json'), 'w'), indent=1)
if 'choices' not in resp: print(json.dumps(resp)[:1500]); sys.exit(1)
text = resp['choices'][0]['message']['content']
m = re.search(r'\[.*\]', text, re.S); scores = json.loads(m.group(0))
by = {s['n']: s for s in scores}
old = {o['n']: o for o in json.load(open(OUT))['rubric']} if os.path.exists(OUT) else {}
out = []
for r in rub['rubric']:
    o = dict(r); o.update({k: v for k, v in old.get(r['n'], {}).items() if k in ('m', 'mc', 'r', 'rc')})
    o[KEY] = by.get(r['n'], {}).get('m'); o[KEY + 'c'] = by.get(r['n'], {}).get('mc', '(no score returned)'); out.append(o)
json.dump(dict(scene=rub['scene'], prompt=rub['prompt'], grader=resp.get('model', MODEL), graded_at=time.strftime('%Y-%m-%d'), rubric=out), open(OUT, 'w'), indent=1)
print('model', resp.get('model'), '| %.0f s |' % (time.time() - t), 'usage', resp.get('usage'))
print('pass %d, fail %d, unverified %d of %d' % (sum(o[KEY] is True for o in out), sum(o[KEY] is False for o in out), sum(o[KEY] is None for o in out), len(out)))
