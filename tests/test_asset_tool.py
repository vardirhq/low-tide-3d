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

    def suggestions(self, body):
        """The fixes suggested for a spec, and the spec with them applied, rechecked."""
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import asset as tool
        AssetToolChecks.count += 1
        name = f"fix_{AssetToolChecks.count}"
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.py"
            spec.write_text(f"asset('{name}', [1, 1], 'test')\n" + body)
            fixes = tool.suggest(tool.build(spec))
            lines = spec.read_text().splitlines()
            for fix in fixes:
                self.assertEqual(lines[fix["line"] - 1], fix["original"])
                lines[fix["line"] - 1] = fix["replacement"]
            AssetToolChecks.count += 1
            lines[0] = lines[0].replace(name, f"fix_{AssetToolChecks.count}")
            spec.write_text("\n".join(lines) + "\n")
            _, warnings = tool.check(tool.build(spec))
        return fixes, warnings

    def test_a_lone_hovering_part_gets_a_seating_suggestion(self):
        fixes, after = self.suggestions(
            "box('base', (0, 0, .055), (.8, .8, .11), 'rust')\n"
            "box('crate', (0, 0, .34), (.4, .4, .4), 'wood')\n")
        self.assertEqual(len(fixes), 1)
        self.assertEqual(fixes[0]["line"], 3)
        self.assertEqual(fixes[0]["replacement"], "box('crate', (0, 0, .3105), (.4, .4, .4), 'wood')")
        self.assertEqual(after, [], "the fix clears the warning")

    def test_a_part_joined_by_a_pipe_is_left_to_judgement(self):
        fixes, _ = self.suggestions(
            "box('base', (0, 0, .055), (.8, .8, .11), 'rust')\n"
            "box('post', (.3, 0, .5), (.1, .1, .8), 'steel')\n"
            "cyl('tank', (0, 0, .15), (0, 0, .7), .2, 'teal', 16)\n"
            "pipe('feed', [(.2, 0, .5), (.25, 0, .5)], .02, 'edge')\n")
        self.assertEqual(fixes, [])

    def test_parts_made_in_a_loop_are_left_to_judgement(self):
        fixes, _ = self.suggestions(
            "box('base', (0, 0, .055), (.8, .8, .11), 'rust')\n"
            "for x in [-.2, .2]:\n"
            "    box('crate', (x, 0, .2), (.2, .2, .15), 'wood')\n")
        self.assertEqual(fixes, [])

    def test_a_flush_plate_is_moved_proud(self):
        fixes, after = self.suggestions(
            "box('body', (0, 0, .2), (.5, .5, .4), 'teal')\n"
            "box('plate', (0, -.24, .2), (.2, .02, .1), 'cream')\n")
        self.assertEqual([f["replacement"] for f in fixes],
                         ["box('plate', (0, -.245, .2), (.2, .02, .1), 'cream')"])
        self.assertEqual(after, [])

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

    def test_a_group_floating_together_is_caught(self):
        # A tank with its hoop touches only itself, hovering over the base.
        _, warnings = self.run_spec(
            "box('base', (0, 0, .05), (.8, .8, .1), 'rust')\n"
            "cyl('tank', (0, 0, .5), (0, 0, 1.0), .3, 'teal', 16)\n"
            "cyl('hoop', (0, 0, .6), (0, 0, .63), .31, 'edge', 16)\n")
        self.assertIn("a group of 2 parts ('hoop', 'tank') floats together", warnings)

    def test_a_near_miss_above_the_surface_is_caught(self):
        # Joined to the base by a pipe, so connected, but hovering 4 cm over it.
        _, warnings = self.run_spec(
            "box('base', (0, 0, .055), (.8, .8, .11), 'rust')\n"
            "cyl('tank', (0, 0, .15), (0, 0, .9), .25, 'teal', 16)\n"
            "pipe('stay', [(.2, 0, .1), (.2, 0, .3)], .02, 'edge')\n")
        self.assertIn("'tank' hovers 0.040 m above 'base' under it; seat it at z=0.110", warnings)

    def test_wall_mounted_parts_are_not_near_misses(self):
        _, warnings = self.run_spec(
            "box('wall', (0, 0, .5), (.8, .1, 1.0), 'steel')\n"
            "box('shelf', (0, -.15, .6), (.6, .2, .03), 'wood')\n")
        self.assertEqual(warnings, "")

    def test_flush_faces_flicker(self):
        _, warnings = self.run_spec(
            "box('body', (0, 0, .2), (.5, .5, .4), 'teal')\n"
            "box('plate', (0, -.24, .2), (.2, .02, .1), 'cream')\n")
        self.assertIn("'body' and 'plate' have faces in the same plane", warnings)


if __name__ == "__main__":
    unittest.main()
