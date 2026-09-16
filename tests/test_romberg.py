import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate_romberg.py"
NS = {"svg": "http://www.w3.org/2000/svg"}


def load_generator():
    if not SCRIPT.is_file():
        raise AssertionError("The Romberg generator has not been implemented.")
    spec = importlib.util.spec_from_file_location("generate_romberg", SCRIPT)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    return generator


def area(triangle):
    a, b, c = triangle
    return abs((b[0] - a[0]) * (c[1] - a[1])
               - (b[1] - a[1]) * (c[0] - a[0])) / 2


class RombergGeometryTests(unittest.TestCase):
    def test_subdivision_preserves_the_actual_initial_triangles_and_unit_square(self):
        generator = load_generator()
        stages = generator.mesh_stages()
        self.assertEqual(stages[0], [((0, 0), (1, 0), (0, 1)),
                                    ((1, 0), (1, 1), (0, 1))])
        self.assertEqual([len(stage) for stage in stages], [2, 8, 32, 128, 512])
        for level, triangles in enumerate(stages):
            with self.subTest(level=level):
                self.assertEqual(sum(area(t) for t in triangles), 1)
                self.assertEqual(len({tuple(sorted(t)) for t in triangles}), len(triangles))
                # A conforming partition has only paired interior edges and
                # single boundary edges, with no gaps or overlapping faces.
                edges = {}
                for triangle in triangles:
                    self.assertEqual(area(triangle), 1 / len(triangles))
                    for x, y in triangle:
                        self.assertTrue(0 <= x <= 1 and 0 <= y <= 1)
                        self.assertEqual(x * 2**level, int(x * 2**level))
                        self.assertEqual(y * 2**level, int(y * 2**level))
                    for a, b in zip(triangle, triangle[1:] + triangle[:1]):
                        key = tuple(sorted((a, b)))
                        edges[key] = edges.get(key, 0) + 1
                for (a, b), count in edges.items():
                    boundary = (a[0] == b[0] and a[0] in (0, 1)
                                or a[1] == b[1] and a[1] in (0, 1))
                    self.assertEqual(count, 1 if boundary else 2)

    def test_centroid_quadrature_converges_on_the_original_function(self):
        generator = load_generator()
        self.assertEqual(generator.surface(0, 0), 0)
        self.assertEqual(generator.surface(1, 1), 2)
        estimates = []
        for triangles in generator.mesh_stages():
            # Independently sample the original function at each centroid.
            estimate = sum(area(t) * generator.surface(
                sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3
            ) for t in triangles)
            estimates.append(estimate)
        self.assertAlmostEqual(estimates[0], 5 / 9)
        errors = [2 / 3 - value for value in estimates]
        for coarse, fine in zip(errors, errors[1:]):
            self.assertAlmostEqual(coarse / fine, 4)


class RombergImageTests(unittest.TestCase):
    def test_every_drawn_face_uses_the_function_and_a_consistent_projection(self):
        generator = load_generator()
        svg = generator.render()
        self.assertEqual(svg, generator.render(), "The generated artwork must be deterministic.")
        root = ET.fromstring(svg)
        self.assertEqual(root.attrib["viewBox"], "0 0 640 280")
        self.assertEqual(root.attrib["role"], "img")
        self.assertIsNotNone(root.find("svg:title", NS))
        self.assertIsNotNone(root.find("svg:desc", NS))
        groups = root.findall(".//svg:g[@data-level]", NS)
        self.assertEqual(len(groups), 5)
        for level, group in enumerate(groups):
            faces = group.findall("svg:polygon[@data-vertices]", NS)
            self.assertEqual(len(faces), 2 * 4**level)
            self.assertEqual(group.attrib["data-triangles"], str(len(faces)))
            triangles = []
            for face in faces:
                vertices = [tuple(map(float, point.split(",")))
                            for point in face.attrib["data-vertices"].split()]
                points = [tuple(map(float, point.split(",")))
                          for point in face.attrib["points"].split()]
                triangles.append(tuple((x, y) for x, y, _ in vertices))
                for (x, y, z), (screen_x, screen_y) in zip(vertices, points):
                    self.assertEqual(z, x*x + y*y)
                    self.assertAlmostEqual(screen_x, 196 + 112*(x-y), places=2)
                    self.assertAlmostEqual(screen_y, 206 - 38*(x+y) - 48*z, places=2)
                    self.assertTrue(0 < screen_x < 350 and 25 < screen_y < 230)
            self.assertEqual(set(triangles), set(generator.mesh_stages()[level]))
            self.assertEqual(group.find("svg:text[@class='triangle-count']", NS).text,
                             str(len(faces)))
        self.assertNotIn("<script", svg)
        self.assertNotIn("href=", svg)

    def test_motion_has_a_final_hold_and_reduced_motion_shows_the_final_stage(self):
        generator = load_generator()
        for theme in ("light", "dark"):
            root = ET.fromstring(generator.render(theme=theme))
            style = root.find("svg:style", NS).text
            self.assertIn("animation-duration: 6s", style)
            self.assertIn("animation-iteration-count: infinite", style)
            self.assertIn("66%, 96% { opacity: 1; }", style)
            reduced_motion = style.split("@media (prefers-reduced-motion: reduce)")[1]
            self.assertIn(".mesh-stage { animation: none; opacity: 0; }", reduced_motion)
            self.assertIn(".mesh-stage.final-stage { opacity: 1; }", reduced_motion)

    def test_cli_produces_theme_variants_and_a_truly_static_fine_mesh(self):
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), "--output", directory],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in Path(directory).iterdir()},
                             {"romberg.svg", "romberg-dark.svg", "romberg-static.svg"})
            light = (Path(directory) / "romberg.svg").read_text()
            dark = (Path(directory) / "romberg-dark.svg").read_text()
            static = (Path(directory) / "romberg-static.svg").read_text()
            self.assertEqual(light, generator.render())
            self.assertNotEqual(light, dark)
            self.assertNotIn("@keyframes", static)
            self.assertNotIn("animation", static)
            self.assertIn("prefers-color-scheme: dark", static)
            root = ET.fromstring(static)
            groups = root.findall(".//svg:g[@data-level]", NS)
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0].attrib["data-triangles"], "512")
            self.assertEqual(len(root.findall(".//svg:polygon[@data-vertices]", NS)), 512)


if __name__ == "__main__":
    unittest.main()
