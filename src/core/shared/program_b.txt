def fib_iter(n):
    if n <= 1:
        return n
    a = 0
    b = 1
    for i in range(2, n + 1):
        temp = a + b
        a = b
        b = temp
    return b

print(fib_iter(6))
