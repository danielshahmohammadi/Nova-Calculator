import math
import pytest

from backend.calculator import Calculator, InvalidExpressionError, MathDomainError
from backend.history import CalculationHistory


@pytest.fixture
def calculator(tmp_path):
    return Calculator(history=CalculationHistory(tmp_path / "history.json"))


def test_basic_arithmetic(calculator):
    assert calculator.evaluate("2 + 3 * 4", save_history=False) == 14
    assert calculator.evaluate("(2 + 3) * 4", save_history=False) == 20
    assert calculator.evaluate("10 / 4", save_history=False) == 2.5
    assert calculator.evaluate("2 ** 3", save_history=False) == 8


def test_percent_and_symbols(calculator):
    assert calculator.evaluate("25%", save_history=False) == 0.25
    assert calculator.evaluate("2 × 3 ÷ 2", save_history=False) == 3
    assert calculator.evaluate("π", save_history=False) == pytest.approx(math.pi)


def test_scientific_functions(calculator):
    assert calculator.evaluate("sin(30)", save_history=False) == pytest.approx(0.5)
    assert calculator.evaluate("sqrt(81)", save_history=False) == 9
    assert calculator.evaluate("log(100)", save_history=False) == pytest.approx(2)
    assert calculator.evaluate("ln(e)", save_history=False) == pytest.approx(1)
    assert calculator.evaluate("factorial(5)", save_history=False) == 120


def test_angle_mode(calculator):
    calculator.set_angle_mode("RAD")
    assert calculator.evaluate("sin(pi / 2)", save_history=False) == pytest.approx(1)


def test_errors(calculator):
    with pytest.raises(MathDomainError):
        calculator.evaluate("1 / 0", save_history=False)
    with pytest.raises(MathDomainError):
        calculator.evaluate("sqrt(-1)", save_history=False)
    with pytest.raises(InvalidExpressionError):
        calculator.evaluate("__import__('os').system('echo bad')", save_history=False)
    with pytest.raises(InvalidExpressionError):
        calculator.evaluate("", save_history=False)


def test_memory(calculator):
    calculator.memory_store(10)
    calculator.memory_add(5)
    assert calculator.memory_recall() == 15
    calculator.memory_subtract(3)
    assert calculator.memory_recall() == 12
    calculator.clear_memory()
    assert calculator.memory_recall() == 0


def test_history(calculator, tmp_path):
    calculator.evaluate("4 + 6")
    items = calculator.history.get_all()
    assert items[0]["expression"] == "4 + 6"
    assert items[0]["result"] == 10
    reloaded = CalculationHistory(tmp_path / "history.json")
    assert reloaded.get_all()[0]["result"] == 10


def test_ans_uses_previous_result(calculator):
    assert calculator.evaluate("6 * 7", save_history=False) == 42
    assert calculator.evaluate("ans + 8", save_history=False) == 50


def test_inverse_trig_respects_angle_mode(calculator):
    assert calculator.evaluate("asin(1)", save_history=False) == pytest.approx(90)
    calculator.set_angle_mode("RAD")
    assert calculator.evaluate("asin(1)", save_history=False) == pytest.approx(math.pi / 2)
