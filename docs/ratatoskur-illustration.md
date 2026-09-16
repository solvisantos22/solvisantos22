# Ratatoskur profile illustration

The profile contains an 18-second SVG loop with five stages: write the equation, ask for a hint, continue the working, confirm an uncertain reading, and check the solution. The content comes from the existing [website lesson](https://github.com/solvisantos22/ratatoskur-website/blob/main/src/components/simulator/demo-content.ts) and [reading-confirmation fixture](https://github.com/solvisantos22/ratatoskur_ios/blob/main/api_contract_examples/query_confirm_reading.json).

This is a scripted illustration, not a screen recording, a live AI response or a measured recognition result. The equation is `2x + 3 = 11`, and its solution is `x = 4`. The question mark illustrates uncertainty about the symbol 3; the reading is confirmed before checking the solution.

The open details section can be collapsed to hide motion. The picture element selects a still image for reduced motion and an appropriate light or dark animation. Animated assets also handle reduced motion internally. The still asset adapts its palette to the preferred color scheme.

Regenerate with `python3 scripts/generate_ratatoskur.py`. All assets are local to the profile repository and require no external image service.

## ELVA figure

`assets/elva-denoising.png` is the original embedded Figure 7 from page 12 of [the ELVA report](https://github.com/solvisantos22/ElvaReport/blob/main/Lokaverkefni_ELVA%20(1).pdf), extracted unchanged. Its three panels are Noisy, Pretrained and Fine-tuned. The figure is qualitative; no clean reference frame was available. The profile does not claim that fine-tuning improved quality or reproduce unaudited metric rankings.
