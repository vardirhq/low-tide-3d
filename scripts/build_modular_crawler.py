#!/usr/bin/env python3
"""Build a static modular crawler preview from the existing kit manifest.

No engine API assumptions: emits ordinary sindri.model scene entities.
The original playable poc.scene remains unchanged.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Low_Tide_Kit" / "kit_manifest.json"
SCENE = ROOT / "poc.scene"
DEFAULT_LAYOUT = ROOT / "crawler" / "layout.json"
DEFAULT_OUTPUT = ROOT / "crawler-modular.scene"
CUTAWAY_HIDDEN = {"roof", "upper_walls"}


def build(manifest, scene, layout):
    catalog = {asset["id"]: asset for asset in manifest["assets"]}
    assembly = {item["name"]: item for item in manifest["assembly"]}
    overrides = layout.get("overrides", {})
    unknown = set(overrides) - set(assembly)
    if unknown:
        raise ValueError(f"Unknown assembly slots: {sorted(unknown)}")
    result = json.loads(json.dumps(scene))
    crawler = next(e for e in result["entities"] if e["id"] == "crawler")
    # This is a *static composition preview*, not a replacement for driving.
    result["entities"] = [e for e in result["entities"] if e["id"] != "crawler"]
    for name, instance in assembly.items():
        if instance["group"] in CUTAWAY_HIDDEN:
            continue
        choice = overrides.get(name, instance["asset"])
        if choice is None:
            continue
        if choice not in catalog:
            raise ValueError(f"Unknown asset {choice!r} in slot {name}")
        # Manifest coordinates are source X/right, Y/forward, Z/up.
        # GLB/Sindri coordinates are X/right, Y/up, -Z/forward.
        x, y, z = instance["position"]
        yaw = math.radians(instance.get("yaw_degrees", 0))
        entity = {
            "id": "module-" + name.replace("_", "-"),
            "name": f"Module: {name} ({choice})",
            "transform_3d": {
                "position": [x, z, -y],
                "rotation": [0, math.sin(yaw / 2), 0, math.cos(yaw / 2)],
                "scale": [1, 1, 1]
            },
            "components": {
                "sindri.model": {
                    "asset": f"Low_Tide_Kit/modules/{choice}.glb",
                    "layer": 1
                }
            }
        }
        result["entities"].append(entity)
    result.setdefault("metadata", {})["description"] = (
        "Static modular crawler assembly preview; original poc.scene remains playable."
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    scene = json.loads(SCENE.read_text())
    layout = json.loads(args.layout.read_text())
    output = build(manifest, scene, layout)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {args.output}: {sum(e['id'].startswith('module-') for e in output['entities'])} modules")


if __name__ == "__main__":
    main()
