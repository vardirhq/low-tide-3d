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

    def test_keeper_static_mesh_is_the_playable_explorer(self):
        scene = json.loads((ROOT / "poc.scene").read_text())
        explorer = next(e for e in scene["entities"] if e["id"] == "explorer")
        self.assertEqual(explorer["components"]["sindri.model"]["asset"], "assets/characters/keeper/keeper_static.glb")
        self.assertEqual(explorer["transform_3d"]["scale"], [1, 1, 1])
        self.assertTrue((ROOT / "assets/characters/keeper/keeper_static.glb").is_file())

    def test_explorer_can_recover_and_install_alternator(self):
        scene = json.loads((ROOT / "poc.scene").read_text())
        explorer = next(e for e in scene["entities"] if e["id"] == "explorer")
        self.assertEqual(explorer["components"]["sindri.script"]["script"], "Explorer")
        source = (ROOT / explorer["components"]["sindri.script"]["source"]).read_text()
        self.assertIn('World.take_signal("take_alternator")', source)
        self.assertIn('World.send_signal(crawler, "repair_engine", 1.0)', source)

    def test_boarding_switches_drive_and_camera(self):
        explorer = (ROOT / "scripts/explorer.decay").read_text()
        drive = (ROOT / "scripts/crawler_drive.decay").read_text()
        camera = (ROOT / "scripts/crawler_camera.decay").read_text()
        self.assertIn('Input.Keyboard.just_pressed("F")', explorer)
        self.assertIn('World.send_signal(crawler, "toggle_helm", 1.0)', explorer)
        self.assertIn('World.take_signal("toggle_helm")', drive)
        self.assertIn('World.take_signal("toggle_follow")', camera)
        self.assertIn('World.find("Explorer")', camera)

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
