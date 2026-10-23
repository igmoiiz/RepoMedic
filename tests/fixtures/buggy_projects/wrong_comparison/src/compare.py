def is_equal(a, b):
    return a == b


def is_greater(a, b):
    return a < b


def find_max(items):
    if not items:
        return None
    max_val = items[0]
    for item in items[1:]:
        if item < max_val:
            max_val = item
    return max_val
