import sys, io, math, struct, array, typing
from collections.abc import Mapping, Sequence
from collections import deque, Counter

MUON_MAGIC = b'\x8F\xB5\x30\x31'
BIG_ENDIAN = sys.byteorder == "big"

class DictBuilder:
    def __init__(self):
        self._count = Counter()

    def add(self, val):
        if val is None:
            pass
        elif isinstance(val, str):
            self.add_str(val)
        elif isinstance(val, Sequence):
            for v in val:
                self.add(v)
        elif isinstance(val, Mapping):
            for k, v in val.items():
                self.add_str(k)
                self.add(v)

    def add_str(self, val):
        if len(val) > 1:
            self._count.update([val])

    # TODO: calculate static and dynamic LRU strings separately

    """
    static LRU requires:
      3 bytes once +
        2+ bytes for each occurance

    dynamic LRU requires:
      1 bytes for first occurance
      2+ bytes for the rest

    """

    def get_dict(self, size = 64):
        for k, v in self._count.items():
            self._count[k] = (v-1) * len(k)

        res = filter(lambda x: x[1] > 5, self._count.most_common())
        return list(map(lambda x: x[0], res))[0:size]

"""
Integer encoding
"""

def uleb128encode(x: int) -> bytearray:
    assert x >= 0
    r = []
    while True:
        byte = x & 0x7f
        x = x >> 7
        if x == 0:
            r.append(byte)
            return bytearray(r)
        r.append(0x80 | byte)

def uleb128decode(b: bytearray) -> int:
    r = 0
    for x, e in enumerate(b):
        r = r + ((e & 0x7f) << (x * 7))
    return r

def uleb128read(r: typing.BinaryIO) -> int:
    a = bytearray()
    while True:
        b = ord(r.read(1))
        a.append(b)
        if (b & 0x80) == 0:
            break
    return uleb128decode(a)

def sleb128encode(i: int) -> bytearray:
    r = []
    while True:
        byte = i & 0x7f
        i = i >> 7
        if (i == 0 and byte & 0x40 == 0) or (i == -1 and byte & 0x40 != 0):
            r.append(byte)
            return bytearray(r)
        r.append(0x80 | byte)

def sleb128decode(b: bytearray) -> int:
    r = 0
    for i, e in enumerate(b):
        r = r + ((e & 0x7f) << (i * 7))
    if e & 0x40 != 0:
        r |= - (1 << (i * 7) + 7)
    return r

def sleb128read(r: typing.BinaryIO) -> int:
    a = bytearray()
    while True:
        b = ord(r.read(1))
        a.append(b)
        if (b & 0x80) == 0:
            break
    return sleb128decode(a)

"""
Array helpers
"""

def detect_array_type(arr):
    if len(arr) < 2:
          return None

    res = None
    if isinstance(arr[0], int):
        res = 'int'
    elif isinstance(arr[0], float):
        res = 'float'

    for val in arr:
        if isinstance(val, bool):
            return None
        elif isinstance(val, int):
            pass
        elif isinstance(val, float):
            if res == 'int':
                res == 'float' # extend to float
        else:
            return None
    return res

def get_array_type_code(t):
    if   t == 0xB0: return 'b'
    elif t == 0xB1: return 'h'
    elif t == 0xB2: return 'l'
    elif t == 0xB3: return 'q'

    elif t == 0xB4: return 'B'
    elif t == 0xB5: return 'H'
    elif t == 0xB6: return 'L'
    elif t == 0xB7: return 'Q'

    elif t == 0xB8: raise Exception(f"TypedArray: f16 not supported")
    elif t == 0xB9: return 'f'
    elif t == 0xBA: return 'd'
    else: raise Exception(f"No array type for {hex(t)}")

def get_typed_array_marker(t):
    if   t == 'b': return 0xB0
    elif t == 'h': return 0xB1
    elif t == 'l': return 0xB2
    elif t == 'q': return 0xB3

    elif t == 'B': return 0xB4
    elif t == 'H': return 0xB5
    elif t == 'L': return 0xB6
    elif t == 'Q': return 0xB7

    elif t == 'f': return 0xB9
    elif t == 'd': return 0xBA
    else: raise Exception(f"No encoding for array '{t}'")

"""
Muon formatter and parser
"""

