This document mostly contains some details omitted from the [original presentation](https://bit.ly/muon-present)

## Muon types

- Primitive:
  - **String**
  - **Typed**: integer and float numbers
  - **Special**: `True`, `False`, `Null`, `NaN`, `-Inf`, `+Inf`
- Composite:
  - **TypedArray** - array of elements of the same type, possibly chunked
  - **List** - ordered sequence of arbitrary elements
  - **Dict** - ordered associative container of key-value pairs

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

#### `0x8D` Chunked Array

MUST be used to mark a multi-chunk `TypedArray`.

Payload: none  
Applies to: `TypedArray`

#### `0x8F` Muon Format Identifier

Can be used at the start of a file or stream and allows the reader to more reliably guess that Muon format is used.  
It also has a 3-byte payload: `CE BC 31` which is utf-8 encoding of `μ1` (Greek Small Letter Mu and Muon version, currently always 1)

Payload: `CE BC 31`  
Applies to: only appears at the beginning of file/stream once

#### `0xFF` Padding

Can be used to align the following value in memory, or as stream keep-alive signal.

Payload: none  
Applies to: anything
