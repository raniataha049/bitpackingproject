import pytest
from bitpacking.crossing import BitPackingCrossing
from bitpacking.core import WORD_BITS

def test_empty_list():
    bp = BitPackingCrossing.from_list([])
    assert bp.k == 0
    assert bp.n == 0
    assert bp.words == []
    # to_list vide
    assert bp.to_list() == []

def test_basic_12bits_roundtrip():
    nums = [1, 5, 8, 15, 31, 255, 1023, 4095]  # max=4095 -> k=12
    bp = BitPackingCrossing.from_list(nums)
    assert bp.k == 12
    assert bp.n == len(nums)
    # 8*12=96 bits -> 3 mots de 32 bits
    assert len(bp.words) == 3
    # lecture complète
    assert bp.to_list() == nums
    # accès direct
    for i, x in enumerate(nums):
        assert bp.get(i) == x

def test_crossing_boundary_behavior():
    # construit un tableau où les offsets i*k tombent près des bords de mot
    k = 12
    # 3 valeurs suffisent à traverser 2 mots si on commence tard, mais ici on teste round-trip général
    nums = [4095, 0, 2048, 7, 123, 4095, 1, 33]
    bp = BitPackingCrossing.from_list(nums)
    assert bp.k == k
    assert bp.to_list() == nums

def test_negative_not_supported():
    with pytest.raises(ValueError):
        BitPackingCrossing.from_list([1, -2, 3])
