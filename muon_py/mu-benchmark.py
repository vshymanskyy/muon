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
#from flatbuffers import flexbuffers
#import pickle
#import marshal

#import zlib
import gzip
import bz2
import lzma
import brotli
import heatshrink2

validate = True

def pack_bson(data):
    try:
        return bson.dumps(data)
    except:
        return bson.dumps({'':data})

def ppjson(data):
    return json.dumps(data, indent=4, sort_keys=True)

def pack_muon(data, refs):
    orig_json = ppjson(data)

    res = muon.dumps(data, refs)

    if validate:
        m = muon.Reader(io.BytesIO(res))
        decoded = m.read_object()
        decoded_json = ppjson(decoded)

        if decoded_json != orig_json:
            print("Muon validation failed")
    return res

encoders = {
  "BSON":       pack_bson,
  #"FlexBuf":    lambda data: flexbuffers.Dumps(data),
  "UBJSON":     lambda data: ubjson.dumpb(data),
  #"MsgPack":   lambda data: msgpack.packb(data),
  "CBOR":       lambda data: cbor2.dumps(data, string_referencing=False),
  #"Smile":     lambda data: pysmile.encode(data),
  #"pickle":     lambda data: pickle.dumps(data),
  #"marshal":    lambda data: marshal.dumps(data),
  "Muon":       lambda data: pack_muon(data, refs=False),

  "CBOR+refs":  lambda data: cbor2.dumps(data, string_referencing=True),
  "Muon+refs":  lambda data: pack_muon(data, refs=True),
  "JSON":       lambda data: json.dumps(data, separators=(',', ':')).encode('utf8'),
}

compressors = {
  None:     lambda data: data,
  #"zl":    lambda data: zlib.compress(data, level=9),
  "gz":     lambda data: gzip.compress(data, compresslevel=9),
  "bz2":    lambda data: bz2.compress(data, compresslevel=9),
  "xz":     lambda data: lzma.compress(data, format=lzma.FORMAT_XZ,
                                       preset=9 | lzma.PRESET_EXTREME),
  "br":     lambda data: brotli.compress(data, quality=11),
  "hs":     lambda data: heatshrink2.compress(data, window_sz2=12, lookahead_sz2=5),
}

comprs = [None, 'gz', 'hs'] # list(compressors.keys())
compr_csv = {}

for compr in comprs:
    if compr:
        ofn = './results/mu-benchmark-' + compr + '.csv'
    else:
        ofn = './results/mu-benchmark.csv'

    cols = [""] + list(encoders.keys())
    csvfile = open(ofn, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=cols)
    writer.writeheader()

    compr_csv[compr] = writer

for ifn in sys.argv[1:]:
    print(ifn)

    with open(ifn) as f:
        data = json.load(f)
    data_size = len(encoders["JSON"](data))

    row = {}
    for compr in comprs:
        row[compr] = {
            "": ifn.replace(".json", "").replace(".min", "").replace("./","").replace("data/","")
        }

    for enc_name, enc_func in encoders.items():
        try:
            enc_data = enc_func(data)

            for compr in comprs:
                compr_data = compressors[compr](enc_data)

                size = len(compr_data)

                row[compr][enc_name] = "{:.2f}%".format((size*100) / data_size)


        except Exception as e:
            print(e)

    for compr in comprs:
          compr_csv[compr].writerow(row[compr])
