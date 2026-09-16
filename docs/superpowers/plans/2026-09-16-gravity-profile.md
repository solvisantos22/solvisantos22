# Gravity Profile Revision Implementation Plan

**Goal:** Expand the project descriptions in plain language and replace the wave with a gravity animation.

**Architecture:** Preserve the existing README, Python SVG generator and GitHub Actions refresh. Change project prose and the generator's visual sequence, with no new runtime dependencies.

- [x] Expand README project descriptions from verified public sources, remove em dashes and retain the image selection and contact links.
- [x] Add meaningful regression coverage for stationary empty days, exact active-day identity, sparse and dense calendars, reduced motion and motion bounds.
- [x] Generate deterministic tumbling and return paths in scripts/generate_contributions.py, ending within five seconds on the original grid.
- [x] Render real images and inspect the start, fall, pile and final frame in both themes, including mobile and reduced motion.
- [ ] Review the final changes, update the maintenance notes, and publish without rewriting remote history.
- [ ] Verify the live GitHub profile and successful refresh workflow, then record the results.
