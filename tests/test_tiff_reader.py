"""tools/tiff_reader.py on synthetic deflate-tiled TIFFs written here (no network)."""

import struct
import zlib

import numpy as np
import pytest

from tools.tiff_reader import BytesSource, read_ifds, read_image


def _tiff(levels, big=True, bo="<", comp=8, tile=16, predictor=1):
    """A TIFF / BigTIFF of uint8 (or uint16) tiled images, one IFD per level."""
    out = bytearray()
    ofmt, cfmt = ("Q", "Q") if big else ("I", "H")
    out += (b"II" if bo == "<" else b"MM") + struct.pack(bo + "H", 43 if big else 42)
    if big:
        out += struct.pack(bo + "HH", 8, 0)
    ptr_pos = len(out)  # where the next IFD offset is stored (patched when the IFD is written)
    out += struct.pack(bo + ofmt, 0)
    for img in levels:
        h, w = img.shape
        offs, cnts = [], []
        for ty in range(-(-h // tile)):
            for tx in range(-(-w // tile)):
                t = np.zeros((tile, tile), img.dtype)
                s = img[ty * tile:(ty + 1) * tile, tx * tile:(tx + 1) * tile]
                t[:s.shape[0], :s.shape[1]] = s
                if predictor == 2:
                    t = np.diff(t, axis=1, prepend=0).astype(img.dtype)
                raw = t.astype(img.dtype.newbyteorder(bo)).tobytes()
                raw = zlib.compress(raw) if comp == 8 else raw
                offs.append(len(out))
                cnts.append(len(raw))
                out += raw
        arr_o = len(out)
        out += struct.pack(bo + "Q" * len(offs) if big else bo + "I" * len(offs), *offs)
        arr_c = len(out)
        out += struct.pack(bo + "Q" * len(cnts) if big else bo + "I" * len(cnts), *cnts)
        ents = [(256, 4, w), (257, 4, h), (258, 3, img.dtype.itemsize * 8), (259, 3, comp), (317, 3, predictor),
                (322, 4, tile), (323, 4, tile), (324, 16 if big else 4, len(offs), arr_o),
                (325, 16 if big else 4, len(cnts), arr_c), (339, 3, 1)]
        ifd_pos = len(out)
        struct.pack_into(bo + ofmt, out, ptr_pos, ifd_pos)
        out += struct.pack(bo + cfmt, len(ents))
        for e in ents:
            tag, typ, count = e[:3]
            if len(e) == 4:  # array stored elsewhere
                out += struct.pack(bo + "HH", tag, typ) + struct.pack(bo + ("Q" if big else "I"), count)
                out += struct.pack(bo + ("Q" if big else "I"), e[3])
            else:
                val = e[2]
                out += struct.pack(bo + "HH", tag, typ) + struct.pack(bo + ("Q" if big else "I"), 1)
                code = {3: "H", 4: "I"}[typ]
                out += struct.pack(bo + code, val).ljust(8 if big else 4, b"\0")
        ptr_pos = len(out)
        out += struct.pack(bo + ofmt, 0)
    return bytes(out)


def _img(h, w, dtype=np.uint8, seed=0):
    return np.random.default_rng(seed).integers(0, 30, (h, w)).astype(dtype)


@pytest.mark.parametrize("big", [True, False])
@pytest.mark.parametrize("bo", ["<", ">"])
def test_deflate_tiles_roundtrip(big, bo):
    a, b = _img(50, 70), _img(13, 18, seed=1)  # edge tiles are partial
    src = BytesSource(_tiff([a, b], big=big, bo=bo))
    ifds = read_ifds(src)
    assert [(i["width"], i["length"]) for i in ifds] == [(70, 50), (18, 13)]
    np.testing.assert_array_equal(read_image(src, ifds[0]), a)
    np.testing.assert_array_equal(read_image(src, ifds[1]), b)


def test_uint16_predictor_and_uncompressed():
    a = _img(33, 40, np.uint16)
    for comp, pred in ((8, 2), (1, 1)):
        src = BytesSource(_tiff([a], comp=comp, predictor=pred))
        np.testing.assert_array_equal(read_image(src, read_ifds(src)[0]), a)


def test_rejects_garbage_and_unsupported():
    with pytest.raises(ValueError):
        read_ifds(BytesSource(b"not a tiff at all, just text"))
    src = BytesSource(_tiff([_img(16, 16)], comp=1))
    ifd = read_ifds(src)[0]
    ifd["compression"] = 5  # LZW
    with pytest.raises(ValueError):
        read_image(src, ifd)
