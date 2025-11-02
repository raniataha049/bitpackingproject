from __future__ import annotations
from typing import List
from .core import pack_bits, unpack_bits, WORD_BITS

class BitPackingNonCrossing:
   
    def __init__(self, k: int, n: int, words: List[int], start_bits: List[int]):
        if k < 0 or n < 0:
            raise ValueError("k and n must be >= 0")
        if len(start_bits) != n:
            raise ValueError("start_bits length must equal n")
        self.k = k
        self.n = n
        self.words = words
        self.start_bits = start_bits

    @staticmethod
    def _compute_k(ints: List[int]) -> int:
        if not ints: return 0
        mx = max(ints)
        if mx < 0:
            raise ValueError("Negative values not supported yet (bonus later).")
        return max(1, mx.bit_length())

    @classmethod
    def from_list(cls, ints: List[int]) -> "BitPackingNonCrossing":
        n = len(ints)
        if n == 0:
            return cls(k=0, n=0, words=[], start_bits=[])
        k = cls._compute_k(ints)
        words: List[int] = []
        start_bits: List[int] = []
        pos = 0  # position en bits dans le flux
        for x in ints:
            if x < 0:
                raise ValueError("Negative values not supported yet (bonus later).")
            if x >= (1 << k):
                raise ValueError(f"value {x} does not fit in k={k} bits")

            bit_in_word = pos % WORD_BITS
            if bit_in_word + k > WORD_BITS:
                pos = ((pos // WORD_BITS) + 1) * WORD_BITS  

            start_bits.append(pos)
            pack_bits(words, start_bit=pos, value=x, width=k)
            pos += k
        return cls(k=k, n=n, words=words, start_bits=start_bits)

    def get(self, i: int) -> int:
        if i < 0 or i >= self.n:
            raise IndexError("index out of range")
        if self.k == 0:
            return 0
        s = self.start_bits[i]
        return unpack_bits(self.words, start_bit=s, width=self.k)

    def to_list(self) -> List[int]:
        return [self.get(i) for i in range(self.n)]