class Writer:
    def __init__(self, out):
        self.out = out
        self.lru = deque(maxlen=512)
        self.lru_dynamic = []

        self.detect_arrays = True

    def tag_muon(self):
        self.out.write(MUON_MAGIC)
        return self

    def tag_pad(self, count=1):
        self.out.write(b'\xFF' * count)
        return self

    def tag_count(self, count):
        self.out.write(b'\x8A' + uleb128encode(count))
        return self

    def tag_size(self, size):
        self.out.write(b'\x8B' + uleb128encode(size))
        return self

    def add_lru_dynamic(self, table):
        self.lru_dynamic.extend(list(table))
        return self

    def add_lru_list(self, table):
        table = list(table)
        self.lru.extend(table)

        self.out.write(b'\x8C')
        self.start_list()
        for s in table:
            self.out.write(s.encode('utf8') + b'\x00')
        self.end_list()
        return self

    def add(self, val):
        if isinstance(val, str):
            self.add_str(val)
        elif val is None:
            self.out.write(b'\xAC')
        elif isinstance(val, bool):
            self.out.write(b'\xAB' if val else b'\xAA')
        elif isinstance(val, int):
            if val >= 0 and val <= 9:
                self.out.write(bytes([0xA0 + val]))
            else:
                enc = sleb128encode(val)
                lenc = len(enc)
                if val < 0:
                    if val >= -0x80:
                        self.out.write(b'\xB0' + struct.pack('<b', val))
                    elif val >= -0x8000 and lenc >= 2:
                        self.out.write(b'\xB1' + struct.pack('<h', val))
                    elif val >= -0x8000_0000 and lenc >= 4:
                        self.out.write(b'\xB2' + struct.pack('<l', val))
                    elif val >= -0x8000_0000_0000_0000 and lenc >= 8:
                        self.out.write(b'\xB3' + struct.pack('<q', val))
                    else:
                        self.out.write(b'\xBB' + enc)
                else:
                    if val < 0x80:
                        self.out.write(b'\xB4' + struct.pack('<B', val))
                    elif val < 0x8000 and lenc >= 2:
                        self.out.write(b'\xB5' + struct.pack('<H', val))
                    elif val < 0x8000_0000 and lenc >= 4:
                        self.out.write(b'\xB6' + struct.pack('<L', val))
                    elif val < 0x8000_0000_0000_0000 and lenc >= 8:
                        self.out.write(b'\xB7' + struct.pack('<Q', val))
                    else:
                        self.out.write(b'\xBB' + enc)

        elif isinstance(val, float):
            if math.isnan(val):
                self.out.write(b'\xAD')
                return self
            if math.isinf(val):
                self.out.write(b'\xAE' if val < 0 else b'\xAF')
                return self

            try:
                f16 = struct.pack('<e', val)
                if struct.unpack('<e', f16)[0] == val:
                    self.out.write(b'\xB8' + f16)
                    #print(f'Stored f16: {f16}')
                    return self
            except:
                pass

            try:
                f32 = struct.pack('<f', val)
                if struct.unpack('<f', f32)[0] == val:
                    self.out.write(b'\xB9' + f32)
                    #print(f'Stored f32: {f32}')
                    return self
            except:
                pass

            self.out.write(b'\xBA' + struct.pack('<d', val))
        elif isinstance(val, array.array):
            code = get_typed_array_marker(val.typecode)
            self.out.write(bytes([0x84, code]))
            self.out.write(uleb128encode(len(val)))
            if BIG_ENDIAN:
                val = array.array(val.typecode, val)
                val.byteswap()
            val.tofile(self.out)
        elif isinstance(val, bytes):
            self.out.write(bytes([0x84, 0xB4]))
            self.out.write(uleb128encode(len(val)))
            self.out.write(val)
        elif isinstance(val, Sequence):
            if self.detect_arrays:
                """
                for code in "Bb":
                    try:
                        res = array.array(code, val)
                        code = get_typed_array_marker(code)
                        self.out.write(bytes([0x84, code]))
                        self.out.write(uleb128encode(len(res)))
                        res.tofile(self.out)
                        return self
                    except:
                        pass
                """
                t = detect_array_type(val)
                if t == 'int':
                    #print(f"Detected array int[{len(val)}]")
                    self.out.write(b'\x84\xBB')
                    self.out.write(uleb128encode(len(val)))
                    for v in val:
                        self.out.write(sleb128encode(v))
                    return self
                elif t == 'float':
                    self.add(array.array('d', val))
                    return self

            self.start_list()
            for v in val:
               self.add(v)
            self.end_list()
        elif isinstance(val, Mapping):
            self.start_dict()
            for k, v in val.items():
                self.add_str(k)
                self.add(v)
            self.end_dict()

        return self

    """
    Low-level API
    """

    def add_str(self, val):
        val = str(val)
        strlen = len(val)

        if val in self.lru:
            idx = len(self.lru) - self.lru.index(val) - 1
            #print (f"Found {val} at LRU {idx}")
            self.out.write(b'\x81' + uleb128encode(idx))
        else:
            if val in self.lru_dynamic:
                # Move from dynamic LRU to active
                self.lru.append(val)
                self.lru_dynamic.remove(val)
                # Prepend LRU tag
                self.out.write(b'\x8C')

            buff = val.encode('utf8')
            if b'\x00' in buff or len(buff) >= 512:
                self.out.write(b'\x82')
                self.out.write(uleb128encode(len(buff)))
                self.out.write(buff)
            else:
                self.out.write(buff + b'\x00')

    def _append(self, b):
        self.out.write(b)
        return self

    def start_list(self):         return self._append(b'\x90')
    def end_list(self):           return self._append(b'\x91')
    def start_dict(self):         return self._append(b'\x92')
    def end_dict(self):           return self._append(b'\x93')

