# MUON
µON is object notation format with some good properties for M2M communication.  
It is intended to be used in IoT applications, for example as payload in MQTT or as stand-alone communication protocol.

µ[mju:] stands for "micro", like microcontroller is sometimes abbreviated "µC".

*Attention! This project is on an early stage of development,  and generally should be treated as RFC  (Request for comments).  If you have any ideas/comments, please feel free to post them [here](https://github.com/vshymanskyy/MUON/issues/1).*

#### µON types
Primitive:
* String
* Binary
* Special (true, false, null, undef)

Composite:
* List (sequence of elements)
* Dict (associative container of key-value pairs)
* Meta (an object that contains meta-information)

#### µON features:
* Cross-platform
* Easy to parse and generate, even on microcontrollers (see the grammar below!)
  * You can interpret/produce it on-fly
* Uses [control characters](http://en.wikipedia.org/wiki/Control_character) 0x00, 0x01, 0x25, 0x29-0x31 as markers
* Supports raw binary values
* Supports UTF-8 string values
* Virtually unlimited size of objects and values
* Data is ready to be used "in-place" (for example, is not escaped/modified)
  * All strings are already zero-terminated
  * No need to pre-parse data (you can do this, of course)
* Mostly covers features of JSON and XML to minimize information loss during conversion to MUON

#### µON compared to JSON and XML:
* µON is more compact than JSON (approx. 25%, depends on the object)
* µON is binary format (so not human-readable)
  * Can easily be transformed into a readable form
* Almost all values are stored as strings
  * Keys and values are not quoted, they are zero-terminated instead
  * There's no need to escape "'&<>...
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

![alt tag](docs/object.png?raw=true)

