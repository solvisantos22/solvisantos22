# Gravity Profile Revision Implementation Plan

**Goal:** Expand the project descriptions in plain language and replace the wave with a gravity animation.

**Architecture:** Preserve the existing README, Python SVG generator and GitHub Actions refresh. Change project prose and the generator's visual sequence, with no new runtime dependencies.

- [x] Expand README project descriptions from verified public sources, remove em dashes and retain the image selection and contact links.
- [x] Add meaningful regression coverage for stationary empty days, exact active-day identity, sparse and dense calendars, reduced motion and motion bounds.
- [x] Generate deterministic tumbling and return paths in scripts/generate_contributions.py, ending within five seconds on the original grid.
- [x] Render real images and inspect the start, fall, pile and final frame in both themes, including mobile and reduced motion.
- [x] Review the final changes, update the maintenance notes, and publish without rewriting remote history.
- [x] Verify the live GitHub profile and successful refresh workflow, then record the results.

## Verification

Six tests passed locally and in [the GitHub Actions refresh](https://github.com/solvisantos22/solvisantos22/actions/runs/35105245812). Independent review found no important issues. Browser checks sampled the animation every 80 milliseconds in both themes: empty cells stayed still, contribution metadata was unchanged, moving cells stayed within the drawing area, and every tile returned to its original position by 4.8 seconds.

Desktop and mobile layout checks passed. Reduced motion selected the still image and disabled motion inside the animated SVG. The live GitHub profile loaded all three image variants, its public image served the new gravity keyframes, and the published README contained the expanded prose without em dashes.
