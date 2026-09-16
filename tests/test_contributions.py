import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate_contributions.py"
NS = {"svg": "http://www.w3.org/2000/svg"}


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
