import numpy as np


def one():
    for i in range(10):
        yield i


def two():
    yield one()


for j in enumerate(two()):
    print(j)

a = [1, 2, 3]
print(a[:])
print(a[::])
