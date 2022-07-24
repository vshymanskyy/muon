# MUON
µON is a compact and **simple** object notation format with some interesting  properties.  
It is intended to be used in IoT applications, for example as payload in MQTT or as stand-alone communication protocol.

µ[mju:] stands for "micro"

*If you have any ideas/comments, please feel free to post them [here](https://github.com/vshymanskyy/MUON/issues).*

### µON types

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

### µON features:

* Cross-platform
* Easy to parse and generate, even on microcontrollers (see the grammar below!)
  * You can interpret/produce it on-fly
* Uses [control characters](http://en.wikipedia.org/wiki/Control_character) 0x00, 0x01, 0x25, 0x29-0x31 as markers
* Supports raw binary values and typed arrays
* Virtually unlimited size of objects and values
* Data is ready to be used "in-place" (for example, is not escaped/modified)
  * All strings are already zero-terminated
  * No need to pre-parse data (you can do this, of course)
* Mostly covers features of JSON and XML to minimize information loss during conversion to MUON

#### µON compared to JSON and XML:

* µON is more compact than JSON (approx. 25%, depends on the object)
* µON is a binary format (so not human-readable.. most JSON documents are also not human-readable anyway)
  * Can be easily transformed into a readable form
* "Meta" is similar to attribute set in XML
  * It can be any object (contain tree structures)

#### µON grammar

This grammar can be visualized using http://www.bottlecaps.de/rr/ui :

```
object ::= ( #x01 object ) ?                     /* meta */
           ( any-utf8-except-control* #x00       /* text */
           | #x16 [0-9]+ #x00 raw-data           /* blob */
           | #x1F (                              /* special */
                    'T'                             /* true */
                  | 'F'                             /* false */
                  | 'X'                             /* null */
                  | '?'                             /* undef */
                  )
           | #x1E object* #x25                   /* list */
           | #x1D (any-utf8 #x00 object)* #x25   /* dict */
           )
```

![alt tag](docs/muon.png?raw=true)

