#!/usr/bin/env python3
"""Generate a quiet contribution-calendar SVG using only the standard library."""

import argparse
from datetime import date, timedelta
from html import escape
import json
from pathlib import Path
import subprocess
import sys


QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}"""
LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")
PALETTES = {
    "light": ("#ebedf0", "#aceebb", "#4ac26b", "#2da44e", "#116329"),
    "dark": ("#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"),
}


def load_calendar(payload):
    """Validate all upstream data before generating or replacing any image."""
    if payload.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; existing images were preserved.")
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    total = calendar["totalContributions"]
    if type(total) is not int or total < 0 or not 1 <= len(weeks) <= 54:
        raise ValueError("Invalid calendar size or total.")
    days, seen = [], set()
    first_sunday = None
    for column, week in enumerate(weeks):
        if not 1 <= len(week["contributionDays"]) <= 7:
            raise ValueError("Invalid number of days in a week.")
        for item in week["contributionDays"]:
            day = date.fromisoformat(item["date"])
            weekday = (day.weekday() + 1) % 7
            if type(item["weekday"]) is not int or item["weekday"] != weekday:
                raise ValueError("Contribution weekday does not match its date.")
            sunday = day - timedelta(days=weekday)
            if first_sunday is None:
                first_sunday = sunday
            if sunday != first_sunday + timedelta(weeks=column) or day in seen:
                raise ValueError("Contribution weeks are out of order or contain duplicate dates.")
            count = item["contributionCount"]
            if type(count) is not int or count < 0:
                raise ValueError("Invalid contribution count.")
            level = LEVELS.index(item["contributionLevel"])
            if (count == 0) != (level == 0):
                raise ValueError("Contribution level does not match its count.")
            seen.add(day)
            days.append((column, weekday, day, count, level))
    if sum(day[3] for day in days) != total:
        raise ValueError("Calendar total does not match the daily counts.")
    return total, days


def color_rules(theme):
    palette = PALETTES[theme]
    text = "#59636e" if theme == "light" else "#9198a1"
    return f"text{{fill:{text}}}" + "".join(f".level-{i}{{fill:{color}}}" for i, color in enumerate(palette))


def render(total, days, theme="light", animated=True):
    first, last = min(d[2] for d in days), max(d[2] for d in days)
    columns = max(d[0] for d in days) + 1
    width = max(828, columns * 15 + 32)
    title = f"{total:,} contributions · {first.isoformat()} to {last.isoformat()}"
    style = color_rules(theme)
    if animated:
        style += """
        .week { animation: wave .8s ease-in-out 1 both; }
        @keyframes wave {
          0%, 100% { transform: translateY(0); }
          45% { transform: translateY(-3px); }
        }
        @media (prefers-reduced-motion: reduce) { .week { animation: none; } }
        """
    else:
        style += "@media (prefers-color-scheme: dark){" + color_rules("dark") + "}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="188" viewBox="0 0 {width} 188" role="img" aria-labelledby="title desc">',
        f"<title id=\"title\">{escape(title)}</title>",
        '<desc id="desc">Each square is one day; darker green in the light theme or brighter green in the dark theme means more contributions. The calendar uses GitHub contribution levels. '
        + ("A single gentle wave settles within 3.4 seconds. " if animated else "This is the still version. ")
        + 'Empty days remain empty.</desc>',
        f"<style>{style}</style>",
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12">',
        f'<text x="16" y="21" font-size="14">{total:,} contributions</text>',
        f'<text x="{width - 16}" y="21" text-anchor="end">{first.strftime("%b %Y")} – {last.strftime("%b %Y")}</text>',
    ]
    labels = []
    for column, _, day, _, _ in days:
        if day == first or day.day == 1:
            if labels and column - labels[-1][0] < 2:
                # A short partial first month should not hide the next full month.
                labels.pop()
            labels.append((column, day.strftime("%b")))
    parts.extend(f'<text x="{16 + column * 15}" y="46">{month}</text>' for column, month in labels)
    for column in range(columns):
        delay = 2.6 * column / max(columns - 1, 1)
        attrs = f' class="week" style="animation-delay:{delay:.3f}s"' if animated else ""
        parts.append(f"<g{attrs}>")
        for col, weekday, day, count, level in days:
            if col != column:
                continue
            parts.append(
                f'<rect x="{16 + col * 15}" y="{57 + weekday * 15}" width="11" height="11" rx="2" '
                f'class="level-{level}" data-date="{day.isoformat()}" data-count="{count}">'
                f'<title>{day.isoformat()}: {count} contribution{"s" if count != 1 else ""}</title></rect>'
            )
        parts.append("</g>")
    parts.append(f'<text x="{width - 150}" y="179">Less</text>')
    for i in range(5):
        parts.append(f'<rect x="{width - 119 + i * 15}" y="169" width="11" height="11" rx="2" class="level-{i}"/>')
    parts.extend([f'<text x="{width - 16}" y="179" text-anchor="end">More</text>', "</g></svg>"])
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="solvisantos22")
    parser.add_argument("--input", type=Path, help="Read a saved GraphQL response instead of making a request.")
    parser.add_argument("--output", type=Path, default=Path("assets"))
    args = parser.parse_args()
    try:
        if args.input:
            payload = json.loads(args.input.read_text(encoding="utf-8"))
        else:
            request = subprocess.run(
                ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={args.user}"],
                capture_output=True, text=True, timeout=60, check=True,
            )
            payload = json.loads(request.stdout)
        total, days = load_calendar(payload)
        images = {
            "contributions.svg": render(total, days),
            "contributions-dark.svg": render(total, days, theme="dark"),
            "contributions-static.svg": render(total, days, animated=False),
        }
        args.output.mkdir(parents=True, exist_ok=True)
        for name, content in images.items():
            temporary = args.output / f".{name}.tmp"
            temporary.write_text(content, encoding="utf-8")
            temporary.replace(args.output / name)
        print(f"Generated {len(images)} images from {len(days)} days and {total:,} contributions.")
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Contribution update failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
