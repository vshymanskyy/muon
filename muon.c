#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define MUON_VAL_END  '\00'
#define MUON_LIST_BEG '\01'
#define MUON_DICT_BEG '\02'
#define MUON_META_BEG '\03'
#define MUON_BLOB_BEG '\04'

// Defines for compile-time constructiion
#define STRINGIFY(x) #x
#define uEND		 "\0"
#define uVAL(v)	     uSTR(STRINGIFY(v)) // Utility to stringify constants
#define uSTR(s)	     s uEND			    // Every value is null-terminated
#define uKV(k,v)	 uSTR(k) v		    // Key-value pairs are just pairs
#define uLIST(items) "\01" items "\00"	// LIST: 1 and 0 are like [ and ]
#define uDICT(items) "\02" items "\00"  // DICT: 2 and 0 are like { and }
#define uMETA(items) "\03" items "\00"  // ATTR: dict of attributes
#define uBLOB(s, b)  "\04" s b		    // Binary is prefixed with length

size_t muon_length(const char* beg, size_t len)
{
	unsigned depth = 0;
	for (const char *ptr = beg, *end = beg+len; ptr < end; ) {
		switch(*ptr) {
		case MUON_BLOB_BEG: {
			const long l = atol(++ptr);
			ptr += strlen(ptr) + 1;
			ptr += l;
		}	break;
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
	while(true) {
		switch(*ptr) {
		case (MUON_BLOB_BEG): {
			const int len = atoi(++ptr);
			ptr += strlen(ptr) + 1;
			printf("%*s [%i]:%s\n", depth*3, "", len, ptr);
			ptr += len;
		} break;
		case (MUON_LIST_BEG):
			printf("%*s L(\n", depth*3, "");
			depth++;
			ptr++;
			break;
		case (MUON_DICT_BEG):
			printf("%*s D(\n", depth*3, "");
			depth++;
			ptr++;
			break;
		case (MUON_META_BEG):
			printf("%*s M(\n", depth*3, "");
			depth++;
			ptr++;
			break;
		case (MUON_VAL_END):
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
		uDICT(
			uMETA(
				uKV("encoding", uSTR("utf8"))
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
	
	// For this object, size is 109
	printf("uObj sizeof: %lu\n", sizeof(uObj)-1);
	printf("uObj length: %lu\n", muon_length(uObj, sizeof(uObj)));
	
	muon_pretty_print(uObj);
  
	return 0;
}
