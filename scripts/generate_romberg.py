#!/usr/bin/env python3
"""Draw the Romberg project's triangular refinement with standard-library SVG.

Geometry follows https://github.com/solvisantos22/Romberg/blob/master/romberg2.py:
the unit square starts with two triangles and each edge is bisected at every
level. Vertices are lifted onto f(x, y) = x² + y² to illustrate the surface;
this is a mesh illustration, not a plot of extrapolation error or runtime.
"""

import argparse
from pathlib import Path


PALETTES = {
    "light": {
        "text": "#1f2328", "muted": "#59636e", "axis": "#8c959f", "edge": "#0969da",
        "faces": ("#ddf4ff", "#b6e3ff", "#a5d6ff", "#80ccff", "#79c0ff", "#54aeff", "#388bfd", "#218bff"),
    },
    "dark": {
        "text": "#f0f6fc", "muted": "#9198a1", "axis": "#656c76", "edge": "#79c0ff",
        "faces": ("#102b47", "#123c64", "#164b7d", "#195899", "#1f65b5", "#1f6feb", "#388bfd", "#58a6ff"),
    },
}


def surface(x, y):
    """The smooth example function in romberg2.py."""
    return x*x + y*y


def mesh_stages():
    """Return the original two triangles and four midpoint refinements."""
    stages = [[((0, 0), (1, 0), (0, 1)), ((1, 0), (1, 1), (0, 1))]]
    for _ in range(4):
        refined = []
        for a, b, c in stages[-1]:
            ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
            ca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
            refined.extend(((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)))
        stages.append(refined)
    return stages


def project(x, y, z):
    """A fixed oblique view keeps all stages in the same coordinate system."""
    return 196 + 112*(x-y), 206 - 38*(x+y) - 48*z


def color_rules(theme):
    colors = PALETTES[theme]
    return (f'text {{ fill: {colors["text"]}; }} '
            f'.muted {{ fill: {colors["muted"]}; }} '
            f'.axis {{ stroke: {colors["axis"]}; }} '
            f'.mesh-edges {{ stroke: {colors["edge"]}; }}\n'
            + "\n".join(f'.facet-{i} {{ fill: {color}; }}' for i, color in enumerate(colors["faces"])))


def render(theme="light", animated=True):
    style = color_rules(theme) + """
    .axis { fill: none; stroke-width: 1; }
    .mesh-edges { fill: none; stroke-width: .7; stroke-opacity: .65; stroke-linejoin: round; }
    .triangle-count { font-variant-numeric: tabular-nums; }
    """
    if animated:
        style += """
    .mesh-stage {
      opacity: 0;
      animation-duration: 6s;
      animation-timing-function: linear;
      animation-iteration-count: infinite;
      animation-fill-mode: both;
    }
    .mesh-stage.final-stage { opacity: 1; }
    .stage-0 { animation-name: refinement-0; }
    .stage-1 { animation-name: refinement-1; }
    .stage-2 { animation-name: refinement-2; }
    .stage-3 { animation-name: refinement-3; }
    .stage-4 { animation-name: refinement-4; }
    @keyframes refinement-0 {
      0%, 12%, 100% { opacity: 1; }
      16%, 96% { opacity: 0; }
    }
    @keyframes refinement-1 {
      0%, 12%, 32%, 100% { opacity: 0; }
      16%, 28% { opacity: 1; }
    }
    @keyframes refinement-2 {
      0%, 28%, 48%, 100% { opacity: 0; }
      32%, 44% { opacity: 1; }
    }
    @keyframes refinement-3 {
      0%, 44%, 66%, 100% { opacity: 0; }
      48%, 62% { opacity: 1; }
    }
    @keyframes refinement-4 {
      0%, 62%, 100% { opacity: 0; }
      66%, 96% { opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .mesh-stage { animation: none; opacity: 0; }
      .mesh-stage.final-stage { opacity: 1; }
    }
    """
    else:
        style += "@media (prefers-color-scheme: dark) {" + color_rules("dark") + "}"
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="280" viewBox="0 0 640 280" role="img" aria-labelledby="title desc">',
        '<title id="title">Triangular mesh refinement for f(x, y) = x² + y²</title>',
        '<desc id="desc">The unit square is split into two triangles. Each triangle splits into four at its edge midpoints, giving 2, 8, 32, 128 and 512 triangles. '
        + ('The six-second loop pauses on the finest mesh before restarting. ' if animated else 'The still view shows the finest mesh. ')
        + 'Mesh vertices lie on the function surface. This illustrates refinement, not measured integration error or runtime.</desc>',
        f'<style>{style}</style>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        '<path class="axis" d="M 63,161 L 196,206 L 329,161"/>',
        '<path class="axis" stroke-dasharray="3 5" opacity=".5" d="M 84,168 L 196,130 L 308,168 M 84,168 L 84,120 M 308,168 L 308,120 M 196,130 L 196,34"/>',
        '<text class="muted" x="342" y="166" font-size="18">x</text>',
        '<text class="muted" x="47" y="166" font-size="18">y</text>',
        '<text class="muted" x="196" y="249" text-anchor="middle" font-size="20">0 ≤ x, y ≤ 1</text>',
        '<text x="370" y="87" font-size="24">f(x, y) = x² + y²</text>',
        '<text class="muted" x="447" y="149" font-size="21">triangles</text>',
        '<text class="muted" x="370" y="181" font-size="18">midpoint subdivision</text>',
    ]
    stages = mesh_stages()
    for level in (range(len(stages)) if animated else (len(stages) - 1,)):
        triangles = stages[level]
        final = " final-stage" if level == len(stages) - 1 else ""
        parts.append(f'<g class="mesh-stage stage-{level}{final}" data-level="{level}" data-triangles="{len(triangles)}">')
        edges = set()
        for triangle in triangles:
            vertices = [(x, y, surface(x, y)) for x, y in triangle]
            points = " ".join(f"{px:.3f},{py:.3f}" for px, py in (project(*vertex) for vertex in vertices))
            data = " ".join(f"{x:.12g},{y:.12g},{z:.12g}" for x, y, z in vertices)
            # Shade by height only; there is no numerical-error color scale.
            shade = min(7, int(sum(vertex[2] for vertex in vertices) / 3 * 4))
            parts.append(f'<polygon class="facet-{shade}" points="{points}" data-vertices="{data}"/>')
            for a, b in zip(triangle, triangle[1:] + triangle[:1]):
                edges.add(tuple(sorted((a, b))))
        path = " ".join("M " + " L ".join(f"{px:.3f},{py:.3f}" for px, py in
                                           (project(x, y, surface(x, y)) for x, y in edge))
                        for edge in sorted(edges))
        parts.append(f'<path class="mesh-edges" d="{path}"/>')
        parts.append(f'<text class="triangle-count" x="370" y="149" font-size="36">{len(triangles)}</text>')
        parts.append('</g>')
    parts.extend(('</g>', '</svg>', ''))
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, theme, animated in (("romberg.svg", "light", True),
                                     ("romberg-dark.svg", "dark", True),
                                     ("romberg-static.svg", "light", False)):
        (args.output / filename).write_text(render(theme, animated), encoding="utf-8")


if __name__ == "__main__":
    main()
