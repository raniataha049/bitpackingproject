import pytest
from bitpacking.core import words_needed, pack_bits, unpack_bits

def test_words_needed_basic():
    assert words_needed(0) == 0
    assert words_needed(1) == 1
    assert words_needed(31) == 1
    assert words_needed(32) == 1
    assert words_needed(33) == 2
    assert words_needed(64) == 2

def test_pack_unpack_single_word_middle():
    words = []
    # écrire 5 bits (0b10101 = 21) à partir du bit 3 du mot 0
    pack_bits(words, start_bit=3, value=0b10101, width=5)
    assert len(words) == 1
    got = unpack_bits(words, start_bit=3, width=5)
    assert got == 0b10101

def test_cross_word_boundary():
    words = []
    # écrire 20 bits qui commencent au bit 28 -> traverse sur 2 mots
    val = int("1010_1111_0001_0110_10".replace("_",""), 2)  # juste une valeur non-triviale
    pack_bits(words, start_bit=28, value=val, width=20)
    assert len(words) == 2
    got = unpack_bits(words, start_bit=28, width=20)
    assert got == val

def test_sequential_12bit_values():
    nums = [1, 5, 8, 15, 31, 255, 1023, 4095]
    k = 12
    words = []
    # pack en séquence sans espace : offsets i*k (mode crossing logique)
    for i, x in enumerate(nums):
        pack_bits(words, start_bit=i*k, value=x, width=k)
    # 8*12 = 96 bits -> 3 mots
    assert len(words) == 3
    # vérifier lecture
    for i, x in enumerate(nums):
        assert unpack_bits(words, start_bit=i*k, width=k) == x

def test_overwrite_bits_clears_previous():
    words = []
    pack_bits(words, 0, (1<<12)-1, 12)    # 0xFFF
    pack_bits(words, 0, 0, 12)            # overwrite with zeros
    assert unpack_bits(words, 0, 12) == 0

def test_invalid_value_raises():
    words = []
    with pytest.raises(ValueError):
        pack_bits(words, 0, value=8, width=3)  # 8 ne tient pas sur 3 bits
