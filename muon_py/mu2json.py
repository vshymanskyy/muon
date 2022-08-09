#!/usr/bin/env python3

import sys
import json
import muon

inp = sys.argv[1]

if inp.endswith(".hs"):
    import hsfile
    f = hsfile.open(inp, "rb")
else:
    f = open(inp, "rb")

m = muon.Reader(f)
data = m.read_object()

json.dump(data, sys.stdout, indent=2)
print()
