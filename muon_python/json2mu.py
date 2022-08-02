#!/usr/bin/env python3

import sys
import json
import muon

ifn = sys.argv[1]
ofn = sys.argv[2]

with open(ifn) as f:
    data = json.load(f)

if True:
    print("Analysing JSON")
    d = muon.DictBuilder()
    d.add(data)
    t = d.get_dict(512)
    #print(t)
else:
    t = []

print("Generating MuON")

if ofn.endswith(".hs"):
    import hsfile
    f = hsfile.open(ofn, "wb")
else:
    f = open(ofn, "wb")

m = muon.Writer(f)
m.tag_muon()
if len(t) > 128:
    m.add_lru_list(reversed(t))
elif len(t):
    m.add_lru_dynamic(t)
m.add(data)
