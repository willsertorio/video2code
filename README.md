# video2code

A video rebuilt as code.

`index.html` is a self-contained page that redraws a 19.7-second handheld clip of geese crossing a sunset sky. It has no dependencies and loads nothing from the network: open the file in a browser and it plays in a loop at the clip's own frame rate (29.97 fps, 591 frames).

## How it works

The original clip was measured, and the page re-films those measurements:

- **Sky map**: one stitched picture of the cloud field, built by aligning every frame and taking the median so the birds drop out, plus five correction maps for how the clouds change over the clip.
- **Camera track**: the handheld camera's position, zoom, exposure and colour balance for every frame.
- **Lens shading**: a small map of brightness falloff across the frame.
- **Birds**: the traced outline, opacity and colour of every bird in every frame.

A WebGL shader looks at the sky map through the camera track, and a 2D canvas draws the bird outlines on top.

## Notes

- The sky map is real imagery derived from the source clip; it is not procedurally generated. The source video itself is not in this repository.
- The page draws at up to 1080 px wide (the source was 2160 x 3840).
- Add `?f=<frame>` (0-590) to the address to freeze on a single source frame.
- Measured against the source over all 591 frames at 1080 x 1920: 43.98 dB PSNR on average (worst frame 42.28), SSIM 0.992.
