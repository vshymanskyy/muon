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
    muon.add("f16").add_typed_array_f16([1.2,3.4,5.6])
    muon.add("f32").add(array('f',[1.2,3.4,5.6]))
    muon.add("f64").add(array('d',[1.2,3.4,5.6]))
    muon.add("leb128").add([
      -123456789123456789123456789,
       123456789123456789123456789
    ])
    if True:
        muon.add("chunked").start_array(array('B',[0,1,2,3,4]), chunked=True)
        muon.add_array_chunk(array('B',[5,6,7,8,9]))
        muon.add_array_chunk(array('B',[10,11,12,13,14]))
        muon.end_array_chunked()
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
        muon.add_tagged("padded", pad=4)
        muon.add_tagged("items", pad=4)
        muon.end_list()

    muon.add("count string").add_tagged("привіт", count=True)
    muon.add("count list").add_tagged(["a","b","c"], count=True)
    muon.add("count dict").add_tagged({"k1":"a", "k2":"b"}, count=True)
    muon.add("size").add_tagged({"k1":"a", "k2":"b"}, size=True)

    muon.add("multiple tags").tag_muon().add_tagged(
        ["1","2","3"], pad=2, count=True, size=True)

    muon.end_dict()

muon.end_dict()
