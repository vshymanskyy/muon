# MUON
µON is object notation format with some good properties for M2M communication.  
It is intended to be used in IoT applications, for example as payload in MQTT or as stand-alone communication protocol.

µ[mju:] stands for "micro", like microcontroller is sometimes abbreviated "µC".

*Attention! This project is on an early stage of development,  and generally should be treated as RFC  (Request for comments).  If you have any ideas/comments, please feel free to post them [here](https://github.com/vshymanskyy/MUON/issues/1).*

#### µON types
Primitive:
* String
* Binary
* Special (true, false, null)

Composite:
* List (sequence of elements)
* Dict (associative container of key-value pairs)
* Meta (an object that contains meta-information)

#### µON features:
* Cross-platform
* Easy to parse and generate, even on microcontrollers (see the grammar below!)
  * You can interpret/produce it on-fly
* Uses [control characters](http://en.wikipedia.org/wiki/Control_character) 0..5 as markers
* Supports raw binary values
* Supports UTF-8 string values
* Unlimited size of objects
* Data is ready to be used "in-place" (for example, is not escaped/modified)
  * All strings are already zero-terminated
  * No need to pre-parse data (but you can do this, of course)
* Mostly covers features of JSON and XML to minimize information loss during conversion to MUON

#### µON compared to JSON and XML:
* µON is more compact than JSON (approx. 25%, depends on the object)
* µON is binary format (so not human-readable)
  * But can easily be transformed into a readable form
* Almost all values are stored as strings
  * But keys and values are not quoted. They are zero-terminated instead
  * So there's no need to escape "'&<>...
* "Meta" is similar to attribute set in XML
  * But it can be any object, so can contain tree structures

#### µON grammar
This grammar can be visualized using http://www.bottlecaps.de/rr/ui :

```
object ::= ( #x13 object ) ?                     /* meta */
           ( any-utf8-except-control* #x00       /* text */
           | #x01 [0-9]* #x00 raw-data           /* blob */
           | #x02 (                              /* special */
                    'T'                             /* true */
                  | 'F'                             /* false */
                  | 'X'                             /* null */
                  | '?'                             /* undef */
                  )
           | #x11 object* #x10                   /* list */
           | #x12 (any-utf8 #x00 object)* #x10   /* dict */
           )
```

![alt tag](docs/object.png?raw=true)

