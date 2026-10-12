asset('water_purifier', [.9, .6], 'Deck-mounted seawater purifier; tap, gauge and hand pump face -Y.')
# Silhouette
box('deck_skid', (0, 0, .055), (.86, .56, .11), 'rust', .015)
cyl('collection_tank', (-.19, .055, .15), (-.19, .055, .92), .225, 'teal', 16)
cyl('filter_column', (.285, .105, .17), (.285, .105, 1.16), .105, 'steel', 12)
# Structure
for z in [.19, .77, .9]:
    cyl('tank_hoop', (-.19, .055, z), (-.19, .055, z+.035), .238, 'edge', 16)
cyl('tank_lid', (-.19, .055, .92), (-.19, .055, .985), .215, 'steel', 16)
cyl('filter_cap', (.285, .105, 1.16), (.285, .105, 1.215), .128, 'teal', 12)
cyl('filter_foot', (.285, .105, .12), (.285, .105, .19), .135, 'rust', 12)
pipe('transfer_pipe', [(.025, .12, .69), (.13, .12, .69), (.13, .105, .94), (.285, .105, .94)], .025, 'edge')
pipe('feed_pipe', [(-.32, -.13, .96), (-.32, -.13, 1.08), (-.11, -.13, 1.08)], .023, 'steel')
box('hand_pump_body', (-.11, -.2, 1.07), (.19, .12, .17), 'rust', .012)
pipe('pump_handle', [(-.11, -.22, 1.14), (-.11, -.25, 1.31), (-.27, -.25, 1.31)], .016, 'gold')
pipe('outlet_line', [(.285, -.01, .62), (.285, -.23, .62), (.32, -.23, .52)], .023, 'edge')
cyl('outlet_tap', (.32, -.23, .52), (.32, -.28, .52), .038, 'gold', 10)
box('drip_tray', (.29, -.175, .16), (.27, .2, .045), 'steel', .008)
box('tray_well', (.29, -.178, .185), (.21, .14, .008), 'dark', .002)
# Detail
cyl('gauge_rim', (.285, -.028, .82), (.285, -.07, .82), .074, 'gold', 12)
cyl('gauge_face', (.285, -.072, .82), (.285, -.079, .82), .057, 'cream', 12)
pipe('gauge_needle', [(.285, -.087, .82), (.307, -.087, .846)], .006, 'dark')
box('maintenance_label', (-.19, -.177, .5), (.23, .018, .16), 'cream', .003)
box('label_stripe', (-.19, -.19, .5), (.15, .009, .035), 'dark', .002)
box('tank_patch', (-.24, -.172, .32), (.15, .021, .105), 'steel', .004)
for x in [-.29, -.19]:
    cyl('patch_rivet', (x, -.19, .32), (x, -.205, .32), .012, 'gold', 6)
for x in [-.34, .34]:
    for y in [-.21, .21]:
        cyl('mount_bolt', (x, y, .11), (x, y, .133), .02, 'gold', 6)
pipe('tap_handle', [(.32, -.26, .55), (.32, -.26, .61)], .013, 'gold')
box('filter_service_band', (.285, -.004, 1.02), (.15, .018, .045), 'cream', .002)
