from functools import reduce
foo = [2, 18, 9, 22, 17, 24, 8, 12, 27]
print(reduce(lambda x, y: x + y, foo))
