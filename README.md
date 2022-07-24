# muon
A compact and **simple** object notation. µ[mju:] stands for "micro". See [**presentation**](https://docs.google.com/presentation/d/1MosK6LTy_Rr32eF6HKej6UEtf9vBzdbeSF6YPb1_e4A/present) for more details.

**If you have any ideas/comments, please feel free to [post them here](https://github.com/vshymanskyy/muon/issues).**

Muon has some interesting  properties:
- Every `UTF8` string is a valid `muon` object
- Uses gaps in the `UTF8` encoding space to encode things like `[` `]` `{` `}` etc.
- More compact than `JSON` (approx. 25%, depends on the object). On par/outperforms `CBOR`, `MsgPack`, `UBJSON`
- Unlimited size of objects and values
- Data is ready to be used in-place without pre-processing
- Supports raw binary values and typed arrays
- Mostly covers features of JSON and XML to minimize information loss during conversion to MUON
- See [**presentation**](https://docs.google.com/presentation/d/1MosK6LTy_Rr32eF6HKej6UEtf9vBzdbeSF6YPb1_e4A/present) for more details

Future goals:
- Well-specified (little or no room for implementation-specific behavior / vendor-specific extensions)

![alt tag](docs/muon.png?raw=true)

## Muon types

Primitive:
* String
* Integer
* Typed (integers and floats)
* Special: `True`, `False`, `Null`, `NaN`, `-Inf`, `+Inf`

Composite:
* TypedArray
* List (sequence of elements)
* Dictionary (associative container of key-value pairs)
* Attribute (an object that contains meta-information)

