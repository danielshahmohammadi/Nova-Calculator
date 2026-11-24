
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QMessageBox
)


class HistoryPage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 34, 42, 34)

        header = QHBoxLayout()

        title = QLabel("History")
        title.setObjectName("pageTitle")

        header.addWidget(title)
        header.addStretch()

        clear_button = QPushButton("Clear History")
        clear_button.setObjectName("operatorButton")

        clear_button.clicked.connect(self.clear_history)

        header.addWidget(clear_button)

        layout.addLayout(header)

        self.items = QListWidget()
        self.items.setObjectName("historyList")

        layout.addWidget(self.items)

    def get_history(self):

        calculator = self.main_window.calculator_page.calculator

        return calculator.history

    def refresh(self):

        self.items.clear()

        try:

            entries = self.get_history().get_all()

            for entry in reversed(entries):

                if isinstance(entry, dict):

                    expression = entry.get("expression", "")
                    result = entry.get("result", "")

                    self.items.addItem(
                        f"{expression}    =    {result}"
                    )

                else:

                    self.items.addItem(str(entry))

            if not entries:
                self.items.addItem("No calculations yet.")

        except Exception as error:

            self.items.addItem(
                f"Could not load history: {error}"
            )

    def clear_history(self):

        try:

            self.get_history().clear()
            self.refresh()

        except Exception as error:

            QMessageBox.warning(
                self,
                "History Error",
                str(error)
            )
