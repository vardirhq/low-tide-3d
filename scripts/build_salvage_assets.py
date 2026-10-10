#!/usr/bin/env python3
"""Build the Last Signal pack without regenerating or modifying the crawler kit."""
import argparse
import json
import struct

import numpy as np
from scipy.spatial.transform import Rotation
from salvage_shapes import ROOT, ASSETS, kit

OUT = ROOT / 'assets/salvage'


def instance(asset, position=(0, 0, 0), yaw=0, name=None):
    return {'name': name or asset, 'asset': asset, 'position': list(position),
            'yaw_degrees': yaw, 'group': 'salvage'}


CATALOG = [instance(name, ((i % 4-1.5)*3, (i//4-1.5)*3.5, 0))
           for i, name in enumerate(ASSETS)]
DIORAMA = [
    instance('wreck_rib_2m', (0, y, 0), name=f'wreck_bay_{y}') for y in [0, 1, 2]
] + [
    instance('wreck_bulkhead_2m', (0, 2.5, .25)),
    instance('radio_desk', (0, 1.65, .28)),
    instance('replacement_alternator', (0, -.15, .28)),
    instance('signal_beacon', (-2.1, 2, 0)),
    instance('tide_gauge', (2, 2, 0)),
    instance('salvage_locker', (-2.2, .65, 0), -15),
    instance('supply_shelf', (-2.1, -.7, 0), -15),
    instance('cargo_pallet', (-1.8, -2.1, 0)),
    instance('battery_pack', (-2.05, -2.1, .235)),
    instance('fuel_drum', (-1.45, -2.1, .235)),
    instance('water_pump', (1.9, -.2, 0), -30),
    instance('salvage_winch', (1.7, -1.8, 0), 20),
    instance('floodlight', (2.2, .95, 0), 25),
]


def export(path, instances, root_name):
    stats = kit.export(path, instances)
    # Shared writer has a crawler-specific root label; change only this pack's root.
    raw = path.read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+size])
    doc['nodes'][0]['name'] = root_name
    doc['asset']['generator'] = 'Low Tide Last Signal kit v0.1'
    body = json.dumps(doc, separators=(',', ':')).encode()
    body += b' ' * (-len(body) % 4)
    tail = raw[20+size:]
    path.write_bytes(struct.pack('<4sII', b'glTF', 2, 20+len(body)+len(tail)) +
                     struct.pack('<I4s', len(body), b'JSON') + body + tail)
    stats['bytes'] = path.stat().st_size
    return stats


def build_scene():
    base = json.loads((ROOT / 'poc.scene').read_text())
    entities = [e for e in base['entities'] if e['id'] in ['environment', 'sun']]
    eye = np.array([12., 13., 18.])
    back = eye - [0, 1, 0]
    back /= np.linalg.norm(back)
    right = np.cross([0, 1, 0], back)
    right /= np.linalg.norm(right)
    up = np.cross(back, right)
    rotation = Rotation.from_matrix(np.column_stack([right, up, back])).as_quat().tolist()
    entities.append({'id': 'camera', 'name': 'Static salvage catalog camera',
                     'transform_3d': {'position': eye.tolist(), 'rotation': rotation, 'scale': [1, 1, 1]},
                     'components': {'sindri.camera': {'projection': 'perspective',
                                                      'vertical_fov_degrees': 45, 'near': .1, 'far': 120}}})
    for item in CATALOG:
        yaw = np.radians(item['yaw_degrees'])
        entities.append({'id': item['name'].replace('_', '-'), 'name': item['asset'],
                         'transform_3d': {'position': (kit.C @ item['position']).tolist(),
                                          'rotation': [0, float(np.sin(yaw/2)), 0, float(np.cos(yaw/2))],
                                          'scale': [1, 1, 1]},
                         'components': {'sindri.model': {
                             'asset': f'assets/salvage/modules/{item["asset"]}.glb', 'layer': 1}}})
    scene = {'format_version': base['format_version'],
             'metadata': {'name': 'Low Tide — Last Signal asset catalog (static)'}, 'entities': entities}
    (ROOT / 'salvage-catalog.scene').write_text(json.dumps(scene, indent=2)+'\n')


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'modules').mkdir(exist_ok=True)
    kit.P = OUT
    assets = []
    for name in ASSETS:
        definition = kit.K[name]
        stats = export(OUT/'modules'/f'{name}.glb', [instance(name)], f'LT_{name}')
        vertices = np.concatenate([p['v'] for p in definition['parts']])
        # Multiple boxes preserve negative space (walk-through bulkhead, shelf, hull).
        collision = []
        for part in definition['parts']:
            lo, hi = part['v'].min(0), part['v'].max(0)
            collision.append({'part': part['name'], 'type': 'box',
                              'center': ((lo+hi)/2).tolist(), 'size': (hi-lo).tolist()})
        assets.append({k: v for k, v in definition.items() if k != 'parts'} | {
            'path': f'assets/salvage/modules/{name}.glb',
            'bounds_source_m': [vertices.min(0).tolist(), vertices.max(0).tolist()],
            'triangles': stats['triangles_instanced'], 'bytes': stats['bytes'],
            'material_primitives': len({p['mat'] for p in definition['parts']}),
            'collision_proposal': collision})
    combined = [export(OUT/'salvage_catalog.glb', CATALOG, 'LT_Salvage_Catalog'),
                export(OUT/'last_signal_diorama.glb', DIORAMA, 'LT_Last_Signal_Study')]
    manifest = {'version': '0.1', 'units': 'meters', 'source_axes': 'X right, Y forward, Z up',
                'gltf_axes': 'X right, Y up, -Z forward', 'source_to_gltf': '(x,y,z) -> (x,z,-y)',
                'placement_snap_m': .25, 'socket_standard': 'LT_mount_025',
                'socket_gltf_axes': '+Z outward, +Y up tangent',
                'collision_status': 'Conservative per-part AABB proposals in source axes; not active physics.',
                'assets': assets, 'catalog': CATALOG, 'diorama': DIORAMA, 'combined': combined}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    build_scene()
    print(f'Built {len(assets)} assets / {sum(a["triangles"] for a in assets)} unique triangles')


def render():
    from render_preview import render as render_meshes
    from PIL import Image, ImageDraw, ImageFont
    render_meshes(DIORAMA, OUT/'preview_diorama.png', w=1400, h=1150, eye=(8, -12, 11), scale=125)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        font = ImageFont.truetype(font_path, 18)
    except OSError:
        font = ImageFont.load_default()
    sheet = Image.new('RGB', (1600, 1600), (34, 45, 49))
    draw = ImageDraw.Draw(sheet)
    for i, name in enumerate(ASSETS):
        temp = OUT/f'.preview_{name}.png'
        # Shared renderer's fixed look-at is corrected by centering each asset.
        v = np.concatenate([p['v'] for p in kit.K[name]['parts']])
        center = (v.max(0)+v.min(0))/2
        offset = np.array([0, -.6, 1.2])-center
        scale = min(150, 245/max(v.max(0)-v.min(0)))
        render_meshes([instance(name, offset)], temp, w=400, h=355, eye=(7, -11, 8), scale=scale)
        sheet.paste(Image.open(temp), ((i % 4)*400, (i//4)*400))
        draw.text(((i % 4)*400+18, (i//4)*400+360), name.replace('_', ' '), fill='#ddccab', font=font)
        temp.unlink()
    sheet.save(OUT/'preview_catalog.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    build()
    if args.render:
        render()
