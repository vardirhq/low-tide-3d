asset('crawler_galley', [1.05, .6], 'Compact crawler cooking station; burner, controls and storage face -Y.')
# Silhouette
box('galley_cabinet', (0, .035, .39), (1.0, .52, .78), 'teal', .025)
box('countertop', (0, .015, .805), (1.04, .57, .055), 'steel', .012)
box('backsplash', (0, .265, 1.035), (1.0, .045, .43), 'rust', .012)
# Structure
box('stove_plate', (-.245, -.045, .846), (.39, .35, .025), 'dark', .008)
for x in [-.35, -.14]:
    cyl('burner_ring', (x, -.045, .86), (x, -.045, .875), .073, 'edge', 12)
box('sink_basin', (.245, -.035, .85), (.34, .31, .025), 'dark', .008)
box('sink_rim', (.245, -.035, .865), (.37, .34, .018), 'steel', .006)
pipe('faucet', [(.36, .065, .83), (.36, .065, 1.02), (.245, .065, 1.02), (.245, -.025, .98)], .016, 'gold')
box('cabinet_left_door', (-.245, -.235, .4), (.44, .018, .59), 'steel', .01)
box('cabinet_right_door', (.245, -.235, .4), (.44, .018, .59), 'teal', .01)
box('storage_lip', (0, -.23, .115), (.95, .035, .05), 'rust', .008)
box('upper_shelf', (0, .225, 1.16), (.87, .19, .04), 'woodlight', .008)
# Detail
for x in [-.35, -.14]:
    cyl('control_knob', (x, -.29, .72), (x, -.315, .72), .031, 'gold', 10)
for x in [-.085, .405]:
    box('door_pull', (x, -.255, .47), (.018, .03, .12), 'gold', .004)
cyl('kettle_body', (-.24, .19, 1.1805), (-.24, .19, 1.3305), .083, 'steel', 12)
cyl('kettle_lid', (-.24, .19, 1.3305), (-.24, .19, 1.3455), .065, 'dark', 10)
pipe('kettle_handle', [(-.32, .19, 1.31), (-.34, .19, 1.42), (-.14, .19, 1.42), (-.16, .19, 1.31)], .012, 'gold')
box('folded_cloth', (.13, .19, 1.193), (.22, .13, .025), 'linen', .006)
box('patched_backsplash', (.27, .235, 1.01), (.18, .018, .14), 'steel', .004)
for x in [.215, .325]:
    cyl('patch_rivet', (x, .22, 1.01), (x, .208, 1.01), .012, 'gold', 6)
for x in [-.43, .43]:
    box('mount_foot', (x, -.16, .035), (.1, .15, .07), 'rust', .008)
