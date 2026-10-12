"""The asset tool's checks catch the mistakes a model makes when writing assets."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAVE_DEPS = all(importlib.util.find_spec(m) for m in ("numpy", "scipy", "PIL"))


@unittest.skipUnless(HAVE_DEPS, "needs numpy, scipy and Pillow")
class AssetToolChecks(unittest.TestCase):
    count = 0

    def run_spec(self, body):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import asset as tool
        AssetToolChecks.count += 1
        name = f"check_{AssetToolChecks.count}"
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.py"
            spec.write_text(f"asset('{name}', [1, 1], 'test')\n" + body)
            a = tool.build(spec)
            errors, warnings = tool.check(a)
            tool.render(a, Path(tmp) / "preview.png")
            self.assertTrue((Path(tmp) / "preview.png").stat().st_size > 1000)
        return " ".join(errors), " ".join(warnings)

    def test_a_clean_asset_passes(self):
        errors, warnings = self.run_spec(
            "box('body', (0, 0, .2), (.5, .5, .4), 'teal')\n"
            "box('label', (0, -.255, .2), (.2, .02, .1), 'cream')\n")
        self.assertEqual((errors, warnings), ("", ""))

    def test_unknown_material_is_an_error(self):
        errors, _ = self.run_spec("box('body', (0, 0, .2), (.5, .5, .4), 'purple')\n")
        self.assertIn("unknown materials ['purple']", errors)

    def test_below_ground_and_nothing_on_the_ground(self):
        errors, _ = self.run_spec("box('sunk', (0, 0, 0), (.5, .5, .4), 'steel')\n")
        self.assertIn("'sunk' goes", errors)
        errors, _ = self.run_spec("box('hovering', (0, 0, .5), (.5, .5, .4), 'steel')\n")
        self.assertIn("nothing touches the ground", errors)

    def test_floating_part_and_footprint(self):
        _, warnings = self.run_spec(
            "box('body', (0, 0, .2), (.5, .5, .4), 'steel')\n"
            "box('balloon', (0, 0, 1.2), (.2, .2, .2), 'red')\n"
            "box('wing', (.9, 0, .2), (.4, .1, .1), 'edge')\n")
        self.assertIn("'balloon' floats", warnings)
        self.assertIn("'wing' reaches outside", warnings)

    def test_flush_faces_flicker(self):
        _, warnings = self.run_spec(
            "box('body', (0, 0, .2), (.5, .5, .4), 'teal')\n"
            "box('plate', (0, -.24, .2), (.2, .02, .1), 'cream')\n")
        self.assertIn("'body' and 'plate' have faces in the same plane", warnings)


if __name__ == "__main__":
    unittest.main()
