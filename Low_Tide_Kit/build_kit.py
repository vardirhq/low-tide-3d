"""Low Tide modular prototype. Python 3 + numpy + scipy. No Blender required.
Source uses meters, X right, Y forward, Z up. GLB exports X right, Y up, -Z forward.
Run this script to rebuild all GLBs and the manifest beside it.
"""
import json, struct, math, pathlib
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
P=pathlib.Path(__file__).resolve().parent
(P/'modules').mkdir(exist_ok=True)
M={
 'steel':('#34474b',.65,.7), 'teal':('#527f7b',.45,.72),
 'rust':('#a65537',.35,.92), 'edge':('#647374',.65,.58),
 'rubber':('#20282a',0,.96), 'wood':('#9d704a',0,.88),
 'woodlight':('#bc9160',0,.86), 'cream':('#d9ccaa',0,.8),
 'red':('#9b4d39',0,.9), 'gold':('#d4a34c',.4,.62),
 'dark':('#172b30',.2,.75), 'blue':('#5e8d9b',.25,.6),
 'lamp':('#ffd28a',0,.4), 'screen':('#9ccab3',0,.45),
 'linen':('#b2baa0',0,1), 'paper':('#e0d5b1',0,1)}
K={}; cur=None
def begin(name,footprint,description,sockets=None):
 global cur
 cur={'id':name,'footprint_m':footprint,'description':description,'parts':[], 'sockets':sockets or []};K[name]=cur
def mesh(name,v,f,mat):cur['parts'].append({'name':name,'v':np.array(v,float),'f':np.array(f,int),'mat':mat})
def box(name,loc,size,mat,bevel=.015,rot=0):
 s=np.array(size)/2;b=min(bevel,float(min(s))*.4)
 if b:
  vs=[]
  for axis in range(3):
   for signs in np.ndindex(2,2,2):
    p=(s-b)*(np.array(signs)*2-1);p[axis]=s[axis]*(signs[axis]*2-1);vs.append(p)
  vs=np.unique(vs,axis=0); hull=ConvexHull(vs); fs=hull.simplices.copy()
  for i,f in enumerate(fs):
   if np.dot(np.cross(vs[f[1]]-vs[f[0]],vs[f[2]]-vs[f[0]]),hull.equations[i,:3])<0:fs[i]=f[::-1]
 else:
  vs=np.array([[x,y,z] for x in [-s[0],s[0]] for y in [-s[1],s[1]] for z in [-s[2],s[2]]]);h=ConvexHull(vs);fs=h.simplices.copy()
  for i,f in enumerate(fs):
   if np.dot(np.cross(vs[f[1]]-vs[f[0]],vs[f[2]]-vs[f[0]]),h.equations[i,:3])<0:fs[i]=f[::-1]
 c,t=math.cos(rot),math.sin(rot);vs=vs@np.array([[c,t,0],[-t,c,0],[0,0,1]])+loc;mesh(name,vs,fs,mat)
