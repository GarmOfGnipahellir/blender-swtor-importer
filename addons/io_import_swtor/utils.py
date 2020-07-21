# from http://wiki.xentax.com/index.php/Blender_Import_Guide

# Convenience functions
import os
from struct import pack, unpack


def half_to_float(h):
    s = int((h >> 15) & 0x00000001)     # sign
    e = int((h >> 10) & 0x0000001f)     # exponent
    f = int(h & 0x000003ff)     # fraction

    if e == 0:
        if f == 0:
            return int(s << 31)
        else:
            while not (f & 0x00000400):
                f <<= 1
                e -= 1
            e += 1
            f &= ~0x00000400
            print(s, e, f)
    elif e == 31:
        if f == 0:
            return int((s << 31) | 0x7f800000)
        else:
            return int((s << 31) | 0x7f800000 | (f << 13))

    e = e + (127 - 15)
    f = f << 13

    return int((s << 31) | (e << 23) | f)


def read_byte(read):
    return unpack(b'B', read(1))[0]


def read_bytes(read, size=1):
    return [read_byte(read) for i in range(size)]


def read_u16(read):
    return unpack(b'<H', read(2))[0]


def read_u32(read):
    return unpack(b'<I', read(4))[0]


def read_i16(read):
    return unpack(b'<h', read(2))[0]


def read_i32(read):
    return unpack(b'<i', read(4))[0]


def read_f16(read):
    v = unpack(b'H', read(2))[0]
    x = half_to_float(v)
    s = pack('I', x)
    return unpack('f', s)[0]


def read_f32(read):
    return unpack(b'<f', read(4))[0]


def find_parent_dir(path, name):
    """Searches parent directories until `name` is found"""
    while not path.endswith(name):
        path = os.path.split(path)[0]
    return path
