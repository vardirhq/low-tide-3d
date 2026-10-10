"""Low Tide Keeper: original segmented low-poly character, in source Z-up meters."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Low_Tide_Kit'))
import build_kit as kit

kit.M.update({
    'coat': ('#be934a', 0, .94), 'coat_dark': ('#896b3e', 0, .97),
    'trousers': ('#42555a', 0, .95), 'skin': ('#ba8a69', 0, .9),
    'hat': ('#4c6462', 0, 1), 'scarf': ('#934e3e', 0, 1),
})

# All bind rotations are identity. Positions below are world-space bind origins.
# Root is ground-center; named limbs permit stable future animation retargeting.
JOINTS = [
    ('root', None, (0, 0, 0)),
    ('pelvis', 'root', (0, 0, .92)),
    ('spine', 'pelvis', (0, 0, 1.10)),
    ('chest', 'spine', (0, 0, 1.33)),
    ('head', 'chest', (0, 0, 1.60)),
    ('upper_arm_l', 'chest', (.29, 0, 1.39)),
    ('forearm_l', 'upper_arm_l', (.35, .005, 1.12)),
    ('hand_l', 'forearm_l', (.36, .03, .91)),
    ('upper_arm_r', 'chest', (-.29, 0, 1.39)),
    ('forearm_r', 'upper_arm_r', (-.35, .005, 1.12)),
    ('hand_r', 'forearm_r', (-.36, .03, .91)),
    ('thigh_l', 'pelvis', (.14, 0, .9)),
    ('shin_l', 'thigh_l', (.14, 0, .51)),
    ('foot_l', 'shin_l', (.14, 0, .14)),
    ('thigh_r', 'pelvis', (-.14, 0, .9)),
    ('shin_r', 'thigh_r', (-.14, 0, .51)),
    ('foot_r', 'shin_r', (-.14, 0, .14)),
]
NAMES = [j[0] for j in JOINTS]
kit.begin('keeper', [.8, .75], 'Keeper player-character prototype; +Y forward, feet at ground.')
PARTS = kit.K['keeper']['parts']
active = 'root'


def bind(name):
    global active
    active = name


def box(name, pos, size, material, bevel=.02):
    kit.box(name, pos, size, material, bevel)
    PARTS[-1]['joint'] = NAMES.index(active)


def cylinder(name, start, end, radius, material, sides=12):
    kit.cyl(name, start, end, radius, material, sides)
    PARTS[-1]['joint'] = NAMES.index(active)


bind('pelvis')
box('hips', (0, 0, .88), (.39, .25, .25), 'trousers', .045)
box('coat_hem', (0, -.006, .99), (.46, .32, .21), 'coat_dark', .035)
box('belt', (0, .012, 1.035), (.465, .325, .065), 'rubber', .02)
box('buckle', (0, .183, 1.035), (.075, .027, .055), 'gold', .008)
box('utility_pouch', (-.25, .055, .99), (.11, .2, .19), 'scarf', .022)

bind('spine')
box('lower_jacket', (0, 0, 1.16), (.44, .32, .24), 'coat', .04)
for x in [-.135, .135]:
    box('pocket', (x, .173, 1.14), (.13, .033, .15), 'coat_dark', .008)
    box('pocket_flap', (x, .194, 1.2), (.14, .022, .04), 'coat', .006)
box('zipper', (0, .171, 1.165), (.018, .01, .2), 'edge', .003)

bind('chest')
box('upper_jacket', (0, 0, 1.355), (.5, .34, .25), 'coat', .055)
box('zipper', (0, .18, 1.34), (.019, .013, .19), 'edge', .003)
for x in [-.175, .175]:
    box('backpack_strap', (x, .17, 1.34), (.05, .042, .25), 'steel', .012)
box('neck', (0, 0, 1.52), (.15, .15, .16), 'skin', .022)
box('scarf_collar', (0, .01, 1.495), (.29, .27, .09), 'scarf', .025)
box('scarf_tail', (.065, .195, 1.41), (.085, .028, .18), 'scarf', .012)
box('backpack', (0, -.235, 1.26), (.35, .22, .41), 'teal', .04)
box('backpack_flap', (0, -.255, 1.44), (.38, .24, .075), 'steel', .022)
box('rear_pocket', (0, -.365, 1.22), (.26, .07, .2), 'rust', .018)
for x in [-.1, .1]:
    box('pack_strap', (x, -.403, 1.26), (.032, .02, .21), 'gold', .005)
cylinder('bedroll', (-.23, -.26, 1.04), (.23, -.26, 1.04), .075, 'linen')
for x in [-.15, .15]:
    cylinder('bedroll_tie', (x-.016, -.26, 1.04), (x+.016, -.26, 1.04), .079, 'coat_dark')

bind('head')
box('face', (0, .015, 1.645), (.275, .255, .285), 'skin', .04)
for x in [-.151, .151]:
    box('ear', (x, .013, 1.65), (.047, .067, .08), 'skin', .014)
box('nose', (0, .155, 1.64), (.049, .063, .064), 'skin', .013)
for x in [-.068, .068]:
    box('eye', (x, .146, 1.68), (.025, .012, .021), 'dark', .004)
    box('brow', (x, .148, 1.715), (.054, .013, .012), 'coat_dark', .003)
box('mouth', (0, .146, 1.583), (.054, .012, .009), 'coat_dark', .002)
box('beanie', (0, 0, 1.80), (.305, .28, .14), 'hat', .05)
box('hat_cuff', (0, .005, 1.746), (.32, .29, .065), 'steel', .024)
box('hat_patch', (-.084, .159, 1.76), (.055, .014, .033), 'cream', .004)

for side, x in [('l', 1), ('r', -1)]:
    bind('upper_arm_'+side)
    cylinder('shoulder_joint', (x*.275, 0, 1.39), (x*.31, 0, 1.39), .105, 'coat_dark')
    box('upper_sleeve', (x*.335, 0, 1.26), (.17, .21, .26), 'coat', .035)
    box('shoulder_patch', (x*.427, .005, 1.30), (.019, .12, .08), 'teal', .007)
    bind('forearm_'+side)
    box('elbow', (x*.352, -.005, 1.13), (.155, .175, .12), 'coat_dark', .027)
    box('lower_sleeve', (x*.357, .013, 1.015), (.15, .18, .205), 'coat', .03)
    box('cuff', (x*.36, .026, .926), (.155, .182, .06), 'steel', .012)
    bind('hand_'+side)
    box('glove', (x*.36, .034, .865), (.125, .13, .12), 'coat_dark', .024)
    box('thumb', (x*.294, .055, .89), (.045, .07, .065), 'coat_dark', .014)
    bind('thigh_'+side)
    box('thigh', (x*.14, 0, .72), (.175, .235, .34), 'trousers', .035)
    box('cargo_pocket', (x*.239, .0, .72), (.037, .18, .15), 'steel', .012)
    bind('shin_'+side)
    box('knee', (x*.14, .06, .505), (.16, .18, .12), 'steel', .025)
    box('shin', (x*.14, -.007, .335), (.15, .18, .3), 'trousers', .025)
    bind('foot_'+side)
    box('boot_upper', (x*.14, .01, .17), (.19, .245, .2), 'coat_dark', .035)
    box('boot_toe', (x*.14, .075, .073), (.205, .35, .13), 'rubber', .028)
    box('sole', (x*.14, .075, .022), (.211, .357, .044), 'steel', .01)
    for z in [.13, .18, .22]:
        box('lace', (x*.14, .139, z), (.095, .009, .012), 'gold', .003)

# Keep the relaxed silhouette inside the starter crawler's 0.82 m doorway.
# Bake the proportion change into both mesh and bind skeleton, not node scale.
for part in PARTS:
    part['v'][:, 0] *= .88
JOINTS = [(name, parent, (position[0]*.88, position[1], position[2]))
          for name, parent, position in JOINTS]
