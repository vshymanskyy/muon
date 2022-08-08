#!/usr/bin/env python3

import sys, os
import muon
import hashlib
from pathlib import Path
from errno import ENXIO

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
muon.add_lru_dynamic(["name","md5","sha256","data","offset","size","owner","group","mtime","mode"])

files = os.listdir(inp)
files.sort()

def sparse_ranges(f):
    cur = f.tell()
    ranges = []
    end = 0
    while True:
        try:
            beg = f.seek(end, os.SEEK_DATA)
            end = f.seek(beg, os.SEEK_HOLE)
            ranges.append((beg, end-beg))
        except OSError as e:
            if e.errno != ENXIO:
                raise
            f.seek(cur)
            return ranges

muon.start_list()

for filename in files:
    fn = os.path.join(inp, filename)
    path = Path(fn)

    with open(fn, "rb") as src:

        muon.start_dict()
        muon.add("name").add(filename)
        muon.add("mtime").add(int(path.stat().st_mtime))
        muon.add("owner").add(path.owner())
        muon.add("group").add(path.group())
        muon.add("mode").add(path.stat().st_mode)

        ranges = sparse_ranges(src)
        #print(ranges)
        if len(ranges) > 1:
            # Sparse file detected
            muon.add("size").add(path.stat().st_size)
            muon.add("data").start_list()

            for offset, size in ranges:
                src.seek(offset)
                data = src.read(size)

                muon.start_dict()
                muon.add("offset").add(offset)
                muon.add("md5").add(hashlib.md5(data).digest())
                muon.add("sha256").add(hashlib.sha256(data).digest())
                muon.add("data").add(data)
                muon.end_dict()

            muon.end_list()

        else:
            data = src.read()

            muon.add("md5").add(hashlib.md5(data).digest())
            muon.add("sha256").add(hashlib.sha256(data).digest())
            muon.add("data").add(data)

        muon.end_dict()
muon.end_list()
