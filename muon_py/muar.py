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

def is_sparse(ranges, filesize):
    if len(ranges) == 1:
        return ranges[0] != (0, filesize)
    else:
        return True

def strip_zeros(offset, data):
    # Find first non-zero byte
    size = len(data)
    fnz = 0
    while fnz < size:
        if data[fnz]: break
        fnz += 1
    else:
        # Skip all-zeroes block
        return (offset, [])

    # Strip leading zeroes
    data = data[fnz:size]
    offset += fnz
    size = len(data)

    # Find last non-zero byte
    while size > 0:
        if data[size-1]: break
        size -= 1

    # Strip trailing zeroes
    data = data[0:size]

    return (offset, data)

muon = muon.Writer(f)
muon.tag_muon()
muon.add_lru_dynamic([
    "name","data","offset","size",
    "owner","group","mtime","mode",
    "md5","sha1","sha256"
])

muon.start_list()

for filename in files:
    fn = os.path.join(inp, filename)
    path = Path(fn)
    stat = path.stat()
    filesize = stat.st_size

    with open(fn, "rb") as src:
        muon.start_dict()
        muon.add("name").add(filename)
        muon.add("mtime").add(int(stat.st_mtime))
        muon.add("owner").add(path.owner())
        muon.add("group").add(path.group())
        muon.add("mode").add(stat.st_mode & 0o777)

        ranges = sparse_ranges(src)
        #print(filename, ranges)
        if is_sparse(ranges, filesize):
            # Sparse file detected
            muon.add("size").add(filesize)
            muon.add("data").start_list()

            for offset, size in ranges:
                src.seek(offset)
                data = src.read(size)

                offset, data = strip_zeros(offset, data)
                if not len(data):
                    continue

                muon.start_dict()
                muon.add("offset").add(offset)
                muon.add("md5").add(hashlib.md5(data).digest())
                #muon.add("sha1").add(hashlib.sha1(data).digest())
                #muon.add("sha256").add(hashlib.sha256(data).digest())
                muon.add("data").add(data)
                muon.end_dict()

            muon.end_list()

        else:
            data = src.read()

            muon.add("md5").add(hashlib.md5(data).digest())
            #muon.add("sha1").add(hashlib.sha1(data).digest())
            #muon.add("sha256").add(hashlib.sha256(data).digest())
            muon.add("data").add(data)

        muon.end_dict()

muon.end_list()
