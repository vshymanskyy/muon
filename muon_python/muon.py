import io
import base64
import re
import array

import leb128, struct
from collections.abc import Mapping, Sequence
from collections import Counter

class DictBuilder:
    def __init__(self):
        self._count = Counter()

    def add(self, val):
        if val is None:
            pass
        elif isinstance(val, str):
            self.add_str(val)
        elif isinstance(val, list):
            for v in val:
                self.add(v)
        elif isinstance(val, dict):
            for k, v in val.items():
                self.add_str(k)
                self.add(v)

    def add_str(self, val):
        if len(val) > 1:
            self._count.update([val])

    def get_dict(self, size = 64):
        for k, v in self._count.items():
            self._count[k] = (v-1) * len(k)

        res = filter(lambda x: x[1] > 6, self._count.most_common(size))
        return list(map(lambda x: x[0], res))

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
    def __init__(self, out, table=[], mark=False):
        self.out = out
        self.st = {}

        self.detect_arrays = True
        self.detect_binary = False
        self.detect_numstr = True

        if mark:
            self.out.write(b'\x8F\xCE\xBC\x31')

        if len(table):
            self.add(b'\x8C')
            self.start_list()
            for idx, s in enumerate(table):
                self.add_str(s)
                self.st[s] = idx
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
                    print(f'Stored f16: {f16}')
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
            pass # TODO
        elif isinstance(val, Sequence):
            t = None
            if self.detect_arrays:
                t = detect_array_type(val)

            if t == 'int':
                #print(f"Detected array int[{len(val)}]")
                self.out.write(b'\x84\xBB')
                self.out.write(leb128.i.encode(len(val)))
                for v in val:
                    self.out.write(leb128.i.encode(v))
                self.out.write(b'\x00')
            elif t == 'float':
                #print(f"Detected array float[{len(val)}]")
                self.out.write(b'\x84\xBA')
                self.out.write(leb128.i.encode(len(val)))
                for v in val:
                    self.out.write(struct.pack('<d', v))
                self.out.write(b'\x00')
            else:
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

    def add_attr(self, val):
        self.start_attr()
        for k, v in val.items():
            self.add_str(k)
            self.add(v)
        self.end_attr()

    """
    Low-level API
    """

    def add_str(self, val):
        strlen = len(val)

        if self.detect_numstr and not val.startswith('0'):
            try:
                self.add(int(val))
                return
            except:
                pass

        if self.detect_numstr and strlen > 8:
            try:
                self.add(float(val))
                return
            except:
                pass


        if self.detect_binary and not bool(re.search('\s', val)):
            tmp = None

            if tmp == None and (strlen == 32 or strlen == 40 or strlen > 120):
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
                self.out.write(leb128.i.encode(len(tmp)))
                self.out.write(tmp)
                self.out.write(b'\x00')
                return

        if val in self.st:
            idx = self.st[val]
            self.out.write(b'\x81' + leb128.u.encode(idx))
        else:
            self.out.write(str(val).encode('utf8') + b'\x00')

    def add_binary(self, val):
        self.out.write(b'\x84\xB4')
        self.out.write(leb128.u.encode(len(val)))
        self.out.write(val)
        self.out.write(b'\x00')

    def start_list(self):         self.out.write(b'\x90')
    def end_list(self):           self.out.write(b'\x91')
    def start_dict(self):         self.out.write(b'\x92')
    def end_dict(self):           self.out.write(b'\x93')
    def start_attr(self):         self.out.write(b'\x94')
    def end_attr(self):           self.out.write(b'\x95')

class Reader:
    def __init__(self, inp):
        if isinstance(inp, io.BufferedReader):
            self.inp = inp
        else:
            self.inp = io.BufferedReader(inp)

    def peek_byte(self):
        return self.inp.peek(1)[0]

    def read_string(self):
        c = self.inp.read(1)
        if c == b'\x81':
            raise Exception("TODO: String refs")
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
            n, l = leb128.i.decode_reader(self.inp)
            return n
        else:
            raise Exception(f"Unknown typed value: {t}")

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

    def read_attrs(self):
        res = {}
        assert(self.inp.read(1) == b'\x94')
        while not self.peek_byte() == 0x95:
            key = self.read_string()
            val = self.read_object()
            res[key] = val
        self.inp.read(1)
        return res

    def read_typed_array(self):
        raise Exception("TODO: Typed arrays")

    def read_object(self):
        nxt = self.peek_byte()

        if nxt >= 0x80 and nxt <= 0xC1:
            if   nxt >= 0xA0 and nxt <= 0xAF:
                return self.read_special()
            elif nxt >= 0xB0 and nxt <= 0xBB:
                return self.read_typed_value()
            elif nxt == 0x84:
                return self.read_typed_array()
            elif nxt == 0x90:
                return self.read_list()
            elif nxt == 0x92:
                return self.read_dict()
            elif nxt == 0x94:
                attr = self.read_attrs()
                return self.read_object()
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
    m = Writer(out, table=t)
    m.add(data)
    return out.getvalue()

def loads(data):
    inp = io.BytesIO(data)
    m = Reader(out)
    return m.read_object()
