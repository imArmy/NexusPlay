from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame
)
from PySide6.QtCore import Qt


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NexusPlay")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.stack = QStackedWidget()

        self.pages = {
            "Главная": self.create_page(
                "NEXUSPLAY",
                "Твоя игровая платформа"
            ),
            "PlayStation Store": self.create_page(
                "PlayStation Store",
                "Каталог игр PlayStation"
            ),
            "PC Store": self.create_page(
                "PC Store",
                "Steam • Epic Games • GOG • itch.io"
            ),
            "Моя библиотека": self.create_page(
                "Моя библиотека",
                "Твои установленные игры"
            ),
            "Мини-игры": self.create_page(
                "Nexus Arcade",
                "Snake • Tetris • 2048 • Сапёр"
            ),
            "Настройки": self.create_page(
                "Настройки",
                "Настройки приложения"
            )
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.build_interface()

    def create_page(self, title, subtitle):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("Subtitle")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()

        return page

    def build_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(10)

        logo = QLabel("NEXUSPLAY")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        sidebar_layout.addSpacing(25)

        for name in self.pages:
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, n=name: self.open_page(n)
            )
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        version = QLabel("NEXUSPLAY 2.0")
        version.setObjectName("Version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        self.open_page("Главная")

    def open_page(self, name):
        page = self.pages.get(name)

        if page:
            self.stack.setCurrentWidget(page)
