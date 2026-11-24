
from PySide6.QtCore import Qt
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

from backend.calculator import Calculator


class CalculatorPage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.calculator = Calculator(
            angle_mode=main_window.angle_mode
        )

        self.create_ui()

    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(42, 34, 42, 34)
        layout.setSpacing(18)

        # Header
        header = QHBoxLayout()

        title = QLabel("Calculator")
        title.setObjectName("pageTitle")

        header.addWidget(title)
        header.addStretch()

        self.mode_label = QLabel("DEG")
        self.mode_label.setObjectName("modeLabel")

        header.addWidget(self.mode_label)

        layout.addLayout(header)

        # Expression input
        self.expression = QLineEdit()

        self.expression.setObjectName("expressionInput")
        self.expression.setPlaceholderText("Enter an expression...")
        self.expression.setAlignment(Qt.AlignRight)
        self.expression.setMinimumHeight(62)

        self.expression.returnPressed.connect(self.calculate)

        layout.addWidget(self.expression)

        # Result
        self.result_label = QLabel("0")

        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.result_label.setMinimumHeight(64)

        layout.addWidget(self.result_label)

        # Buttons
        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            ["AC", "DEL", "(", ")"],
            ["sin", "cos", "tan", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "%", "="]
        ]

        operators = [
            "AC", "DEL", "(", ")",
            "sin", "cos", "tan",
            "÷", "×", "−", "+", "%", "="
        ]

        for row, values in enumerate(buttons):

            for col, value in enumerate(values):

                button = QPushButton(value)

                if value in operators:
                    button.setObjectName("operatorButton")
                else:
                    button.setObjectName("numberButton")

                button.setMinimumHeight(62)
                button.setCursor(Qt.PointingHandCursor)

                button.clicked.connect(
                    lambda checked=False, v=value:
                    self.handle_button(v)
                )

                grid.addWidget(button, row, col)

        layout.addLayout(grid)
        layout.addStretch()

        hint = QLabel(
            "Tip: You can also type an expression using your keyboard."
        )

        hint.setObjectName("hint")

        layout.addWidget(hint)

    def update_angle_mode(self, mode):

        self.mode_label.setText(mode)
        self.calculator.set_angle_mode(mode)

    def handle_button(self, value):

        current = self.expression.text()

        if value == "AC":

            self.expression.clear()
            self.result_label.setText("0")

        elif value == "DEL":

            self.expression.setText(current[:-1])

        elif value == "=":

            self.calculate()

        elif value in ("sin", "cos", "tan"):

            self.expression.setText(
                current + value + "("
            )

        elif value in ("×", "÷", "−"):

            symbols = {
                "×": "*",
                "÷": "/",
                "−": "-"
            }

            self.expression.setText(
                current + symbols[value]
            )

        else:

            self.expression.setText(current + value)

        self.expression.setFocus()
        self.expression.setCursorPosition(
            len(self.expression.text())
        )

    def calculate(self):

        expression = self.expression.text().strip()

        if not expression:
            return

        try:

            result = self.calculator.evaluate(expression)

            self.result_label.setText(str(result))

        except Exception as error:

            QMessageBox.warning(
                self,
                "Calculation Error",
                str(error)
            )
