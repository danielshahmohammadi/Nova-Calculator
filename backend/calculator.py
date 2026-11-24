
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

from backend.calculator import calculator


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
