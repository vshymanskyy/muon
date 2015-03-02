# MUON
µON is object notation format with some good properties for M2M communication.
It is intended to be used in IoT applications, for example as payload in MQTT or as stand-alone communication protocol.

µ[mju:] stands for "micro", like microcontroller is sometimes abbreviated "µC".

**Attention! This project is on an early stage of developpment, and generally should be treated as RFC  (Request for comments). If you have any ideas/comments, you can post them [here](https://github.com/vshymanskyy/MUON/issues/1)**

#### µON types
Primitive:
* String
* Binary
* Special (true, false, null)

Composite:
* List (sequence of elements)
* Dict (associative container of key-value pairs)
* Meta (a Dict that contains meta-information )

#### µON features:
* Cross-platform
* Easy to parse and generate, even on microcontrollers (see the grammar below!)
  * You can interpret/produce it on-fly
* Uses control characters 0..5 as markers
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
  * But it is equivalent to Dict, so can contain tree structures

#### µON grammar
This grammar can be visualized using http://www.bottlecaps.de/rr/ui :

    object ::= ( '\5' object )?                      /* optional meta-information */
               ( string '\0'                         /* string */
               | '\1' length raw-data                /* binary */
               | '\2' (                              /* special */
                        '1'                             /* true */
                      | '0'                             /* false */
                      | '-'                             /* null */
                      )
               | '\3' object* '\0'                   /* list */
               | '\4' (string '\0' object)* '\0'     /* dict */
               )
    
    string ::= any-utf8-except-control*
    length ::= [#x80-#xFF]* [#x00-#x7F]

Length of binary is encoded like in MQTT: each byte encodes 128 values and a "continuation bit". The last byte of length has most significant bit set to 0.

![alt tag](docs/object.png?raw=true)

