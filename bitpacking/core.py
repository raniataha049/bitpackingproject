WORD_BITS = 32
WORD_MASK = 0xFFFFFFFF


def words_needed(total_bits: int) -> int:
   
    if total_bits <= 0:
        return 0
    return (total_bits + WORD_BITS - 1) // WORD_BITS


def _ensure_words_capacity(words: list[int], total_bits: int) -> None:
    
    needed = words_needed(total_bits)
    if needed > len(words):
        words.extend([0] * (needed - len(words)))


def pack_bits(words: list[int], start_bit: int, value: int, width: int) -> None:
   
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
