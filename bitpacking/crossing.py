from __future__ import annotations
from typing import List
from .core import pack_bits, unpack_bits, words_needed, WORD_BITS, WORD_MASK

class BitPackingCrossing:
    """
    Bit packing en mode 'crossing' (les entiers peuvent chevaucher 2 mots).
    Accès direct O(1) via offset i*k.
    """

    def __init__(self, k: int, n: int, words: List[int]):
        if k < 0:
            raise ValueError("k must be >= 0")
        if n < 0:
            raise ValueError("n must be >= 0")
        self.k = k
        self.n = n
        self.words = words

    @staticmethod
    def _compute_k(ints: List[int]) -> int:
        if not ints:
            return 0
        mx = max(ints)
        if mx < 0:
            raise ValueError("Negative values not supported yet (will be in bonus).")
        return max(1, mx.bit_length())

    @classmethod
    def from_list(cls, ints: List[int]) -> "BitPackingCrossing":
        n = len(ints)
        if n == 0:
            return cls(k=0, n=0, words=[])
        k = cls._compute_k(ints)
        words: List[int] = []
        for i, x in enumerate(ints):
            if x < 0:
                raise ValueError("Negative values not supported yet (will be in bonus).")
            if x >= (1 << k):
                raise ValueError(f"value {x} does not fit in k={k} bits")
            pack_bits(words, start_bit=i * k, value=x, width=k)
        return cls(k=k, n=n, words=words)

    def get(self, i: int) -> int:
        if i < 0 or i >= self.n:
            raise IndexError("index out of range")
        if self.k == 0:
            # tableau vide
            return 0
        return unpack_bits(self.words, start_bit=i * self.k, width=self.k)

    def to_list(self) -> List[int]:
        return [self.get(i) for i in range(self.n)]
