from bitpacking.overflow import BitPackingOverflow

def test_simple_overflow_example():
    nums = [1, 2, 3, 1024, 4, 5, 2048]
    bp = BitPackingOverflow.from_list(nums)
    assert bp.n == len(nums)
    out = bp.to_list()
    assert out == nums

def test_no_overflow_needed():
    nums = [1, 2, 3, 4, 5, 6]
    bp = BitPackingOverflow.from_list(nums)
    assert bp.m == 0
    assert bp.to_list() == nums

def test_get_index_individual():
    nums = [1, 2, 3, 1024, 4, 5, 2048]
    bp = BitPackingOverflow.from_list(nums)
    for i, v in enumerate(nums):
        assert bp.get(i) == v
