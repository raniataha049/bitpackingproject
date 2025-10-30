from typing import List, Tuple
import math, struct

MAGIC = b"BPov"
VERSION = 1


def _bits_needed(x: int) -> int:
    return 1 if x == 0 else x.bit_length()


def _choose_kprime(vals: List[int]) -> Tuple[int, int, int, int]:
    n = len(vals)
    if n == 0:
        return 1, 0, 1, 1
    K = _bits_needed(max(vals))
    best_cost = None
    best = None
    for kprime in range(1, K + 1):
        thr = 1 << kprime
        over_vals = [v for v in vals if v >= thr]
        overflow_count = len(over_vals)
        if overflow_count == 0:
            idx_bits = 0
            k_over = 1
        else:
            idx_bits = max(1, math.ceil(math.log2(overflow_count)))
            k_over = _bits_needed(max(over_vals))
        slot_w = 1 + max(kprime, idx_bits)
        cost = n * slot_w + overflow_count * k_over
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = (kprime, idx_bits, slot_w, k_over)
    return best


class BitPackerOverflow:
    """
    Overflow encoding with fixed-width slots (slot_w bits each).
      - slot_w = 1 + max(k', idx_bits)
      - For each slot:
         flag(1b) + payload (k' if flag=0, else idx_bits) + padding to reach slot_w
      - overflow area: values on k_over bits, tightly packed (crossing)
    """

    @staticmethod
    def _emit_crossing(words: List[int], bitbuf: int, bitlen: int, bits: int, width: int):
        if width == 0:
            return words, bitbuf, bitlen
        bitbuf |= (bits & ((1 << width) - 1)) << bitlen
        bitlen += width
        while bitlen >= 32:
            words.append(bitbuf & 0xFFFFFFFF)
            bitbuf >>= 32
            bitlen -= 32
        return words, bitbuf, bitlen

    def compress(self, arr: List[int]) -> bytes:
        n = len(arr)
        if n == 0:
            return MAGIC + bytes([VERSION]) + struct.pack("<I", 0)

        kprime, idx_bits, slot_w, k_over = _choose_kprime(arr)
        thr = 1 << kprime

        flags: List[int] = []
        payloads: List[int] = []
        overflow_values: List[int] = []
        for v in arr:
            if v < thr:
                flags.append(0)
                payloads.append(v)
            else:
                flags.append(1)
                payloads.append(len(overflow_values))
                overflow_values.append(v)

        words: List[int] = []
        bitbuf = 0
        bitlen = 0

        for f, p in zip(flags, payloads):
            words, bitbuf, bitlen = self._emit_crossing(words, bitbuf, bitlen, f, 1)
            used = 1
            if f == 0:
                words, bitbuf, bitlen = self._emit_crossing(words, bitbuf, bitlen, p, kprime)
                used += kprime
            else:
                w_idx = max(1, idx_bits)
                words, bitbuf, bitlen = self._emit_crossing(words, bitbuf, bitlen, p, w_idx)
                used += w_idx
            pad = slot_w - used
            if pad > 0:
                words, bitbuf, bitlen = self._emit_crossing(words, bitbuf, bitlen, 0, pad)

        if bitlen > 0:
            words.append(bitbuf)

        over_words: List[int] = []
        bitbuf = 0
        bitlen = 0
        for v in overflow_values:
            over_words, bitbuf, bitlen = self._emit_crossing(over_words, bitbuf, bitlen, v, max(1, k_over))
        if bitlen > 0:
            over_words.append(bitbuf)

        header = (
            MAGIC
            + bytes([VERSION])
            + struct.pack("<I", n)
            + bytes([kprime, max(1, idx_bits), slot_w, max(1, k_over)])
            + struct.pack("<I", len(words))
            + struct.pack("<I", len(over_words))
        )
        body = b"".join(w.to_bytes(4, "little") for w in words)
        over = b"".join(w.to_bytes(4, "little") for w in over_words)
        return header + body + over

    def _parse(self, blob: bytes):
        assert blob[:4] == MAGIC, "Bad magic"
        version = blob[4]
        if version != VERSION:
            raise ValueError(f"Bad version: {version}")
        off = 5
        n = struct.unpack_from("<I", blob, off)[0]
        off += 4
        kprime = blob[off]
        off += 1
        idx_bits = blob[off]
        off += 1
        slot_w = blob[off]
        off += 1
        k_over = blob[off]
        off += 1
        n_words = struct.unpack_from("<I", blob, off)[0]
        off += 4
        n_over_words = struct.unpack_from("<I", blob, off)[0]
        off += 4
        words_bytes = blob[off : off + 4 * n_words]
        off += 4 * n_words
        over_bytes = blob[off : off + 4 * n_over_words]
        words = [int.from_bytes(words_bytes[i : i + 4], "little") for i in range(0, len(words_bytes), 4)]
        over_words = [int.from_bytes(over_bytes[i : i + 4], "little") for i in range(0, len(over_bytes), 4)]
        return n, kprime, idx_bits, slot_w, k_over, words, over_words

    @staticmethod
    def _bitread(words: List[int], start_bit: int, width: int) -> int:
        if width == 0:
            return 0
        w_idx = start_bit // 32
        w_off = start_bit % 32
        need = width
        got = 0
        acc = 0
        while need > 0:
            chunk = min(32 - w_off, need)
            part = (words[w_idx] >> w_off) & ((1 << chunk) - 1)
            acc |= part << got
            got += chunk
            need -= chunk
            w_idx += 1
            w_off = 0
        return acc

    def decompress(self, blob: bytes, n: int | None = None) -> List[int]:
        N, kprime, idx_bits, slot_w, k_over, words, over_words = self._parse(blob)
        if n is None:
            n = N

        flags: List[int] = []
        payloads: List[int] = []
        bitpos = 0
        for _ in range(n):
            f = self._bitread(words, bitpos, 1)
            bitpos += 1
            if f == 0:
                p = self._bitread(words, bitpos, kprime)
                used = 1 + kprime
                bitpos += kprime
            else:
                w_idx = max(1, idx_bits)
                p = self._bitread(words, bitpos, w_idx)
                used = 1 + w_idx
                bitpos += w_idx
            pad = slot_w - used
            if pad > 0:
                bitpos += pad
            flags.append(f)
            payloads.append(p)

        over_vals: List[int] = []
        over_count = sum(flags)
        if over_count > 0:
            for j in range(over_count):
                start = j * max(1, k_over)
                over_vals.append(self._bitread(over_words, start, max(1, k_over)))

        out: List[int] = []
        for f, p in zip(flags, payloads):
            if f == 0:
                out.append(p)
            else:
                out.append(over_vals[p])
        return out

    def get_blob(self, blob: bytes, i: int) -> int:
        N, kprime, idx_bits, slot_w, k_over, words, over_words = self._parse(blob)
        if not (0 <= i < N):
            raise IndexError("i out of range")

        start = i * slot_w
        f = self._bitread(words, start, 1)
        start += 1
        if f == 0:
            return self._bitread(words, start, kprime)
        w_idx = max(1, idx_bits)
        idx = self._bitread(words, start, w_idx)
        off = idx * max(1, k_over)
        return self._bitread(over_words, off, max(1, k_over))

    # --- helpers for tests / compatibility ---
    @classmethod
    def from_list(cls, arr):
        """Factory helper for tests: directly create compressed instance from list."""
        self = cls()
        self.blob = self.compress(arr)
        self.n = len(arr)
        kprime, _, _, _ = _choose_kprime(arr)
        thr = 1 << kprime
        self.m = sum(1 for v in arr if v >= thr)
        return self

    def decompress_self(self):
        """Decompress internal blob to Python list."""
        return self.decompress(self.blob)

    def get(self, i: int) -> int:
        """Return the i-th integer directly from the internally stored blob."""
        return self.get_blob(self.blob, i)

    def to_list(self):
        """Return the decompressed list of all integers (for tests)."""
        return self.decompress(self.blob)


# --- alias pour compatibilité avec la factory existante ---
class BitPackingOverflow(BitPackerOverflow):
    pass
