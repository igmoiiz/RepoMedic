from src.compare import find_max, is_greater, is_equal


def test_is_equal():
    assert is_equal(5, 5) is True


def test_is_greater():
    assert is_greater(10, 5) is True


def test_find_max():
    assert find_max([1, 5, 3, 9, 2]) == 9
