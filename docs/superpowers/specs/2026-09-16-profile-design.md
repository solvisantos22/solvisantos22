# Profile refresh

The selected direction is clean and personal, with a subtle animated contribution grid.

The README introduces Sölvi through concrete work: Ratatoskur, ELVA video denoising, Réttarvísir, and Romberg integration. It uses short paragraphs, ordinary headings, and direct project links. It avoids generic capability claims, badges, emoji headings, and repeated skill inventories. Education wording does not assume graduation or current enrollment.

An embedded SVG shows the real preceding year of GitHub contributions. One gentle wave moves across the grid and stops in under four seconds. Contributions retain their original levels and dates. The native GitHub calendar is unaffected. Light and dark images match GitHub, and reduced-motion visitors receive a static image. A visible static-image link is also available.

A daily GitHub Action fetches contribution data, validates it, tests the generator, and commits only generated assets when changed. It uses the repository token and pinned checkout action. Failure leaves the previous images intact. A manual trigger provides recovery. No third-party image service or runtime package dependencies are needed.

Verification covers data fidelity, error preservation, accessible SVG metadata, reduced motion, desktop/mobile rendering, and an actual scheduled-workflow implementation run before completion.
