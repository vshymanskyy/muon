This document mostly contains some details omitted from the [original presentation](https://bit.ly/muon-present)

## Muon tags

#### `0x8A` Count

Specifies size of the following structure in **elements**. Payload is encoded in `LEB128`.

Applies to: `Dict`, `List`

#### `0x8B` Size

Specifies size of the following structure in **bytes**. Payload is encoded in `LEB128`.

Applies to: `Dict`, `List`, `TypedArray`

#### `0x8C` Referenced String

Instructs that the following string needs to be added to the LRU string table.

Applies to: `String`.

Notes:
1. sdfsdf

#### `0x8D` Chunked Array

#### `0x8F` Muon Format Identifier

Can be used at the start of a file or stream that allows the reader to more reliably guess that Muon format is used for encoding.
It also has a 3-byte payload, so the complete tag looks like `8F CE BC 01`.
- `CE BC` is utf-8 encoding of `μ` (Greek Small Letter Mu)
- `01` is Muon version (currently always 1)

Should only appear at the beginning of file/stream once.
