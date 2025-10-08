from __future__ import annotations
from typing import List, Dict
from math import ceil, log2
from .core import pack_bits, unpack_bits


class BitPackingOverflow:
    """
    Compression avec zone de débordement (overflow area), en layout crossing.

    Token i (largeur T = 1 + max(k_base, p)):
      - bit le plus haut (MSB) = flag (1 bit)
            0 => payload = valeur (k_base bits, en bas du token)
            1 => payload = index overflow (p bits, en bas du token)
      - bits de padding (si payload plus petit que max(k_base,p)) restent à 0.

    Accès direct O(1): offset(i) = i * T.
    """

    def __init__(self, k_base: int, p: int, k_over: int,
                 n: int, main_words: List[int], overflow_words: List[int],
                 m: int):
        self.k_base = k_base
        self.p = p
        self.k_over = k_over
        self.n = n
        self.main_words = main_words
        self.overflow_words = overflow_words
        self.m = m
        self.T = 1 + max(k_base, p)

    @classmethod
    def from_list(cls, ints: List[int]) -> "BitPackingOverflow":
        n = len(ints)
        if n == 0:
            return cls(0, 0, 0, 0, [], [], 0)
        if any(x < 0 for x in ints):
            raise ValueError("Negative values not supported yet (bonus).")

        # Heuristique simple: ne pas dépasser 8 bits si possible
        k_max = max(ints).bit_length()
        k_base = max(1, min(8, k_max))

        # Collecte des valeurs overflow et mapping valeur -> index (stable)
        overflow_vals: List[int] = []
        index_map: Dict[int, int] = {}
        for x in ints:
            if x >= (1 << k_base):
                if x not in index_map:
                    index_map[x] = len(overflow_vals)
                    overflow_vals.append(x)

        m = len(overflow_vals)
        p = ceil(log2(m)) if m > 0 else 0
        T = 1 + max(k_base, p)
        k_over = max((x.bit_length() for x in overflow_vals), default=0)

        # Zone principale: écrire T bits par token (payload en bas, flag en haut)
        main_words: List[int] = []
        for i, x in enumerate(ints):
            base = i * T
            if x < (1 << k_base):
                # flag=0, payload = valeur sur k_base bits
                if k_base > 0:
                    pack_bits(main_words, base, x, k_base)
                pack_bits(main_words, base + (T - 1), 0, 1)  # flag en MSB
            else:
                # flag=1, payload = index overflow sur p bits
                idx = index_map[x]
                if p > 0:
                    pack_bits(main_words, base, idx, p)
                pack_bits(main_words, base + (T - 1), 1, 1)  # flag en MSB

        # Zone overflow: valeurs packées de façon crossing standard
        overflow_words: List[int] = []
        if m > 0 and k_over > 0:
            for j, x in enumerate(overflow_vals):
                pack_bits(overflow_words, j * k_over, x, k_over)

        return cls(k_base, p, k_over, n, main_words, overflow_words, m)

    def get(self, i: int) -> int:
        if i < 0 or i >= self.n:
            raise IndexError("index out of range")
        base = i * self.T
        flag = unpack_bits(self.main_words, base + (self.T - 1), 1)
        if flag == 0:
            return unpack_bits(self.main_words, base, self.k_base) if self.k_base > 0 else 0
        # flag == 1
        if self.p == 0 or self.m == 0:
            raise IndexError("Overflow flag set but no overflow area")
        idx = unpack_bits(self.main_words, base, self.p)
        if idx >= self.m:
            raise IndexError("overflow index out of range")
        return unpack_bits(self.overflow_words, idx * self.k_over, self.k_over) if self.k_over > 0 else 0

    def to_list(self) -> List[int]:
        return [self.get(i) for i in range(self.n)]