def cyl(name,a,b,r,mat,n=12,r2=None):
 a=np.array(a,float);b=np.array(b,float);w=b-a;w/=np.linalg.norm(w)
 u=np.cross(w,[0,0,1] if abs(w[2])<.9 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(w,u)
 vs=[p+rr*(math.cos(i*2*math.pi/n)*u+math.sin(i*2*math.pi/n)*v) for p,rr in [(a,r),(b,r if r2 is None else r2)] for i in range(n)]+[a,b]
 fs=[]
 for i in range(n):
  j=(i+1)%n;fs.extend([(i,j,n+j),(i,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)])
 mesh(name,vs,fs,mat)
def pipe(name,pts,r,mat):
 for i in range(len(pts)-1):cyl(name+str(i),pts[i],pts[i+1],r,mat,10)
def socket(name,pos,normal):return {'name':name,'position':pos,'normal':normal,'standard':'LT_mount_025','load_rating':'prototype_unrated'}
def bolts(y,z):
 for x in [-.36,.36]:cyl('rivet',(x,y-.012,z),(x,y+.012,z),.018,'gold',8)

begin('floor_1m',[1,1],'Deck top at local Z=0; cell pivot at center of walking surface.',
 [socket('edge_'+n,p,v) for n,p,v in [('E',[.5,0,-.12],[1,0,0]),('W',[-.5,0,-.12],[-1,0,0]),('N',[0,.5,-.12],[0,1,0]),('S',[0,-.5,-.12],[0,-1,0])]])
box('chassis',(0,0,-.17),(1,1,.28),'steel')
for i in range(5):
 box('plank',(-.4+i*.2,0,-.018),(.192,.984,.036),'woodlight' if i%3==0 else 'wood',.004)
 for y in [-.42,.42]:cyl('nail',(-.4+i*.2,y,0),(-.4+i*.2,y,.004),.009,'dark',6)
for x in [-.43,.43]:box('underbeam',(x,0,-.35),(.12,1,.16),'rust')

begin('wall_low_1m',[1,.12],'Lower wall; local +Y is exterior; endpoints X +/-0.5.',[socket('equipment',[0,.105,.65],[0,1,0])])
box('panel',(0,0,.43),(.9,.12,.86),'teal')
box('kickplate',(0,.075,.16),(.88,.03,.26),'rust')
box('cap',(0,0,.88),(.92,.19,.08),'edge')
box('patch',(.15,.079,.54),(.29,.025,.25),'rust',.004, .08)
for z in [.16,.68]:bolts(.08,z)
box('interior_board',(0,-.074,.46),(.88,.024,.46),'wood')

begin('wall_upper_1m',[1,.12],'Removable upper wall, pivot remains at deck level. Full height 2.2 m.')
box('upper',(0,0,1.55),(.9,.12,1.26),'teal')
box('rim',(0,0,2.18),(.92,.18,.08),'edge')
for x in [-.35,.35]:box('strap',(x,.077,1.52),(.05,.025,1.15),'rust')

begin('window_upper_1m',[1,.12],'Open window aperture, no transparent sorting dependency.')
for x in [-.39,.39]:box('jamb',(x,0,1.56),(.12,.16,1.28),'cream')
for z in [.99,2.13]:box('lintel',(0,0,z),(.88,.17,.13),'cream')
box('mullion',(0,0,1.56),(.045,.09,1.0),'steel')
box('awning',(0,.16,2.2),(1,.44,.07),'rust')

begin('corner_post',[.1,.1],'Shared junction post fills 0.1 m gap between adjacent wall spans.')
box('post',(0,0,.46),(.1,.1,.92),'rust')
box('cap',(0,0,.94),(.14,.14,.04),'gold')
begin('corner_upper',[.1,.1],'Removable upper portion of shared corner/junction post.')
box('post',(0,0,1.56),(.1,.1,1.28),'rust')

begin('doorway_1m',[1,.18],'0.82 m clear doorway, 2.05 m clear headroom; no threshold collider.')
for x in [-.455,.455]:box('jamb',(x,0,1.06),(.09,.18,2.12),'cream')
box('header',(0,0,2.12),(1,.18,.14),'rust')
box('threshold',(0,0,-.015),(.82,.24,.03),'edge')

begin('roof_1m',[1,1],'Removable roof tile; pivot on deck; underside at 2.22 m.')
box('roof',(0,0,2.26),(1,1,.08),'teal')
for x in [-.4,-.2,0,.2,.4]:box('seam',(x,0,2.312),(.045,1,.04),'edge',.004)

begin('track_bogie_3m',[.72,3],'Self-contained 3 m tracked bogie; pivot at ground beneath center. Wheel axles local X.',[socket('chassis',[0,0,1.1],[0,0,1])])
box('suspension',(0,0,.72),(.46,2.6,.24),'steel')
for y in [-1.02,-.51,0,.51,1.02]:
 cyl('wheel_tire',(-.30,y,.50),(.30,y,.50),.37,'rubber',16)
 for side in [-1,1]:
  cyl('wheel_hub',(.305*side,y,.5),(.335*side,y,.5),.24,'rust',12)
  cyl('axle',(.34*side,y,.5),(.36*side,y,.5),.09,'gold',10)
  pipe('spring',[(.17*side,y-.2,.92),(.17*side,y,.53)],.055,'edge')
# Continuous capsule belt built from tread shoes; separated per bogie by design.
r=.45; half=1.0; L=4*half+2*math.pi*r; count=48
for i in range(count):
 d=i*L/count
 if d<2*half:y=-half+d;z=.5+r;ang=0
 elif d<2*half+math.pi*r:
  a=(d-2*half)/r;y=half+r*math.sin(a);z=.5+r*math.cos(a);ang=-a
 elif d<4*half+math.pi*r:y=half-(d-2*half-math.pi*r);z=.5-r;ang=math.pi
 else:
  a=(d-4*half-math.pi*r)/r;y=-half-r*math.sin(a);z=.5-r*math.cos(a);ang=math.pi-a
 # Box long axis local Y, rotate around X using tangent dy/ds,dz/ds.
 before=len(cur['parts']);box('tread',(0,0,0),(.74,L/count*.91,.09),'steel',.009)
 part=cur['parts'][-1];c,s=math.cos(ang),math.sin(ang);part['v']=part['v']@np.array([[1,0,0],[0,c,s],[0,-s,c]])+[0,y,z]
box('mount',(0,0,1.0),(.35,1.8,.25),'rust')

begin('helm',[1,.75],'Console front faces local +Y; operator stands at -Y.',[socket('operator',[0,-.7,0],[0,1,0])])
box('pedestal',(0,0,.45),(.64,.43,.9),'teal',.035)
box('desk',(0,0,.94),(.96,.68,.12),'edge',.025)
box('instrument',(0,.18,1.16),(.8,.18,.35),'dark')
for x in [-.24,0,.24]:
 cyl('gauge',(x,.074,1.17),(x,.065,1.17),.083,'cream',16)
 pipe('needle',[(x,.054,1.17),(x+.033,.054,1.215)],.007,'red')
for x in [-.3,.3]:
 cyl('lever',(x,-.14,1),(x,-.26,1.25),.018,'edge')
 cyl('grip',(x-.045,-.26,1.25),(x+.045,-.26,1.25),.036,'rust')
box('map',(-.08,-.12,1.008),(.26,.22,.008),'paper',0)
box('screen',(.28,.066,1.35),(.18,.018,.07),'screen')

begin('engine',[1,1.5],'Engine skid with exposed cylinders, exhaust and removable service space.')
box('skid',(0,0,.09),(.95,1.45,.18),'steel')
box('block',(0,0,.43),(.62,1.08,.56),'rust',.04)
for y in [-.35,0,.35]:
 cyl('cylinder',(-.27,y,.65),(.27,y,.65),.18,'edge',12)
 for z in [.7,.76,.82]:box('cooling_fin',(0,y,z),(.58,.23,.025),'dark',.004)
pipe('manifold',[(.39,-.48,.43),(.39,.52,.43),(.39,.52,1.4),(.55,.52,1.4)],.065,'steel')
cyl('generator',(0,-.56,.46),(0,-.72,.46),.27,'teal',16)
box('service_label',(-.322,0,.48),(.018,.35,.15),'gold')
for y in [-.46,.46]:pipe('hose',[(-.35,y,.25),(-.42,y,.42),(-.38,y,.7)],.026,'rubber')

begin('bed',[.85,2],'Single bed; feet at -Y, head at +Y.')
for x in [-.32,.32]:
 for y in [-.85,.85]:box('leg',(x,y,.22),(.1,.1,.44),'steel')
box('frame',(0,0,.4),(.85,2,.16),'wood')
box('mattress',(0,0,.55),(.79,1.94,.19),'cream',.04)
box('blanket',(0,-.28,.663),(.81,1.25,.06),'linen')
for y in [-.72,-.65]:box('woven_stripe',(0,y,.698),(.81,.027,.008),'red',0)
box('pillow',(0,.7,.7),(.59,.37,.13),'cream',.04)
box('headboard',(0,.95,.64),(.85,.08,.58),'wood')

begin('workbench',[1.35,.6],'Bench front faces -Y.')
for x in [-.56,.56]:
 for y in [-.22,.22]:box('leg',(x,y,.43),(.08,.08,.86),'steel')
box('worktop',(0,0,.87),(1.35,.6,.09),'woodlight')
box('shelf',(0,0,.25),(1.22,.5,.055),'wood')
box('toolboard',(0,.275,1.2),(1.25,.055,.53),'teal')
for x in [-.43,-.23,.04,.26]:
 cyl('tool_handle',(x,.227,1.1),(x,.227,1.32),.018,'gold',8)
 box('tool_head',(x,.227,1.33),(.09,.035,.04),'edge')
box('vise',(.4,-.1,1),(.18,.22,.17),'rust')
box('parts_bin',(-.4,.02,.98),(.3,.25,.15),'dark')

begin('kitchen',[1.25,.55],'Compact cabinet, sink and single burner; front faces -Y.')
box('cabinet',(0,0,.43),(1.25,.55,.86),'cream')
for x in [-.31,.31]:
 box('door',(x,-.286,.45),(.57,.025,.66),'teal')
 box('pull',(x,-.32,.64),(.16,.045,.035),'gold')
box('counter',(0,0,.9),(1.3,.6,.08),'woodlight')
box('sink',(-.3,0,.945),(.45,.38,.025),'steel')
box('basin',(-.3,0,.96),(.35,.28,.014),'dark')
pipe('tap',[(-.3,.18,.95),(-.3,.18,1.2),(-.3,.02,1.2)],.02,'edge')
cyl('burner',(.31,0,.94),(.31,0,.965),.16,'dark',16)
cyl('pot',(.31,0,.97),(.31,0,1.13),.105,'rust',12)
cyl('lid',(.31,0,1.13),(.31,0,1.15),.115,'edge',12)

begin('crate',[.5,.5],'Stackable cargo crate, bottom-center pivot.')
box('body',(0,0,.24),(.49,.49,.48),'wood')
for z in [.07,.4]:
 for y in [-.25,.25]:box('band',(0,y,z),(.51,.03,.07),'edge',.004)
for x in [-.18,.18]:box('strap',(x,0,.489),(.045,.5,.018),'steel',.004)
box('label',(0,-.269,.23),(.21,.006,.14),'paper',0)

begin('stool',[.45,.45],'Small helm stool.')
for x,y in [(-.15,-.15),(.15,-.15),(-.15,.15),(.15,.15)]:box('leg',(x,y,.22),(.045,.045,.44),'steel')
box('seat',(0,0,.47),(.43,.43,.1),'red',.04)

begin('rug',[1,1.5],'Thin woven rug; decorative, not collision.')
box('rug',(0,0,.008),(1,1.5,.016),'red',0)
for x in [-.44,.44]:box('border',(x,0,.018),(.055,1.4,.006),'gold',0)
for y in [-.66,.66]:box('border',(0,y,.018),(.92,.055,.006),'gold',0)
for y in [-.4,0,.4]:box('motif',(0,y,.023),(.2,.2,.004),'cream',0,math.pi/4)

begin('tank',[.65,1],'Exterior horizontal tank; pivot is mounting base.',[socket('mount',[0,0,0],[0,0,-1])])
for y in [-.32,.32]:box('cradle',(0,y,.12),(.6,.12,.24),'steel')
cyl('tank',(0,-.46,.41),(0,.46,.41),.3,'blue',16)
for y in [-.31,.31]:cyl('band',(0,y-.025,.41),(0,y+.025,.41),.312,'edge',16)
cyl('cap',(0,0,.7),(0,0,.77),.075,'gold',10)
pipe('outlet',[(0,-.5,.4),(0,-.6,.4),(0,-.6,.18)],.035,'rust')

begin('lamp',[.2,.25],'Warm wall lamp, back toward +Y.')
box('bracket',(0,.05,.12),(.12,.09,.24),'steel')
cyl('glass',(0,-.045,.05),(0,-.045,.23),.065,'lamp',10)
for z in [.04,.24]:cyl('cage',(0,-.045,z),(0,-.045,z+.02),.09,'gold',10)
for x in [-.065,.065]:cyl('guard',(x,-.08,.05),(x,-.08,.24),.009,'gold',8)

begin('interior_partition_1m',[1,.1],'Low engine-room bulkhead; distinct from exterior panels.')
box('panel',(0,0,.43),(.98,.1,.86),'steel')
for x in [-.36,-.12,.12,.36]:box('wood_inset',(x,-.057,.43),(.22,.018,.62),'wood')
box('rail',(0,0,.9),(1,.14,.07),'gold')
for x in [-.35,-.175,0,.175,.35]:box('vent',(x,.058,.5),(.08,.017,.3),'dark',.004)

begin('vent',[.5,.16],'Bolt-on exterior vent; back at local Y=0, faces +Y.')
box('housing',(0,.06,.22),(.48,.12,.44),'rust')
for z in [.08,.15,.22,.29,.36]:box('louver',(0,.135,z),(.38,.07,.035),'steel',.005)

begin('antenna',[.3,.3],'Socket accessory; bottom pivot.')
box('base',(0,0,.055),(.25,.25,.11),'rust')
cyl('mast',(0,0,.1),(0,0,1.4),.023,'edge',10)
pipe('aerial',[(-.35,0,1.15),(.35,0,1.15)],.014,'edge')

begin('exhaust_stack',[.55,.22],'External engine exhaust continuation; inlet pivot; local +X outward.')
pipe('exhaust',[(0,0,0),(.3,0,0),(.3,0,1.15),(.45,0,1.15)],.065,'rust')
cyl('muffler',(.3,0,.3),(.3,0,.8),.11,'steel',12)
for z in [.34,.75]:cyl('strap',(.3,0,z),(.3,0,z+.045),.12,'gold',12)

begin('ramp',[.82,2.75],'Hinge pivot at top; extends local -Y 2.75 m, drops 1.25 m. 24.4 degree slope.')
# Sloped plate constructed directly, with nonslip cross strips.
v=[(x,y,z) for x in [-.41,.41] for y,z in [(0,0),(-2.75,-1.25),(0,-.075),(-2.75,-1.325)]]
h=ConvexHull(v); f=h.simplices.copy();v=np.array(v)
for i,face in enumerate(f):
 if np.dot(np.cross(v[face[1]]-v[face[0]],v[face[2]]-v[face[0]]),h.equations[i,:3])<0:f[i]=face[::-1]
mesh('plate',v,f,'steel')
for j in range(11):
 y=-.12-j*.25;box('grip',(0,y,y*1.25/2.75+.022),(.79,.045,.035),'gold',.003)
cyl('hinge',(-.46,0,0),(.46,0,0),.06,'edge',12)

# Assembly instances, all reference the exact same module mesh definitions.
A=[]
def put(asset,p,angle=0,group='structure'):
 A.append({'name':f'{asset}__{len(A):03d}','asset':asset,'position':list(p),'yaw_degrees':angle,'group':group})
deck=1.25
for x in [-1,0,1]:
 for y in [-2.5,-1.5,-.5,.5,1.5,2.5]:put('floor_1m',(x,y,deck))
for x in [-1.85,1.85]:
 for y in [-1.5,1.5]:put('track_bogie_3m',(x,y,0),group='running_gear')
for x in [-1,0,1]:
 for y,angle in [(-3,180),(3,0)]:
  if y==-3 and x==0:put('doorway_1m',(x,y,deck))
  else:
   put('wall_low_1m',(x,y,deck),angle)
   put('window_upper_1m' if y==3 else 'wall_upper_1m',(x,y,deck),angle,'upper_walls')
for x,angle in [(-1.5,90),(1.5,-90)]:
 for y in [-2.5,-1.5,-.5,.5,1.5,2.5]:
  put('wall_low_1m',(x,y,deck),angle)
  put('window_upper_1m' if y in [-.5,1.5] else 'wall_upper_1m',(x,y,deck),angle,'upper_walls')
for x in [-1.5,1.5]:
 for y in [-3,-2,-1,0,1,2,3]:
  put('corner_post',(x,y,deck));put('corner_upper',(x,y,deck),group='upper_walls')
for x in [-.5,.5]:
 for y in [-3,3]:put('corner_post',(x,y,deck));put('corner_upper',(x,y,deck),group='upper_walls')
for x in [-1,0,1]:
 for y in [-2.5,-1.5,-.5,.5,1.5,2.5]:put('roof_1m',(x,y,deck),group='roof')
put('helm',(0,2.45,deck),group='interior');put('stool',(0,1.75,deck),group='interior')
put('bed',(-.95,.65,deck),group='interior')
put('kitchen',(1.16,.45,deck),-90,'interior')
put('workbench',(-1.13,-1.48,deck),90,'interior')
put('engine',(.95,-1.95,deck),group='interior')
put('interior_partition_1m',(1,-1.03,deck),group='interior')
put('rug',(0,.15,deck),group='interior')
put('crate',(-1.03,-2.55,deck),group='interior');put('crate',(-1.03,-2.55,deck+.48),group='interior')
put('crate',(1.02,1.9,deck),group='interior')
put('ramp',(0,-3,deck),group='access')
put('tank',(1.86,.2,1.13),group='accessories')
put('tank',(-1.86,-.2,1.13),group='accessories')
put('antenna',(-1.4,2.9,deck+2.23),group='roof')
put('vent',(1.58,-2,deck+.28),-90,'accessories')
put('exhaust_stack',(1.5,-1.43,deck+1.4),group='accessories')
for x,y,angle in [(-1.35,.8,90),(1.35,.6,-90),(-1.35,-1.5,90)]:put('lamp',(x,y,deck+.75),angle,'interior')

C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
def export(path,instances):
 doc={'asset':{'version':'2.0','generator':'Low Tide modular kit v0.1'},'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[{'name':'LT_Crawler_Root','children':[]}], 'meshes':[], 'materials':[], 'accessors':[], 'bufferViews':[]};data=bytearray()
 mats=list(M)
 for name,(hexcol,metal,rough) in M.items():
  rgb=[int(hexcol[i:i+2],16)/255 for i in (1,3,5)]
  m={'name':'LT_'+name,'pbrMetallicRoughness':{'baseColorFactor':rgb+[1],'metallicFactor':metal,'roughnessFactor':rough}}
  if name in ['lamp','screen']:m['emissiveFactor']=[v*.45 for v in rgb]
  doc['materials'].append(m)
 def acc(a,typ):
  a=np.asarray(a,dtype='<f4');offset=len(data);data.extend(a.tobytes());doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':34962})
  item={'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':len(a),'type':typ}
  if typ=='VEC3':item.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  doc['accessors'].append(item);return len(doc['accessors'])-1
 used=sorted(set(a['asset'] for a in instances));ids={}
 for name in used:
  prims=[]
  for mat in mats:
   parts=[p for p in K[name]['parts'] if p['mat']==mat]
   if not parts:continue
   verts=np.concatenate([p['v'][p['f']].reshape(-1,3) for p in parts])@C.T
   tris=verts.reshape(-1,3,3);norm=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];norm=np.repeat(norm,3,axis=0)
   prims.append({'attributes':{'POSITION':acc(verts,'VEC3'),'NORMAL':acc(norm,'VEC3')},'material':mats.index(mat)})
  ids[name]=len(doc['meshes']);doc['meshes'].append({'name':name,'primitives':prims})
 for a in instances:
  theta=math.radians(a['yaw_degrees']);node={'name':a['name'],'mesh':ids[a['asset']], 'translation':(C@a['position']).tolist(),'rotation':[0,math.sin(theta/2),0,math.cos(theta/2)],'extras':{'asset_id':a['asset'],'visibility_group':a['group']},'children':[]}
  idx=len(doc['nodes']);doc['nodes'].append(node);doc['nodes'][0]['children'].append(idx)
  for s in K[a['asset']]['sockets']:
   forward=C@s['normal'];up=np.array([0.,1.,0.])
   if abs(np.dot(up,forward))>.9:up=np.array([0.,0.,-1.])
   right=np.cross(up,forward);right/=np.linalg.norm(right);up=np.cross(forward,right)
   quat=Rotation.from_matrix(np.column_stack([right,up,forward])).as_quat().tolist()
   doc['nodes'][idx]['children'].append(len(doc['nodes']));doc['nodes'].append({'name':'SOCKET_'+a['name']+'_'+s['name'],'translation':(C@s['position']).tolist(),'rotation':quat,'extras':{'socket_standard':s['standard'],'normal':forward.tolist()}})
  if a['asset']=='lamp':
   if 'extensions' not in doc:doc['extensions']={'KHR_lights_punctual':{'lights':[]}};doc['extensionsUsed']=['KHR_lights_punctual']
   lights=doc['extensions']['KHR_lights_punctual']['lights'];li=len(lights);lights.append({'type':'point','color':[1,.64,.3],'intensity':9,'range':2.4})
   doc['nodes'][idx]['children'].append(len(doc['nodes']));doc['nodes'].append({'name':a['name']+'_warm_light','translation':[0,.15,.1],'extensions':{'KHR_lights_punctual':{'light':li}}})
 doc['buffers']=[{'byteLength':len(data)}];js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*(-len(js)%4);data+=b'\0'*(-len(data)%4)
 blob=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(data))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(data),b'BIN\0')+data
 path.write_bytes(blob)
 return {'file':str(path.relative_to(P)),'triangles_instanced':sum(sum(len(p['f']) for p in K[a['asset']]['parts']) for a in instances),'mesh_definitions':len(used),'instances':len(instances),'bytes':len(blob)}

