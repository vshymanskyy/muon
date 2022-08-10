/*
  Values:
    Reference     ⮬
    Fixed length  📐

  Tags:
    Muon magic    μ
    LRU           📓 list, 🔖 string
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
    "i8 ": b📐9(...),
    "i16": h📐9(...),
    "i32": l📐9(...),
    "i64": q📐9(...),
    "u8 ": B📐5(...),
    "u16": H📐5(...),
    "u32": L📐5(...),
    "u64": Q📐5(...),
    "f16": "#TODO",
    "f32": f📐3(...),
    "f64": d📐3(...),
    "leb128": 📐2(...),
    "chunked": "#TODO",
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
    "count": "#TODO",
    "size": "#TODO",
    "multiple tags": μ⎵⎵"#TODO",
  },
}
