# Contribution calendar

The profile embeds an image generated from GitHub's contribution calendar API. It does not modify the native contribution calendar or invent activity. Active squares tumble into a pile, pause, and return to their original positions in one 4.8-second sequence. Empty days stay in place. The movement is decorative; dates, counts and contribution levels do not change. Reduced-motion visitors get a static image, also available through the profile's still-image link.

The workflow refreshes images daily at 09:23 UTC and can be run manually from **Actions → Refresh contribution calendar → Run workflow**. GitHub can delay schedules, and it can disable scheduled workflows in public repositories after 60 days of inactivity. If necessary, re-enable the workflow in Actions and run it manually. Existing images remain available when a refresh fails.

The workflow uses its repository-scoped GitHub token. It renders the contribution data visible to that token, which can differ from the calendar seen by an authenticated account owner. No personal access token or external rendering service is required.

For a local refresh, authenticate the GitHub CLI and run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/generate_contributions.py --user solvisantos22
```

Local generation uses the current CLI account's visibility. The automated refresh is the authoritative public profile image. Use `--input saved-response.json --output preview-assets` to preview an offline GraphQL response without making a request.
