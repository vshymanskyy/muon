/*
  Legend:
    Reference     ⮬
    Fixed length  📐
    Muon magic    μ
    LRU           📓 list, 🔖 tag
    Count         ᚒ
    Size          𝄩
    Padding       ⎵
*/
μ📓[
  "string value 1",
  "string value 2",
]{
  "strings": {
    "key1": ⮬1"string value 1",
    "key2": ⮬0"string value 2",
    "key3": 🔖"string value 3",
    "key4": 🔖"string value 4",
    "key5": 📐24"string\u0000containing\u0000\u0000zeros",
    "key3-ref": ⮬1"string value 3",
    "key4-ref": ⮬0"string value 4",
  },
  "special": {
    "int0": 0,
    "int1": 1,
    "int2": 2,
    "int3": 3,
    "int4": 4,
    "int5": 5,
    "int6": 6,
    "int7": 7,
    "int8": 8,
    "int9": 9,
    "false": False,
    "true": True,
    "null": None,
    "nan": nan,
    "neg inf": -inf,
    "pos inf": inf,
  },
  "typed values": {
    "i8 ": b-123,
    "i16": h-1234,
    "i32": l-12356789,
    "i64": q-1234567891234567,
    "u8 ": B123,
    "u16": H1234,
    "u32": L12356789,
    "u64": Q1234567891234567,
    "f16": e1.0,
    "f32": f123123.125,
    "f64": d123.123123123123,
    "big neg int": -123456789123456789123456789,
    "big pos int": 123456789123456789123456789,
  },
  "typed arrays": {
    "i8 ": b📐9(-4,-3,-2,-1,0,1,2,3,4,),
    "i16": h📐9(-4,-3,-2,-1,0,1,2,3,4,),
    "i32": l📐9(-4,-3,-2,-1,0,1,2,3,4,),
    "i64": q📐9(-4,-3,-2,-1,0,1,2,3,4,),
    "u8 ": B📐5(0,1,2,3,4,),
    "u16": H📐5(0,1,2,3,4,),
    "u32": L📐5(0,1,2,3,4,),
    "u64": Q📐5(0,1,2,3,4,),
    "f16": e📐3(1.2001953125,3.400390625,5.6015625,),
    "f32": f📐3(1.2000000476837158,3.4000000953674316,5.599999904632568,),
    "f64": d📐3(1.2,3.4,5.6,),
    "leb128": 📐2(-123456789123456789123456789,123456789123456789123456789,),
    "chunked": B📐5(0,1,2,3,4,)B📐5(5,6,7,8,9,)B📐5(10,11,12,13,14,),
  },
  "lists": {
    "3 strings": [
      "a",
      "simple",
      "list",
    ],
    "2 empty lists": [
      [
      ],
      [
      ],
    ],
    "2 empty dicts": [
      {
      },
      {
      },
    ],
  },
  "dicts": {
    "typed keys": "#TODO",
  },
  "tags": {
    "magic": μ"should be skipped",
    "pad before": [
      ⎵⎵⎵⎵"padded",
      ⎵⎵⎵⎵"items",
    ],
    "count string": ᚒ6"привіт",
    "count list": ᚒ3[
      "a",
      "b",
      "c",
    ],
    "count dict": ᚒ2{
      "k1": "a",
      "k2": "b",
    },
    "size": 𝄩12{
      "k1": "a",
      "k2": "b",
    },
    "multiple tags": μ⎵⎵ᚒ3𝄩8[
      "1",
      "2",
      "3",
    ],
  },
}
