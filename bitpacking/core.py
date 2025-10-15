WORD_BITS = 32
WORD_MASK = 0xFFFFFFFF


def words_needed(total_bits: int) -> int:
    """Return how many 32-bit words are needed to store total_bits."""
    if total_bits <= 0:
        return 0
    return (total_bits + WORD_BITS - 1) // WORD_BITS


def _ensure_words_capacity(words: list[int], total_bits: int) -> None:
    """Extend words with zeros so it can store total_bits bits."""
    needed = words_needed(total_bits)
    if needed > len(words):
        words.extend([0] * (needed - len(words)))


def pack_bits(words: list[int], start_bit: int, value: int, width: int) -> None:
    """
    Pack 'value' encoded on 'width' bits starting at absolute bit index 'start_bit'
    into the 32-bit little-endian bit layout (bit 0 is LSB of words[0]).
    Extends 'words' if necessary.

    Raises:
        ValueError if value doesn't fit in 'width' bits or if width < 0.
    """
    if width < 0:
        raise ValueError("width must be >= 0")
    if width == 0:
        return
    if value < 0 or value >= (1 << width):
        raise ValueError("value does not fit in 'width' bits")

    end_bit = start_bit + width
    _ensure_words_capacity(words, end_bit)

    pos = start_bit
    remaining = width
    val = value
    while remaining > 0:
        wi = pos // WORD_BITS
        bo = pos % WORD_BITS
        chunk = min(remaining, WORD_BITS - bo)  # bits to write in this word
        lowmask = (1 << chunk) - 1
        mask = (lowmask << bo) & WORD_MASK

        # clear target bits then OR with the piece of value
        words[wi] = (words[wi] & ~mask) | (((val & lowmask) << bo) & WORD_MASK)
        words[wi] &= WORD_MASK

        pos += chunk
        val >>= chunk
        remaining -= chunk


def unpack_bits(words: list[int], start_bit: int, width: int) -> int:
    """
    Read 'width' bits starting at absolute bit index 'start_bit' from 'words'
    and return it as a non-negative int.
    Bits beyond current words length are treated as zeros.
    """
    if width < 0:
        raise ValueError("width must be >= 0")
    if width == 0:
        return 0

    pos = start_bit
    remaining = width
    out = 0
    shift = 0

    while remaining > 0:
        wi = pos // WORD_BITS
        bo = pos % WORD_BITS
        chunk = min(remaining, WORD_BITS - bo)

        if wi >= len(words):
            piece = 0
        else:
            lowmask = (1 << chunk) - 1
            piece = (words[wi] >> bo) & lowmask

        out |= (piece << shift)
        pos += chunk
        shift += chunk
        remaining -= chunk

    return out
