"""Reflection counterexamples for overlapping NVN texture/image handle tables."""
import ast
from pathlib import Path
import re
import unittest

source = Path(__file__).resolve().parents[1] / 'dmsh_build.py'
node = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'image_query_slot')
space = {'re': re, 'IMG_BASE': 0x120, 'IMG_SLOTS': 8}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), space)
query = space['image_query_slot']

class ImageQueryTests(unittest.TestCase):
    def test_size_query_uses_declared_image_handle(self):
        src = 'texture2d<float, access::write> cp_i_cb2_48_; int w = spvDescriptorSet0.cp_t_tcb_48.get_width(); int h = spvDescriptorSet0.cp_t_tcb_48.get_height();'
        self.assertEqual(query(src, 'cp_t_tcb_48'), 0)
        self.assertEqual(query(src.replace('48', '56'), 'cp_t_tcb_56'), 7)

    def test_sampled_texture_in_overlap_is_not_reclassified(self):
        src = 'cp_i_cb2_48_; spvDescriptorSet0.cp_t_tcb_48.get_width(); spvDescriptorSet0.cp_t_tcb_48.sample(s, uv);'
        self.assertIsNone(query(src, 'cp_t_tcb_48'))

    def test_different_image_or_indirect_reference_is_not_evidence(self):
        self.assertIsNone(query('cp_i_cb2_4A_; spvDescriptorSet0.cp_t_tcb_48.get_width();', 'cp_t_tcb_48'))
        self.assertIsNone(query('cp_i_cb2_48_; spvDescriptorSet0.cp_t_tcb_48.get_width(); helper(spvDescriptorSet0.cp_t_tcb_48);', 'cp_t_tcb_48'))
        self.assertIsNone(query('cp_i_cb2_48_;', 'cp_t_tcb_48'))

if __name__ == '__main__':
    unittest.main()
