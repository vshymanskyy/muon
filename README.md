# muon
A compact and **simple** object notation. µ[mju:] stands for "micro".

```log
File extension:   .mu
MIME type:        application/muon
Endianness:       little-endian
```

Muon has some interesting  properties (see [**presentation**](https://bit.ly/muon-present) for more details):
- Every `UTF8` string is a valid `muon` object
- Gaps in the `UTF8` encoding space are used to encode things like `[` `]` `{` `}` etc.
- More compact than `JSON` (~25% smaller). On par or outperforms `CBOR`, `MsgPack`, `UBJSON`
- Unlimited size of objects and values
- Data is ready to be used in-place without pre-processing
- Supports raw binary values and typed arrays
- Optionally, can contain count of elements (and size in bytes) of all structures for efficient document processing

Future goals:
- Strict specification (little or no room for implementation-specific behavior / vendor-specific extensions)

## Try it yourself

```sh
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

## Muon types

- Primitive:
  - **String**
  - **Typed**: integer and float numbers
  - **Special**: `True`, `False`, `Null`, `NaN`, `-Inf`, `+Inf`
- Composite:
  - **TypedArray** - array of elements of the same type, possibly chunked
  - **List** - sequence of arbitrary elements
  - **Dict** - associative container of key-value pairs
  - **Attr** - dictionary that contains meta-information

---

**Disclaimer: the notation is still Work In Progress.**
If you have any ideas or comments, please feel free to [post them here](https://github.com/vshymanskyy/muon/issues).

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
