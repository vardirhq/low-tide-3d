"""Create a single four-view review sheet for the assembled Tidebreaker crane.

Uses the SAME software renderer as scripts/asset.py. The assemblies remain
independent GLBs; this is a static inspection pose, not animated gameplay.
"""
import copy
import json
import math
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import asset as preview
import build_tidebreaker as crane

OUT = ROOT / "Low_Tide_Kit"
OUT.mkdir(exist_ok=True)


def rz(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), -math.sin(a), 0],
                     [math.sin(a), math.cos(a), 0], [0, 0, 1]])


def rx(deg):
    a = math.radians(deg)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)],
                     [0, math.sin(a), math.cos(a)]])


parts = []


def add(name, rotation, translation):
    for source in crane.k.K[name]["parts"]:
        p = copy.copy(source)
        p["v"] = source["v"] @ rotation.T + translation
        p["name"] = name + "/" + source["name"]
        parts.append(p)


base = np.zeros(3)
add("tidebreaker_base", np.eye(3), base)
turret_origin = np.array([0, .13, .53])
add("tidebreaker_turret", np.eye(3), turret_origin)
shoulder = turret_origin + np.array([0, .17, .72])
main_rotation = rx(24)
add("tidebreaker_primary_boom", main_rotation, shoulder)
elbow = shoulder + main_rotation @ np.array([0, 2.2, 0])
outer_rotation = main_rotation @ rx(-38)
add("tidebreaker_secondary_boom", outer_rotation, elbow)
add("tidebreaker_winch", outer_rotation, elbow + outer_rotation @ np.array([0, 1.7, .25]))
add("tidebreaker_hook_block", outer_rotation, elbow + outer_rotation @ np.array([0, 2.49, -.8]))
for x, y, angle in [(-.53, -.45, 90), (.53, -.45, -90),
                    (-.53, .48, 90), (.53, .48, -90)]:
    add("tidebreaker_outrigger", rz(angle), np.array([x, y, .52]))

record = {"id": "tidebreaker_assembled_review", "parts": parts}
preview.render(record, OUT / "tidebreaker_review.png")
vertices = np.concatenate([p["v"] for p in parts])
report = {
    "assemblies": 7, "outrigger_instances": 4,
    "individual_parts": len(parts),
    "triangles": sum(len(p["f"]) for p in parts),
    "bounds_m": {"min": vertices.min(0).round(3).tolist(),
                 "max": vertices.max(0).round(3).tolist()},
    "pose": {"shoulder_deg": 24, "elbow_deg": -38},
    "note": "One assembled static inspection pose. Separate GLBs retain rig pivots. "
            "Standard single-prop 4000-triangle and grounded checks do not apply "
            "to this articulated multi-assembly machine."
}
(OUT / "tidebreaker_review.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
