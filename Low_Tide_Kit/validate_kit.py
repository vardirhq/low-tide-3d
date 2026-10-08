"""Structural checks and independent GLB import. Requires trimesh, numpy, scipy."""
from build_kit import *
import trimesh
results=[]
for name,a in K.items():
 for p in a['parts']:
  assert np.isfinite(p['v']).all(),(name,p['name'])
  t=trimesh.Trimesh(p['v'],p['f'],process=True)
  assert t.is_watertight,(name,p['name'],'open geometry')
  assert t.is_winding_consistent,(name,p['name'],'inconsistent winding')
  assert t.volume>0,(name,p['name'],'inverted winding')
 s=trimesh.load(P/'modules'/f'{name}.glb',force='scene')
 assert len(s.geometry)>0
for fn in ['starter_crawler_full.glb','starter_crawler_cutaway.glb','modular_kit_catalog.glb']:
 raw=(P/fn).read_bytes();magic,ver,length=struct.unpack('<4sII',raw[:12]);assert magic==b'glTF' and ver==2 and length==len(raw)
 jslen=struct.unpack('<I',raw[12:16])[0];doc=json.loads(raw[20:20+jslen])
 for n in doc['nodes']:
  if 'rotation' in n:assert abs(np.linalg.norm(n['rotation'])-1)<1e-6
  if n['name'].startswith('SOCKET_'):
   assert np.allclose(Rotation.from_quat(n['rotation']).apply([0,0,1]),n['extras']['normal'])
 s=trimesh.load(P/fn,force='scene')
 results.append({'file':fn,'mesh_definitions':len(doc['meshes']),'module_instances':len(doc['nodes'][0]['children']),'gltf_bounds_m':s.bounds.tolist(),'import':'PASS'})
tiles=[a for a in A if a['asset']=='floor_1m'];assert len(tiles)==18
assert len({tuple(a['position']) for a in tiles})==18
# Character at X=0 has at least 0.82 m doorway clearance; center route excludes props.
for a in A:
 if a['group']!='interior' or a['asset'] in ['rug','lamp','helm','stool']:continue
 t=math.radians(a['yaw_degrees']);r=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
 v=np.concatenate([p['v'] for p in K[a['asset']]['parts']])@r.T+a['position']
 assert v[:,0].max()<=-.41 or v[:,0].min()>=.41,(a['name'],'blocks center aisle')
report={'status':'PASS','module_count':len(K),'closed_positive_volume_parts':sum(len(a['parts']) for a in K.values()),'checks':['All primitive parts watertight, consistently wound, positive volume','Finite vertex positions','All module GLBs imported independently with trimesh','Assembly GLB headers and quaternion lengths','Socket +Z axes match attachment normals','18 unique 1-meter floor cells','0.82 m center aisle free of fixed props, except helm/stool at terminus'], 'not_tested':['Blender application import (Blender unavailable)','Sindri runtime import and physics','Character navigation and stepping','Track animation','glTF validator conformance suite'], 'assemblies':results}
(P/'validation_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
