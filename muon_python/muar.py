#!/usr/bin/env python3

import sys, os
import muon
import hashlib
from pathlib import Path

inp = sys.argv[1]
ofn = sys.argv[2]

if ofn.endswith(".hs"):
    import hsfile
    f = hsfile.open(ofn, "wb")
elif ofn.endswith(".gz"):
    import gzip
    f = gzip.open(ofn, "wb")
elif ofn.endswith(".bz2"):
    import bz2
    f = bz2.open(ofn, "wb")
elif ofn.endswith(".xz"):
    import lzma
    f = lzma.open(ofn, "wb")
else:
    f = open(ofn, 'wb')

muon = muon.Writer(f)
muon.add_lru_dynamic(["name","md5","sha256","data","owner","group","mtime","mode"])

files = os.listdir(inp)
files.sort()

muon.start_list()

for filename in files:
    fn = os.path.join(inp, filename)
    path = Path(fn)

    with open(fn, "rb") as src:
        data = src.read()

    muon.add({
      "name":     filename,
      "md5":      hashlib.md5(data).digest(),
      "sha256":   hashlib.sha256(data).digest(),
      "mtime":    int(path.stat().st_mtime),
      #"owner":   path.owner(),
      #"group":   path.group(),
      #"mode":    path.stat().st_mode,
      "data":     data
    })

muon.end_list()
