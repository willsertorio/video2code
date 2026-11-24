# video2code

A video rebuilt as code.

`human.html` is a self-contained page that redraws a 19.7-second handheld clip of geese crossing a sunset sky. It has no dependencies and loads nothing from the network: open the file in a browser and it plays in a loop at the clip's own frame rate (29.97 fps, 591 frames).

## Viewer

`index.html` is the Overview: what the comparison is and how each of the three versions was made. `sample.html` shows the side-by-side player inside the viewer. Both use `css/docs.css` and the Geist fonts in `fonts/` (licences in `licenses.csv`).

## Side-by-side player

`player.html` shows three panels locked to the same frame: the original clip, Gemini 4 Carbon's version, and the human-made code version. It is a single self-contained file and embeds a 720 x 1280 copy of the source clip for the comparison.

The middle panel is `carbon.html`, the answer `google/gemini-4-carbon` (through OpenRouter) gave when sent the 720 x 1280 clip with the prompt "transform this video into code, be the more realistic as you can". The player hides Carbon's own play bar and drives its clock; its drawing code is unchanged. Carbon's animation runs 19.6 s, so it holds its last frame for the clip's final few frames.

- Play or pause: the button, or Space.
- Step one frame: the -1 and +1 buttons, or the Left and Right arrow keys.
- Jump ten frames: the -10 and +10 buttons, or Shift + Left / Right.
- Scrub: drag the bar to any of the 591 frames.
- Speed: 0.25x, 0.5x or 1x.

## How it works

The original clip was measured, and the page re-films those measurements:

- **Sky map**: one stitched picture of the cloud field, built by aligning every frame and taking the median so the birds drop out, plus five correction maps for how the clouds change over the clip.
- **Camera track**: the handheld camera's position, zoom, exposure and colour balance for every frame.
- **Lens shading**: a small map of brightness falloff across the frame.
- **Birds**: the traced outline, opacity and colour of every bird in every frame.

A WebGL shader looks at the sky map through the camera track, and a 2D canvas draws the bird outlines on top.

## Notes

- The sky map is real imagery derived from the source clip; it is not procedurally generated. `human.html` does not contain the source video; `player.html` embeds a reduced copy of it.
- The page draws at up to 1080 px wide (the source was 2160 x 3840).
- Add `?f=<frame>` (0-590) to the address to freeze on a single source frame.
- Measured against the source over all 591 frames at 1080 x 1920: 43.98 dB PSNR on average (worst frame 42.28), SSIM 0.992.
