
"""
Module: operations.py

This module contains basic arithmetic functions that perform addition, subtraction,
multiplication, division, and exponentiation of two numbers. These functions are foundational for
building more complex applications, such as calculators or financial tools.

Functions:
- add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]: Returns the sum of a and b.
- subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]: Returns the difference when b is subtracted from a.
- multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]: Returns the product of a and b.
- divide(a: Union[int, float], b: Union[int, float]) -> float: Returns the quotient when a is divided by b. Raises ValueError if b is zero.
- power(a: Union[int, float], b: Union[int, float]) -> Union[int, float]: Returns a raised to the power of b.

Usage:
These functions can be imported and used in other modules or integrated into APIs
to perform arithmetic operations based on user input.
"""
from typing import Union

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    return a + b

def subtract(a: Number, b: Number) -> Number:
    return a - b

def multiply(a: Number, b: Number) -> Number:
    return a * b

def divide(a: Number, b: Number) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

def power(a: Number, b: Number) -> Number:
    return a ** b

class Operations:
    def add(self, a, b): return add(a, b)
    def subtract(self, a, b): return subtract(a, b)
    def multiply(self, a, b): return multiply(a, b)
    def divide(self, a, b): return divide(a, b)
    def power(self, a, b): return power(a, b)

operations = Operations()
