import io
import base64
import re
import array

import leb128, struct
from collections.abc import Mapping, Sequence
from collections import deque, Counter

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

    def get_dict(self, size = 64):
        for k, v in self._count.items():
            self._count[k] = (v-1) * len(k)

        res = filter(lambda x: x[1] > 6, self._count.most_common())
        return list(map(lambda x: x[0], res))[0:size]

def detect_array_type(arr):
    if len(arr) < 3:
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

def optimize_json(data):
    return data

class Writer:
    def __init__(self, out):
        self.out = out
        self.lru = deque(maxlen=512)

        self.detect_arrays = True

    def tag_muon(self):
        self.out.write(b'\x8F\xCE\xBC\x31')

    def add_lru_list(self, table):
        table = list(table)
        self.lru.extend(table)

        self.out.write(b'\x8C')
        self.start_list()
        for s in table:
            self.out.write(s.encode('utf8') + b'\x00')
        self.end_list()

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
                self.out.write(b'\xBB' + leb128.i.encode(int(val)))
        elif isinstance(val, float):
            try:
                f16 = struct.pack('<e', val)
                if struct.unpack('<e', f16)[0] == val:
                    self.out.write(b'\xB8' + f16)
                    #print(f'Stored f16: {f16}')
                    return
            except:
                pass

            try:
                f32 = struct.pack('<f', val)
                if struct.unpack('<f', f32)[0] == val:
                    self.out.write(b'\xB9' + f32)
                    #print(f'Stored f32: {f32}')
                    return
            except:
                pass

            self.out.write(b'\xBA' + struct.pack('<d', val))
        elif isinstance(val, array.array):
            code = get_typed_array_marker(val.typecode)
            self.out.write(b'\x84' + struct.pack("<B", code))
            self.out.write(leb128.u.encode(len(val)))
            self.out.write(val.tobytes())
        elif isinstance(val, Sequence):
            if self.detect_arrays:
                """
                for code in "Bb":
                    try:
                        res = array.array(code, val)
                        code = get_typed_array_marker(code)
                        self.out.write(b'\x84' + bytes([code]))
                        self.out.write(leb128.u.encode(len(res)))
                        res.tofile(self.out)
                        return
                    except:
                        pass
                """
                t = detect_array_type(val)
                if t == 'int':
                    #print(f"Detected array int[{len(val)}]")
                    self.out.write(b'\x84\xBB')
                    self.out.write(leb128.u.encode(len(val)))
                    for v in val:
                        self.out.write(leb128.i.encode(v))
                    return
                elif t == 'float':
                    #print(f"Detected array float[{len(val)}]")
                    self.out.write(b'\x84\xBA')
                    self.out.write(leb128.u.encode(len(val)))
                    for v in val:
                        self.out.write(struct.pack('<d', v))
                    return

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

    """
    Low-level API
    """

    def add_str(self, val):
        val = str(val)
        strlen = len(val)


        """ TODO: move this to a separate lint/optimization step
        if self.detect_numstr:
            if not val.startswith('0'):
                try:
                    self.add(int(val))
                    return
                except:
                    pass

            if strlen > 8:
                try:
                    self.add(float(val))
                    return
                except:
                    pass


        if self.detect_binary and not bool(re.search('\s', val)):
            tmp = None

            if tmp == None and (strlen == 32 or strlen == 40 or strlen >= 64):
                try:
                    tmp = bytes.fromhex(val)
                    #print(f"Detected hex: {val}")
                except:
                    pass

            if tmp == None and strlen >= 32 and val.endswith('='):
                try:
                    tmp = base64.b64decode(val)
                    #print(f"Detected base64: {val}")
                except:
                    pass

            if not tmp == None:
                self.out.write(b'\x84\xB4')
                self.out.write(leb128.u.encode(len(tmp)))
                self.out.write(tmp)
                return
        """

        if val in self.lru:
            idx = len(self.lru) - self.lru.index(val) - 1
            #print (f"Found {val} at LRU {idx}")
            self.out.write(b'\x81' + leb128.u.encode(idx))
        else:
            buff = val.encode('utf8')
            if b'\x00' in buff:         # TODO: or len(buff) >= 512
                self.out.write(b'\x82')
                self.out.write(leb128.u.encode(len(buff)))
                self.out.write(buff)
            else:
                self.out.write(buff + b'\x00')

    def start_list(self):         self.out.write(b'\x90')
    def end_list(self):           self.out.write(b'\x91')
    def start_dict(self):         self.out.write(b'\x92')
    def end_dict(self):           self.out.write(b'\x93')

