# muon
A compact and **simple** object notation. µ[mju:] stands for "micro".

```log
File extension:   .mu
MIME type:        application/muon
Endianness:       little-endian
Signature/Magic:  optional, 8F B5 30 31 ["�µ01"] @ 0x0
```

Muon has some interesting  properties (see [**presentation**](https://bit.ly/muon-present) and [**docs**](./docs/README.md)):
- Every null-terminated `UTF8` string is also a valid `muon` object
- Gaps in the `UTF8` encoding space are used to encode things like `[` `]` `{` `}` etc.
- Muon is **self-describing and schemaless**, just like `JSON` (unlike `Protobuf` and `FlatBuffers`)
- **Compact** (~10..50% smaller than `JSON`). On par or outperforms `CBOR`, `MsgPack`, `UBJSON`
- **Unlimited** size of objects and values
- Data is ready to be used **in-place** without pre-processing
- Supports **raw binary** data (values and `TypedArrays`)
- Can _optionally_ contain count of elements (and size in bytes) of all structures for efficient document processing, similar to `BSON`

Future goals:
- Strict specification (little or no room for implementation-specific behavior / vendor-specific extensions)

## Try it yourself

```sh
pip install leb128
python3 muon_python/json2mu.py ./data/AirlineDelays.min.json ./AirlineDelays.mu
python3 muon_python/mu2json.py ./AirlineDelays.mu > ./AirlineDelays.json
```

Run benchmarks:
```sh
./muon_python/extra/json-analyze.py ./data/*.json ./data/small/*.json
./muon_python/mu-benchmark.py ./data/*.json ./data/small/*.json
```

## Muon structure

[![alt tag](docs/muon.png?raw=true)](https://bit.ly/muon-present)

See more [**in documentation**](./docs/README.md).

**Disclaimer: the notation is still Work In Progress.**
If you have any ideas or comments, please feel free to [post them here](https://github.com/vshymanskyy/muon/issues).

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
