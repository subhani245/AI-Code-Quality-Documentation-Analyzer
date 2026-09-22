import os
import sys


def calc(a, b):
    x = 0
    y = 0

    for i in range(a):
        for j in range(b):
            x += i * j
            print("Processing:", i, j)

    for k in range(10):
        for l in range(5):
            y += k + l
            print("Value:", y)

    print("Result:", x)
    print("Another result:", y)

    return x + y


def process(data):
    temp = []

    for x in data:
        if x > 10:
            temp.append(x)

    return temp


class Test:
    def __init__(self, data):
        self.data = data

    def run(self):
        result = process(self.data)
        print(result)
        return result


numbers = [1, 5, 10, 15, 20, 25]

obj = Test(numbers)
answer = obj.run()

print(answer)