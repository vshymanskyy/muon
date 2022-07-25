This document mostly contains some details omitted from the [original presentation](https://bit.ly/muon-present)

## Muon tags

#### `0x8A` Count

Specifies size of the following structure in **elements**.

Payload: `LEB128`  
Applies to: `Dict`, `List`

#### `0x8B` Size

Specifies size of the following structure in **bytes**.

Payload: `LEB128`  
Applies to: `Dict`, `List`, `TypedArray`

#### `0x8C` Referenced String

Instructs that the following string needs to be added to the LRU string table.

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
It also has a 3-byte payload:
- `CE BC` is utf-8 encoding of `μ` (Greek Small Letter Mu)
- `01` is Muon version (currently always 1)

Payload: `CE BC 01`  
Applies to: only appears at the beginning of file/stream once

#### `0xFF` Padding

Can be used to align the following value in memory, or as stream keep-alive signal.

Payload: none  
Applies to: anything
