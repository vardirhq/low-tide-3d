"""Conservative collision recipes, intentionally separate from render GLBs."""
from build_kit import *
out={}
def bounds(parts):
 v=np.concatenate([p['v'] for p in parts]);lo=v.min(0);hi=v.max(0)
 return {'type':'box','center':((lo+hi)/2).tolist(),'size':(hi-lo).tolist()}
for name,a in K.items():
 parts=a['parts'];shapes=[]
 if name in ['rug','lamp','antenna','vent','exhaust_stack']:pass
 elif name=='ramp':shapes=[{'type':'convex_hull','vertices':parts[0]['v'].tolist()}]
 elif name in ['doorway_1m','window_upper_1m']:
  shapes=[bounds([p]) for p in parts if p['name'] in ['jamb','header','lintel','mullion']]
 elif name=='floor_1m':shapes=[{'type':'box','center':[0,0,-.2],'size':[1,1,.4]}]
 elif name=='track_bogie_3m':shapes=[{'type':'box','center':[0,0,.56],'size':[.74,2.96,1.12]}]
 else:shapes=[bounds(parts)]
 out[name]={'shapes':shapes,'note':'Conservative prototype collision; hidden visual groups must retain collision.'}
(P/'collision_recipes.json').write_text(json.dumps({'axes':'Source Z-up meters. Convert vectors (x,y,z) to glTF (x,z,-y); box extents (x,z,y).','policy':'Child colliders of one crawler body, not independent dynamic bodies. Decorative props omitted. Not loaded into GLB automatically.','modules':out},indent=2))
