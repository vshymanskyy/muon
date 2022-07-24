#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>

// Defines for compile-time construction
#define uEND         "\0"
#define uTRUE        "\02" "1"
#define uFALSE       "\02" "0"
#define uNULL        "\02" "-"
#define STRINGIFY(x) #x
#define uVAL(v)      uSTR(STRINGIFY(v)) // Utility to stringify constants
#define uSTR(s)      s uEND             // Every value is null-terminated
#define uKV(k,v)     uSTR(k) v          // Key-value pairs are just pairs
#define uBLOB(s, b)  "\01" s b          // Binary is prefixed with length
#define uLIST(items) "\03" items "\00"  // LIST: 3 and 0 are like [ and ]
#define uDICT(items) "\04" items "\00"  // DICT: 4 and 0 are like { and }
#define uMETA(obj)   "\05" obj          // META: prefixed metainformation

// Defines for run-time handling
#define MUON_VAL_END  '\00'
#define MUON_BLOB_BEG '\01'
#define MUON_SPEC_BEG '\02'
#define MUON_LIST_BEG '\03'
#define MUON_DICT_BEG '\04'
#define MUON_META_BEG '\05'

size_t muon_pretty_print(const char* beg, size_t max_len)
{
    unsigned depth = 0;
    const char *ptr = beg, *end = beg+max_len;
    while (ptr < end) {
    	const char ch = *ptr;
        switch(ch) {
        case MUON_BLOB_BEG: {
            const int len = atoi(++ptr);
            ptr += strlen(ptr) + 1;
            printf("%*s [%i]:%s\n", depth*3, "", len, ptr);
            ptr += len;
        } break;
        case MUON_LIST_BEG:
            printf("%*s L(\n", depth*3, "");
            depth++;
            ptr++;
            break;
        case MUON_DICT_BEG:
            printf("%*s D(\n", depth*3, "");
            depth++;
            ptr++;
            break;
        case MUON_META_BEG:
            printf("[meta]");
            ptr += muon_pretty_print(ptr+1, end-ptr)+1;
            break;
        case MUON_VAL_END:
            depth--;
            ptr++;
            printf("%*s )\n", depth*3, "");
            break;
        default:
            printf("%*s %s\n", depth*3, "", ptr);
            ptr += strlen(ptr) + 1;
        }
        if (!depth && ch != MUON_META_BEG)
            return ptr-beg;
    }
    return max_len;
}




// Compile-time construction
static const char uObj[] =
    uMETA(uDICT(
        uKV("encoding", uSTR("UTF-8"))
    ))
    uDICT(
        uKV("abc", uVAL(123))
        uKV("def", uSTR("456"))
        uKV("map", uDICT(
            uKV("k1", uSTR("v1"))
            uKV("k2", uSTR("v2"))
            uKV("k3", uLIST(
                "i0" uEND "i1" uEND "i2" uEND "i3" uEND
            ))
        ))
        uKV("list", uLIST(
            "i0" uEND "i1" uEND "i2" uEND "i3" uEND
        ))
    );

/*
 * This produces 90 bytes:
 *
 *   "\05"
 *   	"\04"
 *   		"encoding" "\0" "UTF-8" "\0"
 *   	"\00"
 *   "\04"
 *   	"abc" "\0" "123" "\0"
 *   	"def" "\0" "456" "\0"
 *   	"map" "\0" "\04"
 *   		"k1" "\0" "v1" "\0"
 *   		"k2" "\0" "v2" "\0"
 *   		"k3" "\0" "\03"
 *   			"i0" "\0" "i1" "\0" "i2" "\0" "i3" "\0"
 *   		"\00"
 *   	"\00"
 *   	"list" "\0" "\03"
 *   		"i0" "\0" "i1" "\0" "i2" "\0" "i3" "\0"
 *   	"\00"
 *   "\00"
 *
 * Which can be interpreted as:
 *
 *   META-DICT(
 *   	encoding, UTF-8,
 *   )
 *   DICT(
 *   	abc, 123,
 *   	def, 456,
 *   	map, DICT(
 *   		k1, v1,
 *   		k2, v2,
 *   		k3, LIST(
 *   			i0, i1, i2, i3,
 *   		)
 *   	)
 *   	list, LIST(
 *   		i0, i1, i2, i3,
 *   	)
 *   )
 *
 */

int main()
{
    size_t len = muon_pretty_print(uObj, sizeof(uObj));

    assert(len == sizeof(uObj)-1);

    printf("uObj length: %lu\n", len);

    return 0;
}
