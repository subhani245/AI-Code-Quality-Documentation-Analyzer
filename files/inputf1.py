"""
A simple calculator module demonstrating well-documented Python code.
"""

import math
from typing import Union


Number = Union[int, float]


def calculate_circle_area(radius: Number) -> float:
    """
    Calculate the area of a circle.

    Args:
        radius: Radius of the circle.

    Returns:
        The area of the circle.
    """
    return math.pi * radius ** 2


def add_numbers(first: Number, second: Number) -> Number:
    """
    Add two numbers.

    Args:
        first: First number.
        second: Second number.

    Returns:
        Sum of the two numbers.
    """
    return first + second


class Calculator:
    """Provide basic arithmetic operations."""

    def multiply(self, first: Number, second: Number) -> Number:
        """
        Multiply two numbers.

        Args:
            first: First number.
            second: Second number.

        Returns:
            Product of the two numbers.
        """
        return first * second

    def divide(self, first: Number, second: Number) -> float:
        """
        Divide the first number by the second number.

        Args:
            first: Numerator.
            second: Denominator.

        Returns:
            Result of the division.

        Raises:
            ValueError: If the denominator is zero.
        """
        if second == 0:
            raise ValueError("Cannot divide by zero.")

        return first / second


if __name__ == "__main__":
    calculator = Calculator()

    print("Addition:", add_numbers(10, 5))
    print("Multiplication:", calculator.multiply(10, 5))
    print("Division:", calculator.divide(10, 5))
    print("Circle area:", calculate_circle_area(5))