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
    from heatshrink2.streams import HeatshrinkFile

    window = 10
    lookahead = 4

    rawf = open(ofn, 'wb')
    rawf.write(b'H$' + bytes([(window << 4) | lookahead]))

    f = HeatshrinkFile(rawf, 'wb',
                       window_sz2    = window,
                       lookahead_sz2 = lookahead)

else:
    f = open(ofn, 'wb')

muon = muon.Writer(f)
#muon.tag_muon()
if len(t):
    muon.add_lru_list(reversed(t))
muon.add(data)
