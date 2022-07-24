#!/usr/bin/env python3

import sys, os
import muon

inp = sys.argv[1]
ofn = sys.argv[2]

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

muon = muon.Writer(f) #table=["name","mode","regular","type","uid","gid","size"])

files = os.listdir(inp)
files.sort()

muon.start_list()

for filename in files:
    fn = os.path.join(inp, filename)

    with open(fn, "rb") as src:
        data = src.read()

    import hashlib

    muon.add_attr({
      "name": filename,
      "md5": hashlib.md5(data).hexdigest(),
      "sha256": hashlib.sha256(data).hexdigest(),
      #"mode": 0o777,
      #"type": "regular",
      #"uid":  1,
      #"gid":  1,
      #"size": os.path.getsize(fn)
    })
    muon.add_binary(data)



muon.end_list()

print(f"MuON:       {f.tell()} bytes")

if ofn.endswith(".hs"):
    f.close()
    ratio = (rawf.tell()*100) / f.tell()
    print(f"Heatshrink: {rawf.tell()} bytes, {ratio:.3f} %")
