#!/usr/bin/env python3
"""Generate three placeholder PNGs in media/ (stdlib only, no downloads).

Replace or add your own images in media/ and rerun build_baseline.py.
"""
import pathlib
import struct
import zlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "media"
W, H, SCALE = 960, 540, 16
FONT = {  # 5x7 bitmap glyphs
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    " ": ["00000"] * 7,
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
}


def png(path, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data))

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def make(n, bg, fg):
    text = f"SAMPLE {n}"
    tw, th = len(text) * 6 * SCALE - SCALE, 7 * SCALE
    x0, y0 = (W - tw) // 2, (H - th) // 2
    rows = []
    for y in range(H):
        row = []
        for x in range(W):
            on = False
            if y0 <= y < y0 + th and x0 <= x < x0 + tw:
                col, ry = (x - x0) // SCALE, (y - y0) // SCALE
                ci, gx = divmod(col, 6)
                on = gx < 5 and FONT[text[ci]][ry][gx] == "1"
            row += fg if on else bg
        rows.append(row)
    png(OUT / f"sample-{n}.png", rows)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    make(1, (126, 34, 52), (255, 255, 255))
    make(2, (40, 90, 60), (255, 255, 255))
    make(3, (30, 60, 120), (255, 255, 255))
    for p in sorted(OUT.glob("*.png")):
        print(p.name, p.stat().st_size, "bytes")
