This document mostly contains some details omitted from the [**original presentation**](https://bit.ly/muon-present)

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

#### Dict

- Dictionary is ordered by default
- Duplicate keys are **not** allowed
- Keys can be `Integer` or `String`
- All keys must be of the same type (i.e. all strings or all ints)
  - Mixing different string encodings is explicitly allowed
- For integer keys:
  - Typed integer (`0xB0..0xB7` or `0xBB`) encoding is used for the first key
  - All subsequent keys must be of the same type and type specifier (`0xBx`) is omitted for them
  - `special` encoding for integers must **not** be used for keys

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

#### `0x8F` Muon Format Signature/Magic

Can be used at the start of a file or stream and allows the reader to [more reliably guess](https://en.wikipedia.org/wiki/List_of_file_signatures) that Muon format is used.

Payload: `B5 30 31` which is `ISO 8859-1` encoding of `μ01` (`Greek Small Letter Mu` + `version`, currently always 1)  
Applies to: only appears at the beginning of file/stream once

#### `0xFF` Padding

Can be used to align the following value in memory, or as stream keep-alive signal.

Payload: none  
Applies to: anything

---

## Deterministic Encoding

Muon Encoder can optimize it's output, selecting from multiple available encoding for the same value.  
Sometimes, it's desired to have a deterministic encoding, where the same structure maps to the same binary output.  
Specificly, for deterministic muon: `muon_generate(muon_parse(original_bytes)) == original_bytes`.  

For creating a deterministic Muon, follow the following rules:

- **String:**
  - must have a valid and deterministic encoding in UTF8 (out of scope for this document)
  - must be encoded as fixed-length if:
    - longer than 512 bytes, or
    - contains any `0x00` bytes
  - string references:
    - `0x8C` tag must **not** be applied to any strings
    - `0x8C` tag can only apply to a single, static LRU list that apperas only once at the begining of the Muon document
    - if present, LRU list must be preserved when re-encoding
    - all strings that are present in LRU list must be encoded in string ref (`0x81`) format
  - 0-terminated format is used in all other cases

- **Integer:**
  - `0..9` must use special encoding (`0xA0..0xA9`)
  - LEB128 encoding (`0xBB`) is used for all other standalone integers
- **Float:**
  - `NaN`, `-Inf`, `+Inf` must be encoded using special encoding (`0xAD..0xAF`)
  - float64 (`0xBA`) format is used in all other cases
- **TypedArray:**
  - must preserve their type when re-encoding
- **Dict:**
  - is ordered
  - must preserve key type
- **Tags:**
  - `count`,`size`,`padding` tags must **not** be used
  - magic tag `0x8F` must be ignored when comparing deterministic documents (i.e. may be present or missing)
