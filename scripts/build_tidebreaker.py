"""Tidebreaker articulated salvage crane. Run: python3 scripts/build_tidebreaker.py

Procedural, palette-only GLBs. Parts are authored around their real pivot.
The JSON rig defines how a game can assemble/animate them; this is NOT a
working crane controller or a physics simulation.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Low_Tide_Kit"))
import build_kit as k

OUT = ROOT / "Low_Tide_Kit"
B, C, P = k.box, k.cyl, k.pipe


def part(name, size, description):
    k.begin(name, size, description, [k.socket("mount", [0, 0, 0], [0, 0, 1])])


def bolt(x, y, z):
    C("fastener", (x, y, z), (x, y, z + .025), .035, "gold", 8)


# Coordinates: X right, Y forward, Z up. Front / operator faces -Y.
# Root mount footprint 1.35 x 1.4 m, suitable for a reinforced crawler deck.
part("tidebreaker_base", [1.4, 1.5], "Crane mounting skid and turntable; operator side -Y.")
B("mounting_skid", (0, 0, .12), (1.3, 1.4, .24), "steel", .025)
for x in [-.5, .5]:
    B("reinforcing_beam", (x, 0, .27), (.13, 1.27, .13), "rust")
    for y in [-.53, .53]:
        bolt(x, y, .24)
C("slew_ring", (0, .13, .3), (0, .13, .47), .49, "edge", 24)
C("slew_bearing", (0, .13, .47), (0, .13, .53), .36, "dark", 20)
for i in range(16):
    a = i * math.tau / 16
    bolt(.435 * math.cos(a), .13 + .435 * math.sin(a), .48)
B("operator_pedestal", (0, -.51, .57), (.47, .31, .65), "teal", .025)
B("operator_panel", (0, -.7, .93), (.55, .15, .23), "dark")
for x in [-.16, .16]:
    C("control_lever", (x, -.8, .94), (x, -.84, 1.14), .019, "edge", 10)
    C("lever_grip", (x, -.84, 1.13), (x, -.84, 1.19), .045, "gold", 10)
B("emergency_stop", (.0, -.79, .99), (.075, .025, .075), "red")
for x in [-.4, .4]:
    B("guard", (x, -.55, .78), (.05, .25, .55), "gold")
B("pressure_label", (0, -.79, .85), (.27, .02, .09), "cream", .002)

# Rotating upper turret. Pivot is at the center of the slew bearing.
part("tidebreaker_turret", [1.15, 1.2], "Rotating crane turret; local origin is slew pivot.")
B("turntable", (0, 0, .11), (1.05, 1.0, .22), "teal", .03)
for x in [-.34, .34]:
    B("boom_cheek", (x, .16, .48), (.14, .65, .78), "steel", .02)
    C("boom_pivot", (x, .17, .72), (x + .07, .17, .72), .15, "edge", 16)
B("hydraulic_reservoir", (0, -.28, .34), (.45, .37, .37), "rust")
C("slew_motor", (.34, -.33, .3), (.51, -.33, .3), .16, "steel", 12)
for x in [-.22, .22]:
    C("lift_ram_body", (x, -.12, .4), (x, .31, .91), .075, "rust", 12)
    C("lift_ram_rod", (x, .29, .89), (x, .48, 1.11), .035, "gold", 10)
P("hydraulic_supply", [(-.3, -.2, .2), (-.48, -.05, .35), (-.47, .25, .68)], .022, "rubber")

# Longitudinal boom runs +Y. Child pivot is at local (0,0,0).
part("tidebreaker_primary_boom", [.78, 2.55], "Main knuckle boom; root at turret shoulder pivot.")
B("main_box_beam", (0, 1.1, 0), (.63, 2.2, .55), "teal", .04)
for x in [-.26, .26]:
    B("edge_stiffener", (x, 1.1, -.29), (.055, 2.12, .075), "edge")
    for y in [.32, 1.1, 1.88]:
        B("gusset", (x, y, .28), (.095, .2, .13), "rust", .01)
C("shoulder_pin", (-.42, .05, 0), (.42, .05, 0), .14, "edge", 16)
C("elbow_pin", (-.43, 2.2, 0), (.43, 2.2, 0), .14, "edge", 16)
for x in [-.19, .19]:
    C("knuckle_cylinder", (x, .5, .31), (x, 1.5, .39), .085, "rust", 12)
    C("knuckle_rod", (x, 1.46, .39), (x, 1.85, .44), .045, "gold", 10)
P("boom_hose", [(.32, .25, .08), (.43, .8, .23), (.43, 1.55, .2), (.34, 2.12, .1)], .026, "rubber")
B("inspection_plate", (0, .8, .286), (.25, .39, .014), "cream", .004)

part("tidebreaker_secondary_boom", [.63, 2.35], "Articulated outer boom with telescoping channel.")
B("outer_shell", (0, .91, 0), (.55, 1.83, .45), "steel", .035)
B("telescoping_rail", (0, 1.91, 0), (.4, 1.25, .32), "teal", .025)
for x in [-.22, .22]:
    B("wear_strip", (x, 1.9, -.16), (.04, 1.12, .04), "gold", .006)
C("knuckle_pin", (-.35, .08, 0), (.35, .08, 0), .12, "edge", 16)
C("nose_pin", (-.3, 2.49, 0), (.3, 2.49, 0), .11, "edge", 12)
P("extension_hose", [(.28, .2, .08), (.36, .9, .13), (.32, 1.85, .13), (.22, 2.48, .08)], .024, "rubber")
B("hazard_mark", (0, 2.28, .172), (.24, .2, .015), "red", .003)

part("tidebreaker_winch", [.72, .8], "Winch cassette mounted to upper boom; cable exits +Y.")
B("winch_carriage", (0, 0, .12), (.67, .76, .24), "rust")
for x in [-.26, .26]:
    B("drum_bearing", (x, .02, .35), (.1, .45, .39), "steel")
    C("drum_flange", (x - .03, .02, .37), (x + .03, .02, .37), .23, "edge", 16)
C("spool", (-.25, .02, .37), (.25, .02, .37), .17, "dark", 16)
for x in [-.19, -.12, -.05, .02, .09, .16]:
    C("cable_winding", (x, .02, .37), (x + .03, .02, .37), .181, "steel", 16)
C("winch_motor", (.3, -.24, .34), (.47, -.24, .34), .15, "teal", 12)
C("fairlead", (-.16, .39, .26), (.16, .39, .26), .065, "gold", 12)

part("tidebreaker_hook_block", [.5, .45], "Suspended load hook and twin sheaves; static parked pose.")
for x in [-.15, .15]:
    B("cheek_plate", (x, 0, .38), (.065, .32, .48), "rust", .018)
for z in [.25, .48]:
    C("sheave", (-.16, 0, z), (.16, 0, z), .13, "edge", 14)
C("swivel", (0, 0, .1), (0, 0, .23), .065, "gold", 12)
P("hook", [(0, 0, .1), (0, 0, -.07), (.12, 0, -.17), (.23, 0, -.1), (.22, 0, -.025)], .052, "gold")
B("safety_latch", (.16, 0, -.035), (.12, .045, .022), "red", .004)

part("tidebreaker_outrigger", [.7, 1.65], "One extendable stabilizer; mount at inner end, +Y outward.")
B("fixed_channel", (0, .37, .38), (.31, .74, .26), "steel", .015)
B("sliding_beam", (0, 1.02, .38), (.22, .95, .19), "teal", .014)
B("jack_housing", (0, 1.42, .37), (.32, .31, .34), "rust", .02)
C("jack", (0, 1.42, .36), (0, 1.42, -.18), .07, "steel", 12)
C("jack_rod", (0, 1.42, -.14), (0, 1.42, -.43), .046, "gold", 10)
B("ground_pad", (0, 1.42, -.47), (.54, .5, .08), "edge", .018)
for x in [-.17, .17]:
    bolt(x, 1.42, .55)
P("jack_hose", [(.17, .35, .5), (.21, 1.2, .55), (.18, 1.42, .47)], .022, "rubber")

# Separate GLBs preserve independent transforms. The authored rig is a
# descriptive hierarchy for integration, not a promise of engine animation.
rig = {
    "name": "Tidebreaker Mk I", "units": "meters",
    "axes": "X right, Y forward, Z up",
    "status": "static meshes and rig specification; no gameplay controller",
    "nodes": [
        {"id": "base", "asset": "tidebreaker_base", "parent": None, "translation": [0, 0, 0]},
        {"id": "turret", "asset": "tidebreaker_turret", "parent": "base", "translation": [0, .13, .53], "joint": {"type": "yaw", "axis": [0, 0, 1], "limits_deg": [-170, 170]}},
        {"id": "primary", "asset": "tidebreaker_primary_boom", "parent": "turret", "translation": [0, .17, .72], "joint": {"type": "pitch", "axis": [1, 0, 0], "limits_deg": [-15, 65]}},
        {"id": "secondary", "asset": "tidebreaker_secondary_boom", "parent": "primary", "translation": [0, 2.2, 0], "joint": {"type": "pitch", "axis": [1, 0, 0], "limits_deg": [-105, 20]}},
        {"id": "winch", "asset": "tidebreaker_winch", "parent": "secondary", "translation": [0, 1.7, .25]},
        {"id": "hook", "asset": "tidebreaker_hook_block", "parent": "secondary", "translation": [0, 2.49, -.8], "joint": {"type": "cable_length", "range_m": [.5, 6]}},
    ],
    "outriggers": [
        {"asset": "tidebreaker_outrigger", "translation": [x, y, .52], "yaw_degrees": angle}
        for x, y, angle in [(-.53, -.45, 90), (.53, -.45, -90), (-.53, .48, 90), (.53, .48, -90)]
    ],
    "future_gameplay": ["turret rotation", "knuckle motion", "telescoping extension", "winch cable", "stabilizer deployment", "load attachment", "mass and stability checks"],
}

if __name__ == "__main__":
    names = [n for n in k.K if n.startswith("tidebreaker_")]
    results = []
    for name in names:
        results.append(k.export(OUT / "modules" / (name + ".glb"),
                                [{"name": name, "asset": name, "position": [0, 0, 0],
                                  "yaw_degrees": 0, "group": "salvage_crane"}]))
    (OUT / "tidebreaker_rig.json").write_text(json.dumps(rig, indent=2) + "\n")
    print(json.dumps({"modules": results, "rig": "Low_Tide_Kit/tidebreaker_rig.json"}, indent=2))
