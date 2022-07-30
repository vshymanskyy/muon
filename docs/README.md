This document mostly contains some details omitted from the [**original presentation**](https://bit.ly/muon-present)

[![alt tag](muon.png?raw=true)](https://bit.ly/muon-present)

## Muon types

- Primitive:
  - **String**
  - **Typed**: integer and float numbers
  - **Special**: `True`, `False`, `Null`, `NaN`, `-Inf`, `+Inf`
- Composite:
  - **TypedArray** - array of elements of the same type, possibly chunked
  - **List** - ordered sequence of arbitrary objects
  - **Dict** - ordered associative container of key-value pairs

#### String

`0x81` reference to a string in an LRU list, counting from top

`0x82` fixed-length string. `len` is in **bytes**. Useful when encoding:
- long strings (>512 bytes)
- strings that contain `null characters (0x00)`

#### Integer

`0xA0..0xA9` - single-digit integers (for short encoding)  
`0xB0..0xB7` - typed integers (Little-Endian)  
`0xBB` - LEB128 encoded integers

#### Float

`0xB8` - float16, `0xB9` - float32, `0xBA` - float64 (all are Little-Endian)

#### Special value

```c
0xAA  False
0xAB  True
0xAC  Null/None
0xAD  NaN
0xAE  -Inf
0xAF  +Inf
```

#### TypedArray

`0x84` - `TypedArray`  
`0x85` - chunked `TypedArray`. the `count`+`values` sequence is repeated until a zero-length chunk

#### List

A sequence of arbitrary Muon objects

#### Dictionary

- Dictionary is ordered by default
- Duplicate keys are not allowed
- Keys can be `Integer` or `String`
- All keys should be of the same type (not of specific encoding!)
- If typed integer (`0xB0..0xB7`) is used for the first key, all subsequent keys **MUST** of the same type, and type specifier (`0xBx`) is omitted for them

---

## Muon tags

#### `0x8A` Count

Specifies size of the following structure in **elements**.  
This tag can optioanlly added to enable efficient resource allocation by the parser.

Payload: `LEB128`  
Applies to: `Dict`, `List`

#### `0x8B` Size

Specifies size of the following structure in **bytes**.  
This tag can optioanlly added to enable efficient parsing/filtering/scanning of the document.

Payload: `LEB128`  
Applies to: `Dict`, `List`, `TypedArray`

#### `0x8C` Referenced String

Instructs that the following string needs to be added to the LRU string list.

Payload: none  
Applies to: `String`, `List`

Notes:
1. Once the list is full, items are discarded from the beginning
2. If applied to a String Reference (type `0x81`), associated string is moved to the top of the LRU list

#### `0x8F` Muon Format Identifier

Can be used at the start of a file or stream and allows the reader to more reliably guess that Muon format is used.  
It also has a 3-byte payload: `CE BC 31` which is utf-8 encoding of `μ1` (Greek Small Letter Mu and Muon version, currently always 1)

Payload: `CE BC 31`  
Applies to: only appears at the beginning of file/stream once

#### `0xFF` Padding

Can be used to align the following value in memory, or as stream keep-alive signal.

Payload: none  
Applies to: anything
