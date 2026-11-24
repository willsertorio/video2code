# Valley Flyover

A 19.3-second drone clip over forested hills (1920 x 1080, 24 fps, 464 frames), rebuilt as a 3D scene that is drawn live in the browser.

- `human.html`: the code version on its own. Add `?f=<frame>` (0-463) to freeze on one source frame.
- `player.html`: the original clip beside the code version, locked to the same frame. Play or pause with the button or Space; step with the arrow keys; Shift + arrows jumps ten frames.
- `scene.js`: the measured scene and the renderer, shared by both pages (about 28 MB).
- `ref.mp4`: a 1280 x 720 copy of the source clip, used only by the player.

Both pages open straight from disk and load nothing from the network.

## How it works

The clip is a camera flying forward through a scene where nothing else moves, so the whole clip can be described as a fixed 3D scene plus a camera path:

- **Keyframes**: 78 stills taken from the footage, one every 6 frames, each with a depth grid (483 x 273 points) recovered from how the picture shifts between neighbouring views.
- **Camera path**: the drone's position and direction for all 464 frames, plus the lens's focal length and distortion.
- **Wobble correction**: a 32 x 18 grid of sub-pixel shifts per frame, for motion in the source that a rigid camera cannot follow.
- **Sharpening**: one amount per frame, so keyframes and the frames between them carry the same fine detail.

Each keyframe becomes a textured 3D surface. For every frame, WebGL draws the nearest surfaces through the recovered camera; where something in front has moved aside, the stretched part of a surface is cut away and a neighbouring keyframe shows through. One frame in six is a stored still seen from its own position; the other five are drawn from the geometry.

Measured against the source over all 464 frames at 1920 x 1080: 39.5 dB PSNR on average (worst frame 37.1), SSIM 0.978, colour bias under 0.2 levels.

Known differences: between keyframes, mostly in the last 5 seconds at the lower right, the outline of near trees against bright roofs shows small specks and jagged fragments, and near foliage is slightly softer than on keyframes. Frame rate on a real GPU has not been measured.

## Rubric and scores

- `rubric.json`: 40 criteria written for this clip (3 gates and 37 scored), following the framework's dimensions: Builds, Playback, Prompt adherence, Reference fidelity, Scene fidelity, Composition, Lighting, Materials, Motion, Realism, Camera path, Viewpoint consistency and Motion timing. The Orbit gate is left out. The prompt is assumed to be "transform this video into a photorealistic 3D scene".
- `rubric_carbon.json`: the same criteria scored on the code version by `google/gemini-4-carbon` through OpenRouter: 34 pass, 5 fail, 1 unverified (the 30 fps gate).
- `grading/`: what the grader was sent (`reference.mp4`, `page.mp4`, six paired stills, four close-ups, `notes.txt`), the script that sent it (`grade.py`) and the raw reply.

The grader could not run the page. It judged a frame-by-frame capture and stills, and took the build, playback and frame-rate facts from `notes.txt`, which also told it the known weaknesses. It was a single run.

To grade again from this folder:

```bash
export OPENROUTER_API_KEY=...        # your key, never committed
python3 grading/grade.py rubric.json grading rubric_carbon.json
```
