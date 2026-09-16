import json
import importlib.util
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate_contributions.py"
NS = {"svg": "http://www.w3.org/2000/svg"}
SPEC = importlib.util.spec_from_file_location("generate_contributions", SCRIPT)
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def motion_frames(root):
    """Read generated paths so geometry is checked independently of the layout code."""
    style = root.find("svg:style", NS).text
    paths = {}
    for name, body in re.findall(r"@keyframes\s+(gravity-\d+)\s*\{(.*?)\n\s*\}", style, re.S):
        paths[name] = [tuple(map(float, frame)) for frame in re.findall(
            r"([\d.]+)%\s*\{\s*transform:\s*translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*rotate\(([-\d.]+)deg\)",
            body,
        )]
    return paths


def dense_days(active_count):
    start = date(2025, 9, 7)
    return [(index // 7, index % 7, start + timedelta(days=index),
             1 if index < active_count else 0, 1 if index < active_count else 0)
            for index in range(378)]


def response():
    return {"data": {"user": {"contributionsCollection": {"contributionCalendar": {
        "totalContributions": 8,
        "weeks": [
            {"contributionDays": [
                {"date": "2026-08-30", "weekday": 0, "contributionCount": 0, "contributionLevel": "NONE"},
                {"date": "2026-08-31", "weekday": 1, "contributionCount": 3, "contributionLevel": "SECOND_QUARTILE"},
                {"date": "2026-09-01", "weekday": 2, "contributionCount": 5, "contributionLevel": "FOURTH_QUARTILE"},
            ]},
            {"contributionDays": [
                {"date": "2026-09-06", "weekday": 0, "contributionCount": 0, "contributionLevel": "NONE"},
            ]},
        ],
    }}}}}


