"""Guard the first Last Signal gameplay slice against accidental removal."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LastSignalSlice(unittest.TestCase):
    def test_salvage_landmarks_are_in_playable_scene(self):
        scene = json.loads((ROOT / "poc.scene").read_text())
        entities = {e["id"]: e for e in scene["entities"]}
        for entity_id in ("signal-radio", "signal-beacon", "signal-alternator", "signal-gauge"):
            with self.subTest(entity=entity_id):
                asset = entities[entity_id]["components"]["sindri.model"]["asset"]
                self.assertTrue((ROOT / asset).is_file(), asset)

    def test_alternator_recovery_is_connected(self):
        scene = json.loads((ROOT / "poc.scene").read_text())
        alternator = next(e for e in scene["entities"] if e["id"] == "signal-alternator")
        script = alternator["components"]["sindri.script"]
        self.assertEqual(script["script"], "RecoverAlternator")
        source = ROOT / script["source"]
        self.assertTrue(source.is_file())
        content = source.read_text()
        self.assertIn('Input.Keyboard.just_pressed("E")', content)
        self.assertIn("World.set_active(this.entity, false)", content)


if __name__ == "__main__":
    unittest.main()
