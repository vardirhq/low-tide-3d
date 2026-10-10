"""Committed asset-contract checks; no geometry libraries or engine required."""
import json
import math
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'assets/salvage'
MANIFEST = json.loads((PACK / 'manifest.json').read_text())


def glb(path):
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from('<4sII', raw)
    if (magic, version, total) != (b'glTF', 2, len(raw)):
        raise ValueError(f'Invalid GLB header: {path}')
    chunks, offset = [], 12
    while offset < total:
        length, kind = struct.unpack_from('<I4s', raw, offset)
        if length % 4 or offset+8+length > total:
            raise ValueError('Invalid/alignment-exceeding chunk length')
        chunks.append((kind, raw[offset+8:offset+8+length]))
        offset += 8+length
    if [c[0] for c in chunks] != [b'JSON', b'BIN\0']:
        raise ValueError('Expected self-contained JSON/BIN GLB')
    return json.loads(chunks[0][1]), chunks[1][1]


def vectors(doc, blob, index):
    a = doc['accessors'][index]
    if a['componentType'] != 5126 or a['type'] != 'VEC3':
        raise ValueError('Expected float32 VEC3')
    view = doc['bufferViews'][a['bufferView']]
    start = view.get('byteOffset', 0)+a.get('byteOffset', 0)
    stride = view.get('byteStride', 12)
    end = start+(a['count']-1)*stride+12
    if end > view.get('byteOffset', 0)+view['byteLength'] or end > len(blob):
        raise ValueError('Accessor exceeds buffer')
    return [struct.unpack_from('<3f', blob, start+i*stride) for i in range(a['count'])]


class SalvageAssets(unittest.TestCase):
    def test_catalog_covers_each_unique_asset(self):
        names = [a['id'] for a in MANIFEST['assets']]
        self.assertEqual(len(names), 14)
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(set(names), {a['asset'] for a in MANIFEST['catalog']})
        self.assertEqual(set(names), {p.stem for p in (PACK/'modules').glob('*.glb')})

    def test_embedded_geometry_bounds_normals_and_counts(self):
        for asset in MANIFEST['assets']:
            with self.subTest(asset=asset['id']):
                path = ROOT/asset['path']
                doc, data = glb(path)
                self.assertEqual(len(doc['meshes']), 1)
                self.assertEqual(path.stat().st_size, asset['bytes'])
                self.assertNotIn('uri', doc['buffers'][0])
                self.assertEqual(doc['buffers'][0]['byteLength'], len(data))
                count, all_v = 0, []
                for prim in doc['meshes'][0]['primitives']:
                    vertices = vectors(doc, data, prim['attributes']['POSITION'])
                    normals = vectors(doc, data, prim['attributes']['NORMAL'])
                    self.assertEqual(len(vertices) % 3, 0)
                    self.assertEqual(len(vertices), len(normals))
                    self.assertTrue(all(math.isfinite(v) for p in vertices for v in p))
                    for normal in normals:
                        self.assertAlmostEqual(sum(v*v for v in normal), 1, places=5)
                    all_v.extend(vertices)
                    count += len(vertices)//3
                self.assertEqual(count, asset['triangles'])
                low, high = asset['bounds_source_m']
                expected_low, expected_high = [low[0], low[2], -high[1]], [high[0], high[2], -low[1]]
                for axis in range(3):
                    self.assertAlmostEqual(min(v[axis] for v in all_v), expected_low[axis], places=5)
                    self.assertAlmostEqual(max(v[axis] for v in all_v), expected_high[axis], places=5)

    def test_socket_frames_match_outward_normals(self):
        for asset in MANIFEST['assets']:
            doc, _ = glb(ROOT/asset['path'])
            sockets = [n for n in doc['nodes'] if n['name'].startswith('SOCKET_')]
            self.assertEqual(len(sockets), len(asset['sockets']))
            for node in sockets:
                x, y, z, w = node['rotation']
                self.assertAlmostEqual(x*x+y*y+z*z+w*w, 1)
                outward = [2*(x*z+w*y), 2*(y*z-w*x), 1-2*(x*x+y*y)]
                for actual, expected in zip(outward, node['extras']['normal']):
                    self.assertAlmostEqual(actual, expected)

    def test_scene_positions_and_assets_follow_manifest(self):
        scene = json.loads((ROOT/'salvage-catalog.scene').read_text())
        entities = {e['id']: e for e in scene['entities']}
        self.assertEqual(len(entities), len(scene['entities']))
        for item in MANIFEST['catalog']:
            entity = entities[item['name'].replace('_', '-')]
            x, y, z = item['position']
            self.assertEqual(entity['transform_3d']['position'], [x, z, -y])
            self.assertEqual(entity['transform_3d']['scale'], [1, 1, 1])
            self.assertTrue((ROOT/entity['components']['sindri.model']['asset']).is_file())
        self.assertTrue(all('sindri.script' not in e['components'] for e in entities.values()))

    def test_combined_models_reuse_module_geometry(self):
        for filename, assembly_key in [('salvage_catalog.glb', 'catalog'), ('last_signal_diorama.glb', 'diorama')]:
            doc, _ = glb(PACK/filename)
            instances = MANIFEST[assembly_key]
            self.assertEqual(len(doc['nodes'][0]['children']), len(instances))
            self.assertEqual(len(doc['meshes']), len({i['asset'] for i in instances}))
            for node_index, item in zip(doc['nodes'][0]['children'], instances):
                node = doc['nodes'][node_index]
                self.assertEqual(doc['meshes'][node['mesh']]['name'], item['asset'])
                x, y, z = item['position']
                self.assertEqual(node['translation'], [x, z, -y])

    def test_bulkhead_collision_leaves_walkthrough_open(self):
        bulkhead = next(a for a in MANIFEST['assets'] if a['id'] == 'wreck_bulkhead_2m')
        for box in bulkhead['collision_proposal']:
            x, _, z = box['center']
            sx, _, sz = box['size']
            # A 0.9 m wide, 1.77 m tall route must remain free.
            self.assertTrue(x+sx/2 <= -.45+1e-8 or x-sx/2 >= .45-1e-8 or z-sz/2 >= 1.77)


if __name__ == '__main__':
    unittest.main()
