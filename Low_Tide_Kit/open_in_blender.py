"""Run in Blender's Scripting workspace after setting KIT below if necessary.
Imports the full GLB, organizes visibility collections, and saves a .blend.
Does not clear your scene. Requires Blender with its standard glTF importer.
"""
import bpy,pathlib
KIT=pathlib.Path(__file__).resolve().parent if '__file__' in globals() else pathlib.Path(bpy.path.abspath('//'))
bpy.ops.import_scene.gltf(filepath=str(KIT/'starter_crawler_full.glb'))
root=bpy.data.objects.get('LT_Crawler_Root')
groups={}
for o in list(bpy.context.selected_objects):
 group=o.get('visibility_group')
 if not group:continue
 if group not in groups:
  coll=bpy.data.collections.new('LT_'+group);bpy.context.scene.collection.children.link(coll);groups[group]=coll
 for coll in list(o.users_collection):coll.objects.unlink(o)
 groups[group].objects.link(o)
for name in ('roof','upper_walls'):
 if name in groups:groups[name].hide_viewport=True;groups[name].hide_render=True
bpy.context.scene.unit_settings.system='METRIC'
# Each module instance shares mesh data with its siblings. Make single-user before unique edits.
bpy.ops.wm.save_as_mainfile(filepath=str(KIT/'starter_crawler.blend'))
print('Saved starter_crawler.blend; toggle LT_roof and LT_upper_walls to close the shell.')
