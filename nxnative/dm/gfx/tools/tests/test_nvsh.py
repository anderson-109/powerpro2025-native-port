"""NVSH descriptors must locate padded compute payloads and reject invalid bounds."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nvsh import read_nvsh

def program(padding=0):
    own = 0x880
    ctl = bytearray(own + padding)
    ctl[:4] = bytes.fromhex('34127698')
    struct.pack_into('<I', ctl, 0x20, own)
    code = bytes.fromhex('0000000000000000')
    struct.pack_into('<I', ctl, 0x704, len(code))
    struct.pack_into('<3I', ctl, 0x748, 8, 1, 1)
    data = bytearray(0x40)
    data[:4] = b'NVSH'
    struct.pack_into('<4I', data, 4, 1, 0, 1, 1 << 5)
    struct.pack_into('<I', data, 0x14, 0x40)
    data += struct.pack('<6I', 5, len(ctl)+len(code), 0, len(ctl), len(ctl), len(code))
    return data + ctl + code

class NvshTests(unittest.TestCase):
    def test_compute_uses_descriptor_span(self):
        for pad in (0, 0x18, 0x400):
            with self.subTest(padding=pad):
                programs, records = read_nvsh(program(pad))
                self.assertEqual(len(programs), 1)
                item, ctl, code = records[0]
                self.assertEqual(item['stage'], 'cs')
                self.assertEqual(item['group'], [8, 1, 1])
                self.assertEqual(len(ctl), 0x880 + pad)
                self.assertEqual(code, bytes(8))
    def test_truncated_code_rejected(self):
        with self.assertRaises(AssertionError): read_nvsh(program()[:-1])
    def test_stage_mask_rejected(self):
        data = program()
        struct.pack_into('<I', data, 0x40, 0)
        with self.assertRaises(AssertionError): read_nvsh(data)
    def test_non_container_string_ignored(self):
        self.assertEqual(read_nvsh(b'NVSH' + bytes(60)), ([], []))

if __name__ == '__main__': unittest.main()
