# Romberg mesh illustration

The profile illustrates the actual example in [romberg2.py](https://github.com/solvisantos22/Romberg/blob/master/romberg2.py): `f(x, y) = x² + y²` on the unit square. The square starts as two triangles. Splitting each triangle into four produces meshes of 2, 8, 32, 128 and 512 triangles.

The projected surface shows values at mesh vertices. It illustrates geometric refinement, not a measured error, runtime or the complete Romberg extrapolation calculation. The triangle count matches the visible stage.

The six-second animation repeats so it remains visible after scrolling through the profile. The **See the mesh refine** section can be collapsed to hide it. Reduced-motion visitors receive a static final mesh; the animated files also handle reduced motion internally. Light, dark and still versions are checked into `assets/`.

Regenerate after editing the illustration:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/generate_romberg.py
```

Checks cover the unit-square partition and subdivision counts, sampled surface values, reproducible SVG output, stage visibility, reduced motion and mobile layout. These images use no live data and do not need daily regeneration.
