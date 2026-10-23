def countdown(n):
    result = []
    while n > 0:
        result.append(n)
        n = n - 2  # Bug: should be n - 1
    return result


def sum_up_to(n):
    total = 0
    i = 0
    while i <= n:
        total += i
        i += 1
    return total