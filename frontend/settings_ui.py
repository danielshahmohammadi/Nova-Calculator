
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QFormLayout
)


class SettingsPage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 34, 42, 34)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")

        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(18)

        # Angle mode
        self.angle_combo = QComboBox()

        self.angle_combo.addItems([
            "DEG",
            "RAD"
        ])

        self.angle_combo.setCurrentText(
            main_window.angle_mode
        )

        self.angle_combo.currentTextChanged.connect(
            main_window.set_angle_mode
        )

        form.addRow("Angle Unit", self.angle_combo)

        # Theme
        self.theme_combo = QComboBox()

        self.theme_combo.addItems([
            "Dark",
            "Light"
        ])

        self.theme_combo.setCurrentText("Dark")

        self.theme_combo.currentTextChanged.connect(
            self.change_theme
        )

        form.addRow("Appearance", self.theme_combo)

        layout.addLayout(form)

        about = QLabel(
            "NOVA Calculator\n"
            "A desktop calculator built with Python and PySide6."
        )

        about.setObjectName("hint")
        about.setWordWrap(True)

        layout.addWidget(about)
        layout.addStretch()

    def change_theme(self, theme):

        self.main_window.current_theme = theme.lower()

        self.main_window.apply_theme()
