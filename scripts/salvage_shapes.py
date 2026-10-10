"""Last Signal asset definitions. Reuse the original crawler palette and primitives.

All authoring is X-right/Y-forward/Z-up meters; the shared exporter converts to
Y-up glTF. These are static prototype assets, not interactive gameplay entities.
"""
import sys
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Low_Tide_Kit'))
import build_kit as kit

box, cyl, pipe = kit.box, kit.cyl, kit.pipe
ASSETS = []


def start(name, footprint, description, anchors=()):
    ASSETS.append(name)
    sockets = [kit.socket('mount', [0, 0, 0], [0, 0, -1])]
    sockets.extend(kit.socket(n, list(p), list(normal)) for n, p, normal in anchors)
    kit.begin(name, footprint, description, sockets)


def feet(width, depth, height):
    for x in [-width / 2, width / 2]:
        for y in [-depth / 2, depth / 2]:
            box('foot', (x, y, height / 2), (.07, .07, height), 'steel')


def dial(x, y, z, radius=.055):
    cyl('dial_rim', (x, y, z), (x, y-.025, z), radius*1.2, 'gold', 12)
    cyl('dial_face', (x, y-.027, z), (x, y-.032, z), radius, 'cream', 12)
    pipe('needle', [(x, y-.035, z), (x+radius*.4, y-.035, z+radius*.5)], .005, 'dark')


start('radio_desk', [1.25, .75], 'Salvageable receiver and recording desk; operator faces +Y.',
      [('operator', (0, -.65, 0), (0, -1, 0)), ('power', (.48, .34, .5), (0, 1, 0))])
feet(1.05, .5, .8)
box('desktop', (0, 0, .82), (1.25, .75, .08), 'woodlight')
box('receiver', (-.12, .1, 1.07), (.91, .43, .42), 'teal', .03)
box('faceplate', (-.12, -.126, 1.08), (.83, .025, .31), 'dark')
box('tuner', (-.19, -.143, 1.13), (.44, .008, .09), 'screen', .002)
for x in [-.37, -.29, -.21, -.13, -.05]:
    box('frequency_tick', (x, -.149, 1.13), (.009, .006, .05), 'cream', 0)
for x in [-.36, -.12, .14]:
    cyl('knob', (x, -.145, 1.0), (x, -.19, 1.0), .043, 'gold', 12)
for z in [.96, 1.01, 1.06, 1.11, 1.16]:
    box('speaker_grille', (.2, -.148, z), (.15, .015, .014), 'edge', .002)
cyl('microphone_base', (.44, -.08, .86), (.44, -.08, .9), .1, 'steel', 12)
pipe('gooseneck', [(.44, -.08, .9), (.44, -.08, 1.18), (.44, -.18, 1.25)], .018, 'edge')
box('microphone', (.44, -.18, 1.26), (.09, .07, .15), 'dark')
box('recording', (-.25, -.27, .883), (.23, .12, .03), 'cream')
for x in [-.31, -.2]:
    cyl('tape_reel', (x, -.27, .9), (x, -.27, .907), .025, 'dark', 10)
pipe('power_cable', [(.3, .32, 1), (.43, .35, .55), (.4, .34, .3)], .018, 'rubber')

start('tide_gauge', [.5, .5], 'Marked tide staff with sensor enclosure; height marks every 0.25 m.')
box('base', (0, 0, .07), (.5, .5, .14), 'rust')
box('staff', (0, 0, 1.65), (.17, .12, 3.16), 'cream')
for i in range(1, 13):
    z = i * .25
    box('quarter_meter_mark', (-.02, -.067, z), (.12 if i % 2 == 0 else .075, .016, .025), 'dark', .002)
box('high_water_band', (0, -.07, 2.5), (.19, .018, .08), 'red')
box('sensor', (.2, 0, 1.4), (.26, .23, .48), 'teal')
dial(.2, -.13, 1.49)
pipe('conduit', [(.2, .13, 1.4), (.2, .14, .27), (0, .14, .27)], .021, 'steel')
box('warning_flag', (.19, 0, 3.08), (.35, .022, .2), 'gold')

start('signal_beacon', [1, 1], 'Braced survey beacon, 3.6 m tall; fixed antenna and amber lens.')
box('plinth', (0, 0, .09), (1, 1, .18), 'steel')
for x in [-.36, .36]:
    pipe('mast_leg', [(x, -.3, .18), (0, 0, 2.75)], .04, 'rust')
pipe('mast_leg', [(0, .36, .18), (0, 0, 2.75)], .04, 'rust')
for z, width in [(.6, .3), (1.2, .21), (1.8, .12)]:
    pipe('crossbrace', [(-width, -.22, z), (width, -.12, z+.35)], .025, 'edge')
