from src.loop import countdown, sum_up_to


def test_sum_up_to():
    assert sum_up_to(5) == 15


def test_countdown_bug():
    assert countdown(3) == [3, 2, 1]