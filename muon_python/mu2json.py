#!/usr/bin/env python3

import sys
import json
import muon

inp = sys.argv[1]

if inp.endswith(".hs"):
    from heatshrink2.streams import HeatshrinkFile

    f = open(inp, "rb")

    if not b'H$' == f.read(2):
        raise Exception("Heatshrink header not found")

    params = f.read(1)[0]

    f = HeatshrinkFile(f, window_sz2    = (params >> 4) & 0xF,
                          lookahead_sz2 = (params     ) & 0xF)

else:
    f = open(inp, "rb")

m = muon.Reader(f)
data = m.read_object()

json.dump(data, sys.stdout, indent=4)
print()