if __name__=='__main__':
 stats=[]
 for name in K:stats.append(export(P/'modules'/f'{name}.glb',[{'name':name,'asset':name,'position':[0,0,0],'yaw_degrees':0,'group':'module'}]))
 stats.append(export(P/'starter_crawler_full.glb',A))
 cut=[a for a in A if a['group'] not in ['roof','upper_walls']]
 stats.append(export(P/'starter_crawler_cutaway.glb',cut))
 # Base mesh for live modular equipment: exclude only the individually attached
 # tank and antenna instances, retaining the rest of the cutaway crawler.
 # Do not switch the playable scene until this GLB is generated and verified.
 detachable={'tank__123','antenna__125'}
 clean=[a for a in cut if a['name'] not in detachable]
 stats.append(export(P/'starter_crawler_clean_base.glb',clean))
 catalog=[]
 for i,name in enumerate(K):catalog.append({'name':name,'asset':name,'position':[(i%6)*3.5,(i//6)*4,0],'yaw_degrees':0,'group':'catalog'})
 stats.append(export(P/'modular_kit_catalog.glb',catalog))
 manifest={'version':'0.1','units':'meters','source_axes':'X right, Y forward, Z up','gltf_axes':'X right, Y up, -Z forward','source_to_gltf':'(x,y,z) -> (x,z,-y)','grid_m':1,'prop_snap_m':.25,'deck_height_m':deck,'deck_size_m':[3,6], 'assets':[{k:v for k,v in a.items() if k!='parts'} for a in K.values()],'assembly':A,'stats':stats}
 (P/'kit_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps(stats[-3:],indent=2))
