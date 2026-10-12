asset('cargo_rack', [1.0, .6], 'Deck-mounted three-slot cargo rack with tie-down straps; slot labels face -Y.')

# Silhouette: base frame, two end frames, top rail.
box('base_frame', (0, 0, .04), (1.0, .6, .08), 'rust')
for x in [-.47, .47]:
    box('end_frame', (x, 0, .42), (.06, .56, .7), 'steel')
box('top_rail', (0, .25, .76), (1.0, .06, .06), 'steel')

# Structure: slot dividers, back panel, shelf floor slats.
for x in [-.16, .16]:
    box('divider', (x, .04, .34), (.04, .48, .52), 'edge', .008)
box('back_panel', (0, .27, .42), (.88, .03, .64), 'teal', .01)
for y in [-.18, -.06, .06, .18]:
    box('floor_slat', (0, y, .1), (.88, .09, .03), 'woodlight', .004)

# Detail: straps over each slot, buckles, slot plates and bolts on the front.
for x in [-.31, 0, .31]:
    pipe('strap', [(x, -.24, .1), (x, -.24, .58), (x, .24, .74)], .012, 'rubber')
    box('buckle', (x, -.25, .46), (.07, .02, .05), 'gold', .003)
    box('slot_plate', (x, -.305, .045), (.16, .02, .05), 'cream', .003)
for x in [-.47, .47]:
    for z in [.16, .42, .68]:
        cyl('bolt', (x, -.285, z), (x, -.3, z), .014, 'gold', 8)
for x in [-.42, .42]:
    for y in [-.25, .25]:
        cyl('deck_mount', (x, y, 0), (x, y, .085), .028, 'dark', 8)
