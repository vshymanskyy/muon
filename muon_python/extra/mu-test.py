#!/usr/bin/env python3

import sys, io, os

import json
import muon

def pp(data):
    return json.dumps(data, indent=4, sort_keys=True)


for ifn in sys.argv[1:]:

    with open(ifn) as f:
        data = json.load(f)

    orig_json = pp(data)

    out = io.BytesIO()
    m = muon.Writer(out)
    m.detect_arrays = False
    m.detect_binary = False
    m.detect_numstr = False

    m.add(data)

    #print(out.getvalue())

    out.seek(0)

    m = muon.Reader(out)
    res = m.read_object()
    res_json = pp(res)

    if res_json == orig_json:
        print(f"{ifn: <80} OK")
    else:
        print(f"{ifn: <80}: FAIL")
