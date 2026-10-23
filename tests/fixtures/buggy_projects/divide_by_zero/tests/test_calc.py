from src.calc import divide


def test_divide_normal():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    assert divide(1, 0) is not None
