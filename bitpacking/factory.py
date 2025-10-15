from __future__ import annotations
from typing import List, Tuple
import struct

from .crossing import BitPackingCrossing
from .noncrossing import BitPackingNonCrossing
from .core import WORD_BITS
from .overflow import BitPackingOverflow

MAGIC = b"BPK1"
MODE_CROSSING = 0
MODE_NONCROSS = 1
# (On n'encode pas encore l'overflow dans le fichier .bin du CLI, on l'utilisera plus tard si besoin)


class CompressorFactory:
    @staticmethod
    def create_from_list(mode: str, ints: List[int]):
        if mode == "crossing":
            return BitPackingCrossing.from_list(ints)
        elif mode == "non_crossing":
            return BitPackingNonCrossing.from_list(ints)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    @staticmethod
    def from_packed_crossing(k: int, n: int, words: List[int]) -> BitPackingCrossing:
        return BitPackingCrossing(k=k, n=n, words=words)

    @staticmethod
    def from_packed_noncross(k: int, n: int, words: List[int]) -> BitPackingNonCrossing:
        # Recalcule start_bits déterministiquement
        start_bits: List[int] = []
        pos = 0
        for _ in range(n):
            bit_in_word = pos % WORD_BITS
            if bit_in_word + k > WORD_BITS:
                pos = ((pos // WORD_BITS) + 1) * WORD_BITS
            start_bits.append(pos)
            pos += k
        return BitPackingNonCrossing(k=k, n=n, words=words, start_bits=start_bits)

    @staticmethod
    def from_list_overflow(ints: List[int]) -> BitPackingOverflow:
        return BitPackingOverflow.from_list(ints)


def save_binary(path: str, mode_str: str, k: int, n: int, words: List[int]) -> None:
    if mode_str == "crossing":
        mode = MODE_CROSSING
    elif mode_str == "non_crossing":
        mode = MODE_NONCROSS
    else:
        raise ValueError(f"Unknown mode: {mode_str}")

    wlen = len(words)
    # header: MAGIC (4s) + mode (B) + k (H) + n (I) + wlen (I)
    header = struct.pack("<4sBHI I", MAGIC, mode, k, n, wlen)
    body = b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)
    with open(path, "wb") as f:
        f.write(header)
        f.write(body)


def load_binary(path: str) -> Tuple[str, int, int, List[int]]:
    with open(path, "rb") as f:
        head = f.read(4 + 1 + 2 + 4 + 4)
        if len(head) < 15:
            raise ValueError("File too short or corrupted")
        magic, mode, k, n, wlen = struct.unpack("<4sBHI I", head)
        if magic != MAGIC:
            raise ValueError("Bad magic/version")
        words_bytes = f.read(wlen * 4)
        if len(words_bytes) != wlen * 4:
            raise ValueError("Truncated words section")
        words = list(struct.unpack("<" + "I"*wlen, words_bytes))

    if mode == MODE_CROSSING:
        mode_str = "crossing"
    elif mode == MODE_NONCROSS:
        mode_str = "non_crossing"
    else:
        raise ValueError("Unknown mode code")

    return mode_str, k, n, words
