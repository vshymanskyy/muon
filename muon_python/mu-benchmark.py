#!/usr/bin/env python3

import sys, io, os
import csv

import json
import bson
#import msgpack
import cbor2
import ubjson
#import pysmile
import muon

#import zlib
import gzip
import bz2
import lzma
import brotli
import heatshrink2

def pack_bson(data):
    try:
        return bson.dumps(data)
    except:
        return bson.dumps({'':data})

encoders = {
  "BSON":       pack_bson,
  "UBJSON":     lambda data: ubjson.dumpb(data),
  #"MsgPack":   lambda data: msgpack.packb(data),
  "CBOR":       lambda data: cbor2.dumps(data, string_referencing=False),
  #"Smile":     lambda data: pysmile.encode(data),
  "Muon":       lambda data: muon.dumps(data, refs=False),

  "CBOR+refs":  lambda data: cbor2.dumps(data, string_referencing=True),
  "Muon+refs":  lambda data: muon.dumps(data, refs=True),
  "JSON":       lambda data: json.dumps(data, separators=(',', ':')).encode('utf8'),
}

compressors = {
  #"zl":    lambda data: zlib.compress(data, level=9),
  "gz":     lambda data: gzip.compress(data, compresslevel=9),
  "bz2":    lambda data: bz2.compress(data, compresslevel=9),
  "xz":     lambda data: lzma.compress(data, format=lzma.FORMAT_XZ,
                                       preset=9 | lzma.PRESET_EXTREME),
  "br":     lambda data: brotli.compress(data, quality=11),
  "hs":     lambda data: heatshrink2.compress(data, window_sz2=12, lookahead_sz2=5),
}

comprs = [None, 'gz']
#comprs += list(compressors.keys())

for compr in comprs:

    if compr:
        ofn = './results/mu-benchmark-' + compr + '.csv'
    else:
        ofn = './results/mu-benchmark.csv'

    cols = [""] + list(encoders.keys())
    csvfile = open(ofn, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=cols)
    writer.writeheader()

    for ifn in sys.argv[1:]:

        with open(ifn) as f:
            data = json.load(f)
        data_size = len(encoders["JSON"](data))

        row = {
            "": ifn.replace(".json", "").replace(".min", "").replace("./","").replace("data/","")
        }

        for enc_name, enc_func in encoders.items():
            try:
                enc_data = enc_func(data)

                if compr is not None:
                    enc_data = compressors[compr](enc_data)

                size = len(enc_data)

                row[enc_name] = "{:.2f}%".format((size*100) / data_size)
            except Exception as e:
                print(e)

        writer.writerow(row)
