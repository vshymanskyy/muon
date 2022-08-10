#!/usr/bin/env python3

import muon
import math
from array import array

f = open("sample.mu", "wb")

muon = muon.Writer(f)
muon.tag_muon()
muon.add_lru_list(["string value 1", "string value 2"])

muon.add_lru_dynamic([
    "string value 3", "string value 4"
])

muon.start_dict()

if True:
    muon.add("strings").start_dict()
    muon.add("key1").add("string value 1")
    muon.add("key2").add("string value 2")
    muon.add("key3").add("string value 3")
    muon.add("key4").add("string value 4")
    muon.add("key5").add("string\x00containing\x00\x00zeros")
    muon.add("key3-ref").add("string value 3")
    muon.add("key4-ref").add("string value 4")
    muon.end_dict()

if True:
    muon.add("special").start_dict()
    for i in range(10):
        muon.add("int"+str(i)).add(i)
    muon.add("false").add(False)
    muon.add("true").add(True)
    muon.add("null").add(None)
    muon.add("nan").add(float("nan"))
    muon.add("neg inf").add(float("-inf"))
    muon.add("pos inf").add(float("+inf"))
    muon.end_dict()

if True:
    muon.add("typed values").start_dict()
    muon.add("i8 ").add(-123)
    muon.add("i16").add(-1234)
    muon.add("i32").add(-12356789)
    muon.add("i64").add(-1234567891234567)
    muon.add("u8 ").add(123)
    muon.add("u16").add(1234)
    muon.add("u32").add(12356789)
    muon.add("u64").add(1234567891234567)
    muon.add("f16").add(1.0)
    muon.add("f32").add(123123.125)
    muon.add("f64").add(123.123123123123)
    muon.add("big neg int").add(-123456789123456789123456789)
    muon.add("big pos int").add( 123456789123456789123456789)
    muon.end_dict()

if True:
    muon.add("typed arrays").start_dict()
    muon.add("i8 ").add(array('b',[-4,-3,-2,-1,0,1,2,3,4]))
    muon.add("i16").add(array('h',[-4,-3,-2,-1,0,1,2,3,4]))
    muon.add("i32").add(array('l',[-4,-3,-2,-1,0,1,2,3,4]))
    muon.add("i64").add(array('q',[-4,-3,-2,-1,0,1,2,3,4]))
    muon.add("u8 ").add(array('B',[0,1,2,3,4]))
    muon.add("u16").add(array('H',[0,1,2,3,4]))
    muon.add("u32").add(array('L',[0,1,2,3,4]))
    muon.add("u64").add(array('Q',[0,1,2,3,4]))
    muon.add("f16").add("#TODO")
    muon.add("f32").add(array('f',[1.2,3.4,5.6]))
    muon.add("f64").add(array('d',[1.2,3.4,5.6]))
    muon.add("leb128").add([
      -123456789123456789123456789,
       123456789123456789123456789
    ])
    muon.add("chunked").add("#TODO")
    muon.end_dict()

if True:
    muon.add("lists").start_dict()
    muon.add("3 strings").add(["a","simple","list"])
    muon.add("2 empty lists").add([[],[]])
    muon.add("2 empty dicts").add([{},{}])
    muon.end_dict()

if True:
    muon.add("dicts").start_dict()
    muon.add("typed keys").add("#TODO")
    muon.end_dict()

if True:
    muon.add("tags").start_dict()
    muon.add("magic").tag_muon().add("should be skipped")
    if True:
        muon.add("pad before").start_list()
        muon.tag_pad(4).add("padded")
        muon.tag_pad(4).add("items")
        muon.end_list()

    muon.add("count").add("#TODO")
    muon.add("size").add("#TODO")
    muon.add("multiple tags").tag_muon().tag_pad(2).add("#TODO")

    muon.end_dict()

muon.end_dict()
