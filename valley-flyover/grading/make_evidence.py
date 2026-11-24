#!/usr/bin/env python3
"""Build what the grader is sent for one version: page.mp4, six paired stills and four 2x close-ups.

usage: make_evidence.py <reference frames %05d.png, first file = 1> <page frames dir, files = <frame>.png> <out dir> [fps of the page frames] [stills dir]
Stills use frames 0, 116, 232, 348, 418, 463 and close-ups frames 418, 459, 250, 124, read from the stills dir (default: the page frames dir).
Every picture is resized to 960x540, whatever size it was captured at.
"""
import sys, os, glob, subprocess, cv2, numpy as np
REF, PAGE, OUT = sys.argv[1:4]; FPS = sys.argv[4] if len(sys.argv) > 4 else '24'; STILLS = sys.argv[5] if len(sys.argv) > 5 else PAGE
os.makedirs(OUT, exist_ok=True)
rd = lambda p: cv2.resize(cv2.imread(p), (960, 540), interpolation=cv2.INTER_AREA if cv2.imread(p).shape[1] > 960 else cv2.INTER_CUBIC)
ref = lambda f: rd(REF % (f + 1)); page = lambda f: rd(os.path.join(STILLS, '%05d.png' % f))
for i, f in enumerate([0, 116, 232, 348, 418, 463]):
    cv2.imwrite(os.path.join(OUT, 'pair%d.jpg' % i), np.hstack([ref(f), page(f)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
# close-ups: a 480x270 region of the 960x540 picture, shown at 2x
for i, (f, x, y) in enumerate([(418, 480, 270), (459, 480, 270), (250, 240, 270), (124, 480, 270)]):
    z = lambda im: cv2.resize(im[y:y + 270, x:x + 480], (960, 540), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(OUT, 'crop%d.jpg' % i), np.hstack([z(ref(f)), z(page(f))]), [cv2.IMWRITE_JPEG_QUALITY, 90])
frames = sorted(glob.glob(os.path.join(PAGE, '*.png')))
lst = os.path.join(OUT, 'frames.txt'); open(lst, 'w').write(''.join("file '%s'\nduration %f\n" % (os.path.abspath(p), 1 / float(FPS)) for p in frames))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', 'scale=960:540:flags=bicubic,fps=24', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-an', os.path.join(OUT, 'page.mp4')], check=True)
os.remove(lst); print(OUT, len(frames), 'page frames at', FPS, 'fps')