def get_array_type_code(t):
    if   t == 0xB0: return 'b'
    elif t == 0xB1: return 'h'
    elif t == 0xB2: return 'l'
    elif t == 0xB3: return 'q'

    elif t == 0xB4: return 'B'
    elif t == 0xB5: return 'H'
    elif t == 0xB6: return 'L'
    elif t == 0xB7: return 'Q'

    elif t == 0xB8: return None # f16
    elif t == 0xB9: return 'f'
    elif t == 0xBA: return 'd'

def get_typed_array_marker(t):
    if   t == 'b': return 0xB0
    elif t == 'h': return 0xB1
    elif t == 'l': return 0xB2
    elif t == 'q': return 0xB3

    elif t == 'B': return 0xB4
    elif t == 'H': return 0xB5
    elif t == 'L': return 0xB6
    elif t == 'Q': return 0xB7

    elif t == 'd': return 0xB9

class Reader:
    def __init__(self, inp):
        self.lru = deque()
        if isinstance(inp, io.BufferedReader):
            self.inp = inp
        else:
            self.inp = io.BufferedReader(inp)

    def peek_byte(self):
        return self.inp.peek(1)[0]

    def read_string(self):
        c = self.inp.read(1)
        if c == b'\x81':
            n, _ = leb128.u.decode_reader(self.inp)
            return self.lru[-1-n]
        elif c == b'\x82':
            n, _ = leb128.u.decode_reader(self.inp)
            return self.inp.read(n).decode('utf8')
        else:
            # read until 0
            buff = b''
            while not c == b'\x00':
                buff += c
                c = self.inp.read(1)
            return buff.decode('utf8')

    def read_special(self):
        t = self.inp.read(1)[0]
        if   t == 0xAA:               return False
        elif t == 0xAB:               return True
        elif t == 0xAC:               return None
        elif t >= 0xA0 and t <= 0xA9: return t-0xA0
        else:
            raise Exception(f"Wrong special value: {t}")

    def read_typed_value(self):
        t = self.inp.read(1)[0]
        if t == 0xBA:
            return struct.unpack('<d', self.inp.read(8))[0]
        elif t == 0xB9:
            return struct.unpack('<f', self.inp.read(4))[0]
        elif t == 0xB8:
            return struct.unpack('<e', self.inp.read(2))[0]
        elif t == 0xBB:
            n, _ = leb128.i.decode_reader(self.inp)
            return n
        else:
            raise Exception(f"Unknown typed value: {t}")

    def read_typed_array(self):
        chunked = (self.inp.read(1) == b'\x85')
        t = self.inp.read(1)[0]
        n, _ = leb128.u.decode_reader(self.inp)
        if t == 0xBB:
            res = []
            for i in range(0, n):
                val, _ = leb128.i.decode_reader(self.inp)
                res.append(val)
            return res
        else:
            code = get_array_type_code(t)
            res = array.array(code)
            # TODO: use struct here to ensure Little-Endian byte order
            res.fromfile(self.inp, n)
            return res.tolist()

    def read_list(self):
        res = []
        assert(self.inp.read(1) == b'\x90')
        while not self.peek_byte() == 0x91:
            res.append(self.read_object())
        self.inp.read(1)
        return res

    def read_dict(self):
        res = {}
        assert(self.inp.read(1) == b'\x92')
        while not self.peek_byte() == 0x93:
            key = self.read_string()
            val = self.read_object()
            res[key] = val
        self.inp.read(1)
        return res

    def read_object(self):
        nxt = self.peek_byte()

        if nxt > 0x81 and nxt <= 0xC1:
            if nxt == 0x82:
                return self.read_string()
            elif nxt >= 0xA0 and nxt <= 0xAF:
                return self.read_special()
            elif nxt >= 0xB0 and nxt <= 0xBB:
                return self.read_typed_value()
            elif nxt == 0x84 or nxt == 0x85:
                return self.read_typed_array()
            elif nxt == 0x8C:
                self.inp.read(1)
                self.lru.extend(self.read_list())
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
        t = d.get_dict(None)
    else:
        t = []

    out = io.BytesIO()
    m = Writer(out)
    #m.tag_muon()
    if len(t):
        m.add_lru_list(reversed(t))
    m.add(data)
    return out.getvalue()

def loads(data):
    inp = io.BytesIO(data)
    m = Reader(inp)
    return m.read_object()
