asset('salvage_workbench', [1.25, .65], 'Crawler salvage repair bench; vise, tools and sorting bins face -Y.')
# Silhouette
for x in [-.53, .53]:
    box('steel_leg', (x, 0, .4), (.075, .47, .8), 'steel')
box('worktop', (0, 0, .825), (1.23, .62, .07), 'woodlight', .02)
box('rear_toolboard', (0, .265, 1.12), (1.16, .045, .51), 'teal', .015)
# Structure
box('lower_shelf', (0, 0, .22), (1.1, .44, .045), 'rust')
box('front_brace', (0, -.215, .52), (1.08, .045, .065), 'edge')
box('vise_base', (-.38, -.19, .89), (.23, .19, .07), 'steel')
box('vise_fixed_jaw', (-.38, -.275, .97), (.21, .055, .11), 'dark', .005)
box('vise_moving_jaw', (-.38, -.105, .965), (.21, .055, .11), 'steel', .005)
cyl('vise_screw', (-.38, -.14, .94), (-.38, .07, .94), .025, 'edge', 10)
box('vise_screw_support', (-.38, .045, .895), (.065, .065, .075), 'steel', .006)
pipe('vise_handle', [(-.48, .07, .94), (-.28, .07, .94)], .015, 'gold')
box('sorting_bin_left', (.27, .05, .89), (.21, .27, .08), 'rust', .006)
box('sorting_bin_right', (.49, .055, .9), (.17, .25, .07), 'steel', .006)
box('tool_rail', (0, .226, 1.29), (.98, .045, .045), 'edge')
# Detail
for x in [-.43, -.21, .02, .24]:
    pipe('hanging_tool', [(x, .19, 1.27), (x, .19, 1.08)], .014, 'gold' if x == -.21 else 'dark')
for x in [-.4, -.17, .07]:
    box('peg_hook', (x, .186, 1.36), (.055, .12, .018), 'gold', .003)
box('patched_toolboard', (.4, .233, 1.08), (.19, .014, .14), 'rust', .003)
for x in [.35, .45]:
    cyl('patch_rivet', (x, .239, 1.08), (x, .204, 1.08), .012, 'gold', 6)
box('worktop_cutting_plate', (.03, -.09, .868), (.25, .24, .012), 'steel', .003)
for x in [-.48, .48]:
    box('shelf_crate', (x, 0, .345), (.2, .32, .21), 'wood', .01)
for x in [-.53, .53]:
    cyl('anchor_bolt', (x, -.19, .04), (x, -.19, .065), .022, 'gold', 6)
