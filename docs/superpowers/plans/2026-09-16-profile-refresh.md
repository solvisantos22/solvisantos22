# Profile Refresh Implementation Plan

**Goal:** Publish the selected clean, personal GitHub profile and a subtle contribution animation.

**Architecture:** Keep profile prose in README.md. A Python standard-library generator turns GitHub GraphQL calendar data into checked-in SVGs; an Actions workflow refreshes only those images daily.

**Tech stack:** Markdown, SVG/CSS, Python, GitHub CLI, GitHub Actions.

- [x] Rewrite README.md around four verified projects and preserve the contact links. Use a picture element for reduced-motion, dark, and default SVGs.
- [x] Add tests/test_contributions.py. Exercise the generator through its CLI with small calendar fixtures; check exact day counts, month alignment, theme variants, animation duration, and preservation of existing images on upstream errors or malformed data.
- [x] Run `python3 -m unittest discover -s tests -v` and confirm the new generator tests fail before implementation.
- [x] Implement scripts/generate_contributions.py with `--input` for offline fixtures, `--output` for assets, and `--user` for live data. Validate the entire response before touching output files; emit accessible image titles and per-day metadata.
- [x] Add .github/workflows/contributions.yml with a daily schedule, manual trigger, relevant main-branch push trigger, pinned checkout, tests, live generation, and a narrow assets-only commit.
- [x] Generate the real assets and run the tests. Preview both themes and motion preferences, including mobile widths.
- [x] Obtain an independent review, resolve actionable issues, check the remote has not changed, and publish the verified update.
- [x] Run the actual GitHub Action and inspect the rendered GitHub profile and its image sources.

## Verification

All four generator tests passed locally and in [the first GitHub Actions run](https://github.com/solvisantos22/solvisantos22/actions/runs/35103678850). The repository token successfully generated all three images from 368 calendar days and 660 contributions.

Browser checks passed at desktop and mobile widths with no horizontal overflow. The animation settles after 3.4 seconds and stops entirely under reduced motion. The published GitHub profile was checked directly: light, dark, and reduced-motion preferences each load the corresponding image successfully. The grid sits below the introduction so the initial wave is visible before scrolling through project descriptions.
