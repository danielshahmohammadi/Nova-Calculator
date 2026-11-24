
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget
)

from frontend.calculator_ui import CalculatorPage
from frontend.history_ui import HistoryPage
from frontend.settings_ui import SettingsPage


BASE_DIR = Path(__file__).resolve().parent.parent


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NOVA Calculator")
        self.resize(1100, 720)
        self.setMinimumSize(850, 580)

        self.angle_mode = "DEG"
        self.current_theme = "dark"

        self.create_ui()
        self.apply_theme()

    def create_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 28, 18, 20)

        logo = QLabel("NOVA")
        logo.setObjectName("logo")

        subtitle = QLabel("CALCULATOR")
        subtitle.setObjectName("subtitle")

        side_layout.addWidget(logo)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(30)

        # Navigation buttons
        buttons = [
            ("Calculator", 0),
            ("History", 1),
            ("Settings", 2)
        ]

        for text, index in buttons:

            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setCursor(Qt.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, i=index: self.show_page(i)
            )

            side_layout.addWidget(button)

        side_layout.addStretch()

        version = QLabel("NOVA Calculator  •  v1.0")
        version.setObjectName("version")

        side_layout.addWidget(version)

        # Pages
        self.stack = QStackedWidget()

        self.calculator_page = CalculatorPage(self)
        self.history_page = HistoryPage(self)
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(self.calculator_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

    def show_page(self, index):

        self.stack.setCurrentIndex(index)

        if index == 1:
            self.history_page.refresh()

    def set_angle_mode(self, mode):

        if mode not in ("DEG", "RAD"):
            return

        self.angle_mode = mode
        self.calculator_page.update_angle_mode(mode)

    def apply_theme(self):

        theme_file = (
            "dark.qss"
            if self.current_theme == "dark"
            else "light.qss"
        )

        style_path = BASE_DIR / "styles" / theme_file

        if style_path.exists():

            with open(style_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
