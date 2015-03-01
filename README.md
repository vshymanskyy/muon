# MUON
µON is object notation format with some good properties for M2M communication.

µ[mju:] stands for "micro", like microcontroller is sometimes abbreviated "µC".

#### µON types
Primitive:
* String
* Binary

Composite:
* List (sequence of elements)
* Dict (associative container of key-value pairs)
* Meta (a Dict that contains meta-information )

#### µON features:
* Cross-platform
* Easily parseable, even on microcontrollers (see the grammar below!)
  * Actually you can just interpret it on-fly
* Uses control characters 0..4 as markers
* Supports raw binary values
* Supports UTF-8 string values
* All strings are zero-terminated
* Unlimited size of objects
* Data can be used "in-place", no need to pre-parse data (but you can do this, of course)
* Mostly covers features of JSON and XML to minimize information loss during conversion to MUON

#### µON compared to JSON and XML:
* µON is binary format (so not human-readable)
  * But can easily be transformed into a readable form
* Almost all values are stored as strings
  * But keys and values are not quoted. They are zero-terminated instead
  * So there's no need to escape "'&<>...
* "Meta" is similar to attribute set in XML
  * But it is equivalent to Dict, so can contain tree structures

#### µON grammar

    object ::= ( '\4' (string '\0' object)+ '\0' )?  /* optional meta-information */
               ( string '\0'                         /* string */
               | '\1' digits '\0' raw-data           /* binary */
               | '\2' object* '\0'                   /* list */
               | '\3' (string '\0' object)* '\0'     /* dict */
               )
    string ::= any-utf8-except-control*

![alt tag](docs/object.png?raw=true)
