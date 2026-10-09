#!/usr/bin/env python3
"""Validate crawler equipment slots against scene, script and kit manifest.

This file intentionally does not rewrite Decay: runtime slot APIs are not yet
verified in Sindri. It provides a checked source of truth for the next slice.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate():
    slots = json.loads((ROOT / "crawler/equipment_slots.json").read_text())["slots"]
    scene = json.loads((ROOT / "poc.scene").read_text())
    manifest = json.loads((ROOT / "Low_Tide_Kit/kit_manifest.json").read_text())
    drive = (ROOT / "scripts/crawler_drive.decay").read_text()
    entities = {e["id"]: e for e in scene["entities"]}
    assembly = {a["name"]: a for a in manifest["assembly"]}
    ids = [s["id"] for s in slots]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate equipment slot ID")
    for slot in slots:
        mount = assembly[slot["assembly_mount"]]
        if mount["asset"] != slot["asset"] and slot["id"] != "cargo-rear":
            raise ValueError(f"Wrong asset for {slot['id']}")
        entity = entities[slot["scene_entity"]]
        expected_asset = f"Low_Tide_Kit/modules/{slot['asset']}.glb"
        if entity["components"]["sindri.model"]["asset"] != expected_asset:
            raise ValueError(f"Asset mismatch: {slot['id']}")
        position = slot["position"]
        if entity["transform_3d"]["position"] != position:
            raise ValueError(f"Scene position mismatch: {slot['id']}")
        values = ", ".join(str(float(x)) for x in position)
        if f'attach_equipment("{slot["name"]}", Vec3({values}))' not in drive:
            raise ValueError(f"Runtime mount mismatch: {slot['id']}")
    return len(slots)


if __name__ == "__main__":
    print(f"Validated {validate()} crawler equipment slots")