box('junction_box', (0, -.23, .6), (.34, .22, .46), 'teal')
cyl('lens', (0, 0, 2.75), (0, 0, 3.02), .16, 'lamp', 12)
for z in [2.72, 3.03]:
    cyl('lens_cap', (0, 0, z), (0, 0, z+.05), .21, 'steel', 12)
cyl('antenna', (0, 0, 3.08), (0, 0, 3.6), .018, 'edge', 8)
pipe('cross_aerial', [(-.42, 0, 3.4), (.42, 0, 3.4)], .018, 'edge')

start('salvage_winch', [1, 1], 'Deck-mounted winch with cable drum and parked hook; static.',
      [('cable_exit', (0, -.45, .5), (0, -1, 0))])
box('skid', (0, 0, .08), (1, 1, .16), 'steel')
for x in [-.35, .35]:
    box('bearing_tower', (x, 0, .39), (.12, .6, .62), 'teal')
    cyl('drum_flange', (x-.035, 0, .53), (x+.035, 0, .53), .32, 'rust', 16)
cyl('drum', (-.3, 0, .53), (.3, 0, .53), .235, 'rubber', 16)
for x in [-.24, -.16, -.08, 0, .08, .16, .24]:
    cyl('cable_coil', (x-.014, 0, .53), (x+.014, 0, .53), .25, 'edge', 16)
cyl('drive_motor', (.41, .18, .34), (.48, .18, .34), .18, 'gold', 12)
pipe('cable', [(0, -.18, .69), (0, -.4, .48), (0, -.43, .2)], .022, 'edge')
pipe('hook', [(0, -.43, .2), (.09, -.43, .15), (.13, -.43, .23)], .03, 'gold')
for x in [-.4, .4]:
    for y in [-.4, .4]:
        cyl('mount_bolt', (x, y, .16), (x, y, .19), .034, 'gold', 8)

start('fuel_drum', [.6, .6], 'Sealed, patched 200-liter-style fuel drum; ground-center pivot.')
cyl('barrel', (0, 0, .025), (0, 0, .88), .28, 'rust', 16)
for z in [.04, .25, .65, .86]:
    cyl('hoop', (0, 0, z), (0, 0, z+.035), .294, 'edge', 16)
cyl('cap', (.13, 0, .885), (.13, 0, .915), .045, 'gold', 10)
box('label', (0, -.278, .47), (.22, .025, .2), 'cream')
box('fuel_mark', (0, -.295, .47), (.1, .008, .1), 'red', .002, math.pi/4)

start('battery_pack', [.5, .5], 'Carryable power-cell pack; electrical terminals are decorative.',
      [('carry', (0, 0, .48), (0, 0, 1))])
box('case', (0, 0, .18), (.44, .32, .36), 'teal', .025)
box('lid', (0, 0, .37), (.47, .35, .06), 'steel')
for x, mat in [(-.15, 'red'), (.15, 'dark')]:
    cyl('terminal', (x, 0, .4), (x, 0, .45), .03, mat, 10)
pipe('handle', [(-.09, .08, .4), (-.09, .08, .49), (.09, .08, .49), (.09, .08, .4)], .018, 'gold')
box('label', (0, -.165, .21), (.27, .018, .17), 'cream')
for x in [-.08, 0, .08]:
    box('charge_bar', (x, -.177, .21), (.035, .008, .07), 'gold', .003)

start('water_pump', [1, .75], 'Recoverable motor-driven pump; inlet and outlet sockets.',
      [('inlet', (-.42, 0, .36), (-1, 0, 0)), ('outlet', (-.16, 0, .8), (0, 0, 1))])
box('skid', (0, 0, .06), (.95, .65, .12), 'steel')
cyl('motor', (.05, 0, .35), (.4, 0, .35), .21, 'teal', 16)
for x in [.09, .16, .23, .3, .37]:
    cyl('fin', (x, 0, .35), (x+.02, 0, .35), .225, 'edge', 16)
cyl('pump_body', (-.3, 0, .36), (.02, 0, .36), .25, 'rust', 16)
pipe('inlet', [(-.42, 0, .36), (-.28, 0, .36)], .095, 'edge')
pipe('outlet', [(-.16, 0, .5), (-.16, 0, .8)], .07, 'edge')
cyl('flange', (-.16, 0, .76), (-.16, 0, .8), .115, 'gold', 12)
box('switch', (.22, 0, .6), (.2, .18, .12), 'dark')

start('replacement_alternator', [.5, .5], 'Distinct carryable engine repair part, separate from the generator.',
      [('carry', (0, 0, .39), (0, 0, 1))])
box('mounting_feet', (0, 0, .035), (.4, .28, .07), 'rust')
cyl('housing', (0, -.15, .2), (0, .15, .2), .19, 'edge', 12)
for y in [-.13, -.06, .01, .08, .15]:
    cyl('vent_ring', (0, y, .2), (0, y+.02, .2), .2, 'steel', 12)
