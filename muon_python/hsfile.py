import builtins
from heatshrink2.streams import HeatshrinkFile

def open(fn, mode="rb", window=10, lookahead=4):
    magic = b"H$"

    if mode == "wb":
        rawf = builtins.open(fn, mode)
        rawf.write(magic + bytes([(window << 4) | lookahead]))

        f = HeatshrinkFile(rawf, mode,
                           window_sz2    = window,
                           lookahead_sz2 = lookahead)
    elif mode == "rb":
        rawf = builtins.open(fn, "rb")

        if not magic == rawf.read(2):
            raise Exception("Heatshrink header not found")

        params = rawf.read(1)[0]

        f = HeatshrinkFile(rawf, mode,
                           window_sz2    = (params >> 4) & 0xF,
                           lookahead_sz2 = (params     ) & 0xF)
    else:
        raise Exception("Mode should be wb or rb")

    return f
