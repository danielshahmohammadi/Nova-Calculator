"""Basic arithmetic operations used by NOVA Calculator."""
import math


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("تقسیم بر صفر مجاز نیست.")
    return a / b


def power(a: float, b: float) -> float:
    result = a ** b
    if isinstance(result, complex):
        raise ValueError("نتیجه مختلط در این ماشین‌حساب پشتیبانی نمی‌شود.")
    if not math.isfinite(float(result)):
        raise OverflowError("نتیجه خارج از محدوده قابل نمایش است.")
    return result


def percentage(value: float) -> float:
    """Convert a value to its percentage fraction (e.g. 25 -> 0.25)."""
    return value / 100.0