class ContributionImagesTests(unittest.TestCase):
    def run_generator(self, payload, directory):
        source = Path(directory) / "calendar.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(Path(directory) / "assets")],
            capture_output=True, text=True,
        )

    def test_preserves_actual_days_counts_and_week_alignment(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_generator(response(), directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            root = ET.parse(Path(directory) / "assets/contributions.svg").getroot()
            cells = root.findall(".//svg:rect[@data-date]", NS)
            self.assertEqual(len(cells), 4)
            by_date = {cell.attrib["data-date"]: cell for cell in cells}
            self.assertEqual(by_date["2026-09-01"].attrib["data-count"], "5")
            self.assertEqual(by_date["2026-08-30"].attrib["x"], by_date["2026-09-01"].attrib["x"])
            self.assertGreater(float(by_date["2026-09-06"].attrib["x"]), float(by_date["2026-08-30"].attrib["x"]))
            self.assertGreater(float(by_date["2026-09-01"].attrib["y"]), float(by_date["2026-08-30"].attrib["y"]))
            self.assertIn("8 contributions", root.find("svg:title", NS).text)
            self.assertIsNotNone(root.find("svg:desc", NS))
            month_labels = [node.text for node in root.findall(".//svg:text[@y='46']", NS)]
            self.assertIn("Sep", month_labels)

    def test_supplies_theme_variants_and_a_truly_static_alternative(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_generator(response(), directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            assets = Path(directory) / "assets"
            light = (assets / "contributions.svg").read_text()
            dark = (assets / "contributions-dark.svg").read_text()
            static = (assets / "contributions-static.svg").read_text()
            self.assertNotEqual(light, dark)
            self.assertIn("prefers-reduced-motion: reduce", light)
            self.assertIn("prefers-reduced-motion: reduce", dark)
            self.assertNotIn("infinite", light)
            self.assertNotIn("@keyframes", static)
            self.assertNotIn("animation:", static)
            self.assertIn("prefers-color-scheme: dark", static)

    def test_only_active_days_move_and_each_returns_to_its_true_cell(self):
        total, days = GENERATOR.load_calendar(response())
        root = ET.fromstring(GENERATOR.render(total, days))
        moving = root.findall(".//svg:g[@class='falling-cell']", NS)
        self.assertEqual(len(moving), 2, "Every active day should tumble independently.")
        paths = motion_frames(root)
        self.assertEqual(len(paths), len(moving))
        cells = root.findall(".//svg:rect[@data-date]", NS)
        self.assertEqual(len(cells), len(days), "The scaffold must not duplicate contribution metadata.")
        cells_by_date = {cell.attrib["data-date"]: cell for cell in cells}
        self.assertEqual(len(cells_by_date), len(days))
        for column, weekday, day, count, level in days:
            cell = cells_by_date[day.isoformat()]
            self.assertEqual(cell.attrib["data-count"], str(count))
            self.assertIn(f"level-{level}", cell.attrib["class"].split())
            self.assertEqual(float(cell.attrib["x"]), 16 + column * 15)
            self.assertEqual(float(cell.attrib["y"]), 57 + weekday * 15)
        for wrapper in moving:
            cell = wrapper.find("svg:rect[@data-date]", NS)
            self.assertGreater(int(cell.attrib["data-count"]), 0)
            name = re.search(r"animation-name:\s*(gravity-\d+)", wrapper.attrib["style"]).group(1)
            frames = paths[name]
            self.assertEqual(frames[0], (0, 0, 0, 0))
            self.assertEqual(frames[-1], (100, 0, 0, 0))
            self.assertGreater(max(frame[2] for frame in frames), 80)
            self.assertGreater(max(abs(frame[3]) for frame in frames), 300)
            settled = [frame for frame in frames if 50 <= frame[0] <= 67]
            self.assertGreaterEqual(settled[-1][0] - settled[0][0], 10,
                                    "The completed pile needs a visible pause before reconstruction.")
            self.assertTrue(all(frame[1:] == settled[0][1:] for frame in settled))
            falling = [frame for frame in frames if frame[0] < 50]
            self.assertTrue(any(right[2] < left[2] for left, right in zip(falling, falling[1:])),
                            "A falling square should visibly bounce on impact.")
        style = root.find("svg:style", NS).text
        self.assertRegex(style, r"animation-duration:\s*4\.8s")
        self.assertRegex(style, r"animation-iteration-count:\s*1[;\s]")
        self.assertRegex(style, r"animation-fill-mode:\s*both")
        self.assertRegex(style, r"transform-origin:\s*center")
        self.assertNotIn(".week", style)
        reduced_motion = style.split("@media (prefers-reduced-motion: reduce)")[1]
        self.assertIn(".falling-cell", reduced_motion)
        self.assertIn("animation: none", reduced_motion)

    def test_sparse_and_dense_piles_fit_the_canvas_and_preserve_every_day(self):
        for active_count in (0, 1, 86, 378):
            with self.subTest(active_count=active_count):
                days = dense_days(active_count)
                svg = GENERATOR.render(active_count, days)
                self.assertEqual(svg, GENERATOR.render(active_count, days), "Motion must be deterministic.")
                root = ET.fromstring(svg)
                self.assertLessEqual(float(root.attrib["height"]), 280)
                self.assertEqual(len(root.findall(".//svg:rect[@data-date]", NS)), 378)
                moving = root.findall(".//svg:g[@class='falling-cell']", NS)
                self.assertEqual(len(moving), active_count)
                paths = motion_frames(root)
                self.assertEqual(len(paths), active_count)
                width = float(root.attrib["width"])
                positions = set()
                radius = 11 / math.sqrt(2)
                for wrapper in moving:
                    cell = wrapper.find("svg:rect", NS)
                    center_x = float(cell.attrib["x"]) + 5.5
                    center_y = float(cell.attrib["y"]) + 5.5
                    name = re.search(r"animation-name:\s*(gravity-\d+)", wrapper.attrib["style"]).group(1)
                    frames = paths[name]
                    self.assertGreaterEqual(len(frames), 10)
                    self.assertEqual(frames[-1], (100, 0, 0, 0))
                    self.assertEqual(sorted(frame[0] for frame in frames), [frame[0] for frame in frames])
                    for _, dx, dy, _ in frames:
                        # A circumscribed circle also bounds every interpolated rotation.
                        self.assertGreaterEqual(center_x + dx - radius, 0)
                        self.assertLessEqual(center_x + dx + radius, width)
                        self.assertGreaterEqual(center_y + dy - radius, 50, "Keep month labels clear.")
                        self.assertLessEqual(center_y + dy + radius, 258, "Keep the legend clear.")
                    settled = next(frame for frame in frames if frame[0] == 52)
                    position = (round(center_x + settled[1], 2), round(center_y + settled[2], 2))
                    self.assertGreaterEqual(position[1] - radius, 164)
                    positions.add(position)
                self.assertEqual(len(positions), active_count, "Squares must occupy distinct pile positions.")

    def test_api_errors_leave_existing_images_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            assets = Path(directory) / "assets"
            assets.mkdir()
            image = assets / "contributions.svg"
            image.write_text("previous good image")
            result = self.run_generator({"errors": [{"message": "Rate limit exceeded"}], "data": None}, directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(image.read_text(), "previous good image")

    def test_invalid_later_day_does_not_partially_replace_images(self):
        with tempfile.TemporaryDirectory() as directory:
            assets = Path(directory) / "assets"
            assets.mkdir()
            image = assets / "contributions.svg"
            image.write_text("previous good image")
            payload = response()
            payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"][1]["contributionDays"][0]["date"] = "not-a-date"
            result = self.run_generator(payload, directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(image.read_text(), "previous good image")


if __name__ == "__main__":
    unittest.main()
