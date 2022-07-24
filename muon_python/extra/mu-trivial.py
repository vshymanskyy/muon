#!/usr/bin/env python3

import leb128, struct
from collections.abc import Mapping, Sequence

class Writer:
    def __init__(self, out):
        self.out = out

    def add(self, val):
        if isinstance(val, str):
            self.out.write(str(val).encode('utf8') + b'\x00')
        elif val is None:
            self.out.write(b'\xAC')
        elif isinstance(val, bool):
            self.out.write(b'\xAB' if val else b'\xAA')
        elif isinstance(val, int):
            if val >= 0 and val <= 9:
                self.out.write(bytes([0xA0 + val]))
            else:
                self.out.write(b'\xBB' + leb128.i.encode(int(val)))
        elif isinstance(val, float):
            self.out.write(b'\xBA' + struct.pack('<d', val))
        elif isinstance(val, Sequence):
            self.out.write(b'\x90')
            for v in val:
                self.add(v)
            self.out.write(b'\x91')
        elif isinstance(val, Mapping):
            self.out.write(b'\x92')
            for k, v in val.items():
                self.add(k)
                self.add(v)
            self.out.write(b'\x93')

if __name__ == '__main__':
    import sys, io, json
    with open(sys.argv[1]) as f:
        data = json.load(f)
    muon = Writer(io.BytesIO())
    muon.add(data)
    sys.stdout.buffer.write(muon.out.getvalue())

