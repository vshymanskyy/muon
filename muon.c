#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Defines for compile-time constructiion
#define uEND         "\0"
#define uTRUE        "\02" "1"
#define uFALSE       "\02" "0"
#define uNULL        "\02" "0"
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

size_t muon_length(const char* beg, size_t len)
{
    unsigned depth = 0;
    const char *ptr = beg, *end = beg+len;
    while (ptr < end) {
        switch(*ptr) {
        case MUON_BLOB_BEG: {
            const long l = atol(++ptr);
            ptr += strlen(ptr) + 1;
            ptr += l;
        }    break;
        case MUON_LIST_BEG:
        case MUON_DICT_BEG:
        case MUON_META_BEG:
            depth++;
            ptr++;
            break;
        case MUON_VAL_END:
            depth--;
            ptr++;
            break;
        default:
            ptr += strlen(ptr) + 1;
        }
        if (!depth)
            return ptr-beg;
    }
    return len;
}

void muon_pretty_print(const char* ptr)
{
    unsigned depth = 0;
    while (1) {
        switch(*ptr) {
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
            printf("%*s M(\n", depth*3, "");
            depth++;
            ptr++;
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
        if (!depth)
            return;
    }
}

int main()
{
    // Compile-time construction
    const char uObj[] =
        uMETA(uDICT(
            uKV("version", uSTR("1.0"))
            uKV("encoding", uSTR("UTF-8"))
        ))
        uDICT(
            uMETA(
                uKV("meta of dict", uSTR("test"))
            )
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
            uKV("bin", uBLOB(uVAL(5), "\1\2\3\4\5"))
            uKV("last", uSTR("val"))
        );
    
    printf("uObj sizeof: %lu\n", sizeof(uObj)-1);
    printf("uObj length: %lu\n", muon_length(uObj, sizeof(uObj)));
    
    muon_pretty_print(uObj);
  
    return 0;
}
