"""Safe expression evaluator and calculator state for NOVA Calculator."""
from __future__ import annotations

import ast
import math
import operator
import re
from typing import Callable

from .history import CalculationHistory
from .operations import percentage
from .scientific import ScientificFunctions


class CalculatorError(Exception):
    """Base class for calculator errors."""


class InvalidExpressionError(CalculatorError):
    """Raised when an expression contains unsupported syntax."""


class MathDomainError(CalculatorError):
    """Raised when a mathematical operation is undefined."""


_BINARY_OPERATORS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPERATORS: dict[type, Callable] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MAX_EXPRESSION_LENGTH = 300
_MAX_AST_NODES = 100
_MAX_ABS_RESULT = 1e300


class Calculator:
    """Calculator engine. Percent is postfix fraction: 25% evaluates to 0.25."""

    def __init__(
        self,
        angle_mode: str = "DEG",
        history: CalculationHistory | None = None,
    ):
        self.scientific = ScientificFunctions(angle_mode)
        self.history = history or CalculationHistory()
        self.memory = 0.0
        self.last_result = 0.0

    @property
    def angle_mode(self) -> str:
        return self.scientific.angle_mode

    def set_angle_mode(self, mode: str) -> None:
        self.scientific.set_angle_mode(mode)

    def clear_memory(self) -> None:
        self.memory = 0.0

    def memory_recall(self) -> float:
        return self.memory

    def memory_add(self, value: float) -> float:
        self.memory += self._finite_number(value)
        return self.memory

    def memory_subtract(self, value: float) -> float:
        self.memory -= self._finite_number(value)
        return self.memory

    def memory_store(self, value: float) -> float:
        self.memory = self._finite_number(value)
        return self.memory

    def evaluate(self, expression: str, *, save_history: bool = True) -> float:
        if not isinstance(expression, str):
            raise InvalidExpressionError("عبارت باید متن باشد.")
        source = expression.strip()
        if not source:
            raise InvalidExpressionError("عبارت محاسباتی خالی است.")
        if len(source) > _MAX_EXPRESSION_LENGTH:
            raise InvalidExpressionError("طول عبارت بیش از حد مجاز است.")

        # Allow common calculator symbols without permitting arbitrary Python syntax.
        source = source.replace("×", "*").replace("÷", "/").replace("−", "-")
        source = source.replace("π", "pi").replace("√", "sqrt")
        # A postfix percent is converted into division by 100.
        source = re.sub(r"(?<=[0-9.)])\s*%", "/100", source)

        try:
            tree = ast.parse(source, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > _MAX_AST_NODES:
                raise InvalidExpressionError("عبارت بیش از حد پیچیده است.")
            result = self._evaluate_node(tree.body)
            result = self._finite_number(result)
        except CalculatorError:
            raise
        except ZeroDivisionError as exc:
            raise MathDomainError("تقسیم بر صفر مجاز نیست.") from exc
        except (ValueError, OverflowError) as exc:
            raise MathDomainError(str(exc) or "عملیات ریاضی نامعتبر است.") from exc
        except (SyntaxError, TypeError, KeyError, AttributeError) as exc:
            raise InvalidExpressionError("ساختار عبارت محاسباتی معتبر نیست.") from exc

        self.last_result = result
        if save_history:
            self.history.add(expression.strip(), result)
        return result

    def _evaluate_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise InvalidExpressionError("فقط اعداد مجاز هستند.")
            return self._finite_number(node.value)

        if isinstance(node, ast.Name):
            constants = {"pi": math.pi, "e": math.e, "ans": self.last_result}
            if node.id in constants:
                return constants[node.id]
            raise InvalidExpressionError(f"ثابت یا نام ناشناخته: {node.id}")

        if isinstance(node, ast.BinOp):
            operation = _BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise InvalidExpressionError("این عملگر پشتیبانی نمی‌شود.")
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise MathDomainError("توان واردشده بیش از حد بزرگ است.")
            return self._finite_number(operation(left, right))

        if isinstance(node, ast.UnaryOp):
            operation = _UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise InvalidExpressionError("این عملگر یکانی پشتیبانی نمی‌شود.")
            return self._finite_number(operation(self._evaluate_node(node.operand)))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise InvalidExpressionError("نحوه فراخوانی تابع معتبر نیست.")
            functions = {
                "sin": self.scientific.sin,
                "cos": self.scientific.cos,
                "tan": self.scientific.tan,
                "asin": self.scientific.asin,
                "acos": self.scientific.acos,
                "atan": self.scientific.atan,
                "sqrt": self.scientific.sqrt,
                "log": self.scientific.log,
                "ln": self.scientific.ln,
                "factorial": self.scientific.factorial,
                "abs": self.scientific.abs,
                "exp": self.scientific.exp,
            }
            function = functions.get(node.func.id)
            if function is None:
                raise InvalidExpressionError("این تابع علمی پشتیبانی نمی‌شود.")
            args = [self._evaluate_node(arg) for arg in node.args]
            if node.func.id == "log":
                if len(args) not in (1, 2):
                    raise InvalidExpressionError("log به یک یا دو آرگومان نیاز دارد.")
            elif len(args) != 1:
                raise InvalidExpressionError("این تابع دقیقاً یک آرگومان می‌پذیرد.")
            return self._finite_number(function(*args))

        raise InvalidExpressionError("این نوع عبارت مجاز نیست.")

    @staticmethod
    def _finite_number(value: float) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidExpressionError("نتیجه عددی معتبر نیست.")
        number = float(value)
        if not math.isfinite(number) or abs(number) > _MAX_ABS_RESULT:
            raise MathDomainError("نتیجه خارج از محدوده قابل پشتیبانی است.")
        return number
