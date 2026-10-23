from src.sequence import get_first_n, get_last


def test_get_last():
    assert get_last([1, 2, 3]) == 3


def test_get_first_n():
    assert get_first_n([1, 2, 3, 4], 2) == [1, 2, 3]