cyl('pulley', (0, -.21, .2), (0, -.16, .2), .14, 'gold', 12)
cyl('hub', (0, -.23, .2), (0, -.21, .2), .045, 'dark', 8)
pipe('lead', [(.12, .17, .25), (.2, .2, .3), (.22, .12, .32)], .015, 'red')

start('salvage_locker', [.75, .5], 'Closed narrow equipment locker; door is static, not hinged.')
feet(.55, .3, .12)
box('cabinet', (0, 0, .91), (.7, .45, 1.62), 'teal')
box('door', (0, -.24, .91), (.61, .03, 1.5), 'cream')
for z in [1.42, 1.48, 1.54]:
    box('vent', (0, -.261, z), (.36, .01, .025), 'dark', .002)
pipe('handle', [(.22, -.27, .8), (.22, -.31, .8), (.22, -.31, 1), (.22, -.27, 1)], .016, 'gold')
box('repair_patch', (-.11, -.268, .43), (.27, .018, .22), 'rust')

start('cargo_pallet', [1.25, 1], 'Empty reusable pallet with fork gaps; stack cargo as separate instances.')
for x in [-.46, 0, .46]:
    for y in [-.35, .35]:
        box('block', (x, y, .09), (.16, .18, .18), 'wood')
for x in [-.48, -.24, 0, .24, .48]:
    box('deck_plank', (x, 0, .2), (.21, .98, .07), 'woodlight')
for x in [-.46, 0, .46]:
    box('runner', (x, 0, .025), (.17, .98, .05), 'wood')

start('wreck_rib_2m', [2, 1], 'Reusable U-shaped stranded-hull bay; joins every 1 m along Y.')
box('keel', (0, 0, .12), (1.3, 1, .24), 'rust')
for x in [-.47, -.235, 0, .235, .47]:
    box('deck_board', (x, 0, .25), (.21, .96, .045), 'wood')
for side in [-1, 1]:
    pipe('rib', [(side*.55, 0, .15), (side*.82, 0, .55), (side*.95, 0, 1.3)], .065, 'edge')
    for z, x in [(.5, .79), (.86, .88), (1.2, .94)]:
        box('hull_strake', (side*x, 0, z), (.075, 1, .25), 'teal' if z == .86 else 'rust')
    for y in [-.36, .36]:
        cyl('bolt', (side*.985, y, 1.2), (side*1.0, y, 1.2), .026, 'gold', 8)

start('wreck_bulkhead_2m', [2, .25], 'Walk-through bulkhead with 0.9 m clear opening; modular wreck end.')
for x in [-.72, .72]:
    box('side', (x, 0, .91), (.54, .18, 1.82), 'teal')
    box('rust_patch', (x, -.103, .55), (.37, .025, .5), 'rust')
box('lintel', (0, 0, 1.91), (2, .22, .18), 'rust')
for x in [-.47, .47]:
    box('door_frame', (x, -.02, .91), (.035, .26, 1.82), 'gold')
box('frame_top', (0, -.02, 1.8), (.95, .26, .04), 'gold')

start('supply_shelf', [1.25, .5], 'Open domestic shelf with tins, folded blankets and books.')
feet(1.12, .36, 1.65)
for z in [.15, .7, 1.25, 1.65]:
    box('shelf', (0, 0, z), (1.24, .5, .05), 'woodlight')
for x in [-.4, -.17, .08]:
    cyl('tin', (x, 0, .73), (x, 0, .99), .075, 'cream' if x < 0 else 'red', 10)
    cyl('tin_lid', (x, 0, .99), (x, 0, 1.01), .08, 'edge', 10)
for z in [.23, .32, .41]:
    box('blanket', (-.23, 0, z), (.6, .43, .085), 'linen', .025)
for i, mat in enumerate(['red', 'teal', 'cream', 'gold']):
    box('book', (-.42+i*.095, .04, 1.43), (.075, .29, .3), mat, .006)
box('personal_box', (.28, 0, 1.41), (.32, .36, .26), 'rust')

start('floodlight', [.75, .75], 'Tripod work light; emissive lens, no runtime light component.')
for a in [0, 2*math.pi/3, 4*math.pi/3]:
    pipe('tripod_leg', [(math.cos(a)*.34, math.sin(a)*.34, .025), (0, 0, .8)], .032, 'steel')
cyl('mast', (0, 0, .55), (0, 0, 1.85), .03, 'gold', 10)
box('housing', (0, 0, 1.92), (.55, .19, .34), 'steel')
box('reflector', (0, -.103, 1.92), (.46, .025, .25), 'cream')
box('lens', (0, -.12, 1.92), (.39, .01, .19), 'lamp', .004)
for x in [-.2, .2]:
    pipe('guard', [(x, -.14, 1.79), (x, -.14, 2.05)], .009, 'gold')
