
"""Safe expression evaluation and calculator state for NOVA Calculator."""
from __future__ import annotations

import ast
import math
import re

from backend.history import CalculationHistory
from backend.scientific import ScientificFunctions


class CalculatorError(ValueError):
    pass


class InvalidExpressionError(CalculatorError):
    pass


class MathDomainError(CalculatorError):
    pass


class Calculator:
    def __init__(self, angle_mode: str = "DEG", history: CalculationHistory | None = None):
        self.scientific = ScientificFunctions(angle_mode)
        self.history = history or CalculationHistory()
        self._memory = 0.0
        self._answer = 0.0

    def set_angle_mode(self, mode: str) -> None:
        self.scientific.set_angle_mode(mode)

    def memory_store(self, value: float) -> float:
        self._memory = float(value)
        return self._memory

    def memory_recall(self) -> float:
        return self._memory

    def memory_add(self, value: float) -> float:
        self._memory += float(value)
        return self._memory

    def memory_subtract(self, value: float) -> float:
        self._memory -= float(value)
        return self._memory

    def clear_memory(self) -> float:
        self._memory = 0.0
        return self._memory

    def _normalize(self, expression: str) -> str:
        if not isinstance(expression, str) or not expression.strip():
            raise InvalidExpressionError("Expression cannot be empty.")
        normalized = expression.strip()
        normalized = normalized.replace("×", "*").replace("÷", "/").replace("−", "-")
        normalized = normalized.replace("π", "pi")
        normalized = re.sub(r"(?<![\w.])(\d+(?:\.\d+)?)%", r"(\1/100)", normalized)
        return normalized

    def evaluate(self, expression: str, save_history: bool = True) -> float:
        normalized = self._normalize(expression)
        try:
            tree = ast.parse(normalized, mode="eval")
        except (SyntaxError, ValueError) as error:
            raise InvalidExpressionError("Invalid expression.") from error

        try:
            result = float(self._eval_node(tree.body))
            if not math.isfinite(result):
                raise MathDomainError("Result is outside the supported numeric range.")
        except (InvalidExpressionError, MathDomainError):
            raise
        except (ArithmeticError, OverflowError, ZeroDivisionError, ValueError) as error:
            raise MathDomainError(str(error)) from error

        self._answer = result
        if save_history:
            self.history.add(normalized, result)
        return int(result) if result.is_integer() else result

    def _eval_node(self, node: ast.AST):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise InvalidExpressionError("Only numeric constants are allowed.")
            return node.value

        if isinstance(node, ast.Name):
            if node.id == "pi":
                return math.pi
            if node.id == "e":
                return math.e
            if node.id == "ans":
                return self._answer
            raise InvalidExpressionError(f"Unknown name: {node.id}")

        if isinstance(node, ast.UnaryOp):
            value = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value
            raise InvalidExpressionError("Unsupported unary operation.")

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("Division by zero.")
                return left / right
            if isinstance(node.op, ast.Pow):
                result = left ** right
                if isinstance(result, complex):
                    raise MathDomainError("Complex results are not supported.")
                return result
            if isinstance(node.op, ast.Mod):
                raise InvalidExpressionError("Modulo is not supported.")
            raise InvalidExpressionError("Unsupported binary operation.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise InvalidExpressionError("Invalid function call.")
            methods = {
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
            if node.func.id not in methods:
                raise InvalidExpressionError(f"Unknown function: {node.func.id}")
            arguments = [self._eval_node(argument) for argument in node.args]
            if node.func.id == "log" and len(arguments) not in (1, 2):
                raise InvalidExpressionError("log expects one or two arguments.")
            if node.func.id != "log" and len(arguments) != 1:
                raise InvalidExpressionError(f"{node.func.id} expects one argument.")
            try:
                return methods[node.func.id](*arguments)
            except (ValueError, OverflowError) as error:
                raise MathDomainError(str(error)) from error

        raise InvalidExpressionError("Unsupported expression.")


from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

class CalculatorPage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.calculator = calculator(
            angle_mode=main_window.angle_mode
        )

        self.scientific_mode = False
        self.last_result = None

        self.create_ui()
        self.create_shortcuts()

    def create_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(42, 30, 42, 30)
        main_layout.setSpacing(15)

        # Header
        header = QHBoxLayout()

        title = QLabel("NOVA Calculator")
        title.setObjectName("pageTitle")

        header.addWidget(title)
        header.addStretch()

        self.mode_label = QLabel("DEG")
        self.mode_label.setObjectName("modeLabel")

        header.addWidget(self.mode_label)

        self.scientific_button = QPushButton("Scientific Mode")
        self.scientific_button.setObjectName("operatorButton")

        self.scientific_button.clicked.connect(
            self.toggle_scientific_mode
        )

        header.addWidget(self.scientific_button)

        main_layout.addLayout(header)

        # Expression input
        self.expression = QLineEdit()

        self.expression.setObjectName("expressionInput")
        self.expression.setPlaceholderText("Enter an expression...")
        self.expression.setAlignment(Qt.AlignRight)
        self.expression.setMinimumHeight(60)

        self.expression.returnPressed.connect(self.calculate)

        main_layout.addWidget(self.expression)

        # Result
        self.result_label = QLabel("0")

        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.result_label.setMinimumHeight(60)

        main_layout.addWidget(self.result_label)

        # Memory buttons
        memory_layout = QHBoxLayout()

        memory_buttons = [
            ("MC", self.memory_clear),
            ("MR", self.memory_recall),
            ("M+", self.memory_add),
            ("M−", self.memory_subtract),
            ("MS", self.memory_store)
        ]

        for text, function in memory_buttons:

            button = QPushButton(text)
            button.setObjectName("operatorButton")
            button.setMinimumHeight(42)

            button.clicked.connect(function)

            memory_layout.addWidget(button)

        main_layout.addLayout(memory_layout)

        # Scientific buttons
        self.scientific_widget = QWidget()

        scientific_layout = QGridLayout(
            self.scientific_widget
        )

        scientific_layout.setSpacing(8)

        scientific_buttons = [
            ["sin", "cos", "tan", "asin", "acos"],
            ["atan", "sqrt", "log", "ln", "exp"],
            ["factorial", "abs", "(", ")", "ans"]
        ]

        for row, values in enumerate(scientific_buttons):

            for col, value in enumerate(values):

                button = QPushButton(value)

                button.setObjectName("operatorButton")
                button.setMinimumHeight(42)

                button.clicked.connect(
                    lambda checked=False, v=value:
                    self.add_scientific_function(v)
                )

                scientific_layout.addWidget(
                    button,
                    row,
                    col
                )

        self.scientific_widget.setVisible(False)

        main_layout.addWidget(self.scientific_widget)

        # Main calculator buttons
        grid = QGridLayout()
        grid.setSpacing(9)

        buttons = [
            ["AC", "DEL", "(", ")"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "%", "+"],
            ["ANS", "!", "=", " "]
        ]

        for row, values in enumerate(buttons):

            for col, value in enumerate(values):

                if value == " ":
                    continue

                button = QPushButton(value)

                button.setMinimumHeight(55)
                button.setCursor(Qt.PointingHandCursor)

                if value.isdigit() or value == ".":
                    button.setObjectName("numberButton")
                else:
                    button.setObjectName("operatorButton")

                button.clicked.connect(
                    lambda checked=False, v=value:
                    self.handle_button(v)
                )

                grid.addWidget(button, row, col)

        main_layout.addLayout(grid)
        main_layout.addStretch()

        hint = QLabel(
            "Enter: Calculate    |    Esc: Clear    |    "
            "Backspace: Delete"
        )

        hint.setObjectName("hint")

        main_layout.addWidget(hint)

    # Keyboard shortcuts
    def create_shortcuts(self):

        self.enter_shortcut = QShortcut(
            QKeySequence("Escape"),
            self
        )

        self.enter_shortcut.activated.connect(
            self.clear_all
        )

        self.delete_shortcut = QShortcut(
            QKeySequence("Backspace"),
            self
        )

        self.delete_shortcut.activated.connect(
            self.delete_last
        )

    # Scientific mode
    def toggle_scientific_mode(self):

        self.scientific_mode = not self.scientific_mode

        self.scientific_widget.setVisible(
            self.scientific_mode
        )

        if self.scientific_mode:
            self.scientific_button.setText("Basic Mode")
        else:
            self.scientific_button.setText("Scientific Mode")

    def add_scientific_function(self, value):

        current = self.expression.text()

        if value == "ans":
            text = "ans"

        elif value == "factorial":
            text = "factorial("

        elif value in ("(", ")"):
            text = value

        else:
            text = value + "("

        self.expression.insert(text)
        self.expression.setFocus()

    # Main buttons
    def handle_button(self, value):

        if value == "AC":
            self.clear_all()

        elif value == "DEL":
            self.delete_last()

        elif value == "=":
            self.calculate()

        elif value == "ANS":
            self.expression.insert("ans")

        elif value == "!":
            self.expression.insert("factorial(")

        elif value in ("×", "÷", "−"):

            symbols = {
                "×": "*",
                "÷": "/",
                "−": "-"
            }

            self.expression.insert(symbols[value])

        else:
            self.expression.insert(value)

        self.expression.setFocus()

    def clear_all(self):

        self.expression.clear()
        self.result_label.setText("0")

    def delete_last(self):

        current = self.expression.text()

        if current:
            self.expression.setText(current[:-1])

        self.expression.setFocus()
        self.expression.setCursorPosition(
            len(self.expression.text())
        )

    # Calculation
    def calculate(self):

        expression = self.expression.text().strip()

        if not expression:
            return

        try:

            result = self.calculator.evaluate(expression)

            self.last_result = result

            self.result_label.setText(str(result))

        except Exception as error:

            QMessageBox.warning(
                self,
                "Calculation Error",
                str(error)
            )

    # Angle mode
    def update_angle_mode(self, mode):

        self.mode_label.setText(mode)

        self.calculator.set_angle_mode(mode)

    # Memory functions
    def get_current_result(self):

        if self.last_result is None:
            raise ValueError("There is no result to store.")

        return float(self.last_result)

    def memory_store(self):

        try:

            value = self.get_current_result()

            self.calculator.memory_store(value)

        except Exception as error:

            QMessageBox.warning(
                self,
                "Memory Error",
                str(error)
            )

    def memory_recall(self):

        try:

            value = self.calculator.memory_recall()

            self.expression.insert(str(value))

            self.expression.setFocus()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Memory Error",
                str(error)
            )

    def memory_add(self):

        try:

            value = self.get_current_result()

            self.calculator.memory_add(value)

        except Exception as error:

            QMessageBox.warning(
                self,
                "Memory Error",
                str(error)
            )

    def memory_subtract(self):

        try:

            value = self.get_current_result()

            self.calculator.memory_subtract(value)

        except Exception as error:

            QMessageBox.warning(
                self,
                "Memory Error",
                str(error)
            )

    def memory_clear(self):

        try:

            self.calculator.clear_memory()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Memory Error",
                str(error)
            )
