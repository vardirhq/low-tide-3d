"""Validate the committed character GLBs without third-party Python libraries."""
import json
import math
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'assets/characters/keeper'


def load(name):
    raw = (PACK/name).read_bytes()
    if struct.unpack_from('<4sII', raw) != (b'glTF', 2, len(raw)):
        raise ValueError('Invalid GLB header')
    length = struct.unpack_from('<I', raw, 12)[0]
    if raw[16:20] != b'JSON' or raw[24+length:28+length] != b'BIN\0':
        raise ValueError('Missing GLB chunks')
    return json.loads(raw[20:20+length]), raw[28+length:]


def accessor(doc, data, index):
    a = doc['accessors'][index]
    n = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    fmt = {5126: 'f', 5123: 'H'}[a['componentType']]
    view = doc['bufferViews'][a['bufferView']]
    start = view.get('byteOffset', 0)+a.get('byteOffset', 0)
    size = struct.calcsize('<'+fmt*n)
    stride = view.get('byteStride', size)
    end = start+(a['count']-1)*stride+size
    if end > len(data) or end > view.get('byteOffset', 0)+view['byteLength']:
        raise ValueError('Accessor exceeds buffer')
    return [struct.unpack_from('<'+fmt*n, data, start+i*stride) for i in range(a['count'])]


class KeeperAsset(unittest.TestCase):
    def test_static_fallback_has_no_animation_requirements(self):
        doc, _ = load('keeper_static.glb')
        self.assertNotIn('skins', doc)
        self.assertNotIn('animations', doc)
        self.assertTrue(all('skin' not in n for n in doc['nodes']))
        for primitive in doc['meshes'][0]['primitives']:
            self.assertNotIn('JOINTS_0', primitive['attributes'])
            self.assertNotIn('WEIGHTS_0', primitive['attributes'])

    def test_skin_weights_and_bind_pose(self):
        doc, data = load('keeper_rigged.glb')
        skin = doc['skins'][0]
        self.assertEqual(len(skin['joints']), 17)
        parents = {child: i for i, n in enumerate(doc['nodes']) for child in n.get('children', [])}
        origins = {}

        def world_origin(index):
            if index not in origins:
                t = doc['nodes'][index].get('translation', [0, 0, 0])
                p = world_origin(parents[index]) if index in parents else [0, 0, 0]
                origins[index] = [a+b for a, b in zip(t, p)]
            return origins[index]

        inverse = accessor(doc, data, skin['inverseBindMatrices'])
        for node, matrix in zip(skin['joints'], inverse):
            origin = world_origin(node)
            for axis in range(3):
                self.assertAlmostEqual(matrix[12+axis]+origin[axis], 0, places=6)
            for row in range(4):
                for col in range(4):
                    if col != 3:
                        self.assertAlmostEqual(matrix[col*4+row], float(row == col))
        for primitive in doc['meshes'][0]['primitives']:
            attrs = primitive['attributes']
            vertices = accessor(doc, data, attrs['POSITION'])
            joints = accessor(doc, data, attrs['JOINTS_0'])
            weights = accessor(doc, data, attrs['WEIGHTS_0'])
            self.assertEqual(len(vertices), len(joints))
            self.assertEqual(len(vertices), len(weights))
            for ids, values in zip(joints, weights):
                self.assertTrue(all(0 <= j < 17 for j in ids))
                self.assertEqual(values, (1., 0., 0., 0.))

    def test_five_valid_clips_with_closed_loops(self):
        doc, data = load('keeper_rigged.glb')
        self.assertEqual({a['name'] for a in doc['animations']}, {'idle', 'walk', 'run', 'carry_idle', 'interact'})
        for animation in doc['animations']:
            for channel in animation['channels']:
                self.assertNotEqual(doc['nodes'][channel['target']['node']]['name'], 'root')
                sampler = animation['samplers'][channel['sampler']]
                times = accessor(doc, data, sampler['input'])
                values = accessor(doc, data, sampler['output'])
                self.assertEqual(len(times), len(values))
                self.assertEqual(times[0], (0.,))
                self.assertTrue(all(a[0] < b[0] for a, b in zip(times, times[1:])))
                self.assertTrue(all(math.isfinite(v) for row in values for v in row))
                if channel['target']['path'] == 'rotation':
                    for value in values:
                        self.assertAlmostEqual(sum(v*v for v in value), 1, places=5)
                if animation['extras']['loop_hint']:
                    for a, b in zip(values[0], values[-1]):
                        self.assertAlmostEqual(a, b, places=5)
            outputs = [accessor(doc, data, s['output']) for s in animation['samplers']]
            self.assertTrue(any(any(sum(abs(a-b) for a, b in zip(row, rows[0])) > .001
                                    for row in rows[1:]) for rows in outputs))

    def test_static_and_rigged_share_geometry_and_fit_doorway(self):
        static, sdata = load('keeper_static.glb')
        rigged, rdata = load('keeper_rigged.glb')
        vertices = []
        for a, b in zip(static['meshes'][0]['primitives'], rigged['meshes'][0]['primitives']):
            va = accessor(static, sdata, a['attributes']['POSITION'])
            vb = accessor(rigged, rdata, b['attributes']['POSITION'])
            self.assertEqual(va, vb)
            vertices.extend(va)
        self.assertAlmostEqual(min(p[1] for p in vertices), 0)
        self.assertLess(max(p[0] for p in vertices)-min(p[0] for p in vertices), .82)
        self.assertLess(max(p[1] for p in vertices), 2.05)
        self.assertTrue(all(math.isfinite(x) for p in vertices for x in p))


if __name__ == '__main__':
    unittest.main()