class Reader:
    def __init__(self, inp):
        if isinstance(inp, bytes):
            inp = io.BytesIO(inp)
        if not isinstance(inp, io.BufferedReader):
            inp = io.BufferedReader(inp)
        self.inp = inp
        self.lru = deque()

    def peek_byte(self):
        return self.inp.peek(1)[0]

    def has_data(self):
        return len(self.inp.peek(1))

    def read_string(self):
        c = self.inp.read(1)
        if c == b'\x81':
            n = uleb128read(self.inp)
            res = self.lru[-1-n]
        elif c == b'\x82':
            n = uleb128read(self.inp)
            res = self.inp.read(n).decode('utf8')
        else:
            # read until 0
            buff = b''
            while not c == b'\x00':
                buff += c
                c = self.inp.read(1)
            res = buff.decode('utf8')
        return res

    def read_special(self):
        t = self.inp.read(1)[0]
        if   t == 0xAA:               res = False
        elif t == 0xAB:               res = True
        elif t == 0xAC:               res = None
        elif t == 0xAD:               res =  math.nan
        elif t == 0xAE:               res = -math.inf
        elif t == 0xAF:               res =  math.inf
        elif t >= 0xA0 and t <= 0xA9: res = t-0xA0
        else:
            raise Exception(f"Wrong special value: {t}")
        return res

    def read_typed_value(self):
        t = self.inp.read(1)[0]
        if   t == 0xB0:
            res = struct.unpack('<b', self.inp.read(1))[0]
        elif t == 0xB1:
            res = struct.unpack('<h', self.inp.read(2))[0]
        elif t == 0xB2:
            res = struct.unpack('<l', self.inp.read(4))[0]
        elif t == 0xB3:
            res = struct.unpack('<q', self.inp.read(8))[0]
        elif t == 0xB4:
            res = struct.unpack('<B', self.inp.read(1))[0]
        elif t == 0xB5:
            res = struct.unpack('<H', self.inp.read(2))[0]
        elif t == 0xB6:
            res = struct.unpack('<L', self.inp.read(4))[0]
        elif t == 0xB7:
            res = struct.unpack('<Q', self.inp.read(8))[0]
        elif t == 0xB8:
            res = struct.unpack('<e', self.inp.read(2))[0]
        elif t == 0xB9:
            res = struct.unpack('<f', self.inp.read(4))[0]
        elif t == 0xBA:
            res = struct.unpack('<d', self.inp.read(8))[0]
        elif t == 0xBB:
            res = sleb128read(self.inp)
        else:
            raise Exception(f"Unknown typed value: {t}")
        return res

    def read_typed_array(self):
        chunked = (self.inp.read(1) == b'\x85')
        t = self.inp.read(1)[0]
        n = uleb128read(self.inp)
        if t == 0xBB:
            res = []
            for i in range(0, n):
                val = sleb128read(self.inp)
                res.append(val)
            return res
        else:
            code = get_array_type_code(t)
            res = array.array(code)
            res.fromfile(self.inp, n)
            if BIG_ENDIAN:
                res.byteswap()
            return res.tolist()

    def read_list(self):
        res = []
        assert self.inp.read(1) == b'\x90'
        while not self.peek_byte() == 0x91:
            res.append(self.read_object())
        self.inp.read(1)
        return res

    def read_dict(self):
        res = {}
        assert self.inp.read(1) == b'\x92'
        # TODO: typed dict
        while not self.peek_byte() == 0x93:
            key = self.read_object()
            val = self.read_object()
            res[key] = val
        self.inp.read(1)
        return res

    def read_object(self):
        nxt = self.peek_byte()

        while nxt == 0xFF:
            self.inp.read(1)
            nxt = self.peek_byte()

        if nxt > 0x82 and nxt <= 0xC1:
            if nxt >= 0xA0 and nxt <= 0xAF:
                return self.read_special()
            elif nxt >= 0xB0 and nxt <= 0xBB:
                return self.read_typed_value()
            elif nxt == 0x84 or nxt == 0x85:
                return self.read_typed_array()
            elif nxt == 0x8C:
                self.inp.read(1)
                if self.peek_byte() == 0x90:
                    self.lru.extend(self.read_list())
                    # Read next object (LRU list is skipped)
                    return self.read_object()
                else:
                    res = self.read_string()
                    self.lru.append(res)
                    return res
            elif nxt == 0x8F:
                assert self.inp.read(4) == MUON_MAGIC
                return self.read_object()
            elif nxt == 0x90:
                return self.read_list()
            elif nxt == 0x92:
                return self.read_dict()
            else:
                raise Exception("Unknown object")
        else:
            return self.read_string()

def dumps(data, refs=0):
    if refs:
        d = DictBuilder()
        d.add(data)
        t = d.get_dict(512)
    else:
        t = []

    out = io.BytesIO()
    m = Writer(out)
    #m.tag_muon()
    if len(t) > 127:
        m.add_lru_list(reversed(t))
    elif len(t):
        m.add_lru_dynamic(t)
    m.add(data)
    return out.getvalue()

def loads(data):
    return Reader(data).read_object()
