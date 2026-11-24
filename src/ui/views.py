from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from data.ps5_store import FREE_GAMES, STORE_URL


from data.library import (
    load_games, add_game, remove_game,
    launch_game, rename_game
)


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NexusPlay")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.stack = QStackedWidget()
        self.pages = {}

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

        return page, layout

    def build_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)

        logo = QLabel("NEXUSPLAY")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.pages = {
            "Главная": self.create_page(
                "NEXUSPLAY", "Твоя игровая платформа"
            ),
            "PlayStation Store": self.create_page(
                "PlayStation Store", "Каталог PlayStation"
            ),
            "PC Store": self.create_page(
                "PC Store", "Steam • Epic Games • GOG"
            ),
            "Моя библиотека": self.create_page(
                "Моя библиотека", "Твои установленные игры"
            ),
            "Мини-игры": self.create_page(
                "Nexus Arcade", "Snake • Tetris • 2048 • Сапёр"
            ),
            "Настройки": self.create_page(
                "Настройки", "Параметры приложения"
            )
        }

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
        sidebar_layout.addWidget(version)

        main_layout.addWidget(sidebar)

        for page, layout in self.pages.values():
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack, 1)

        self.build_library()
        self.open_page("Главная")

    def build_library(self):
        page, layout = self.pages["Моя библиотека"]

        add_button = QPushButton("+ ДОБАВИТЬ ИГРУ")
        add_button.clicked.connect(self.add_game_dialog)
        layout.addWidget(add_button)

        self.game_list = QListWidget()
        self.game_list.setObjectName("GameList")
        layout.addWidget(self.game_list)

        controls = QHBoxLayout()

        play_button = QPushButton("ИГРАТЬ")
        play_button.clicked.connect(self.play_selected)

        rename_button = QPushButton("ПЕРЕИМЕНОВАТЬ")
        rename_button.clicked.connect(self.rename_selected)

        delete_button = QPushButton("УДАЛИТЬ ИЗ БИБЛИОТЕКИ")
        delete_button.clicked.connect(self.delete_selected)

        controls.addWidget(play_button)
        controls.addWidget(rename_button)
        controls.addWidget(delete_button)

        layout.addLayout(controls)

        self.refresh_library()

    def refresh_library(self):
        self.game_list.clear()

        for game in load_games():
            item = QListWidgetItem(
                game.get("name", "Без названия")
            )
            item.setData(Qt.ItemDataRole.UserRole, game.get("path"))
            self.game_list.addItem(item)

    def add_game_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбери игру",
            "",
            "Windows applications (*.exe)"
        )

        if not path:
            return

        try:
            add_game(path)
            self.refresh_library()
            QMessageBox.information(
                self, "NexusPlay", "Игра добавлена в библиотеку!"
            )
        except Exception as error:
            QMessageBox.warning(
                self, "Ошибка", str(error)
            )

    def selected_path(self):
        item = self.game_list.currentItem()

        if item is None:
            QMessageBox.information(
                self, "NexusPlay", "Сначала выбери игру."
            )
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def play_selected(self):
        path = self.selected_path()

        if not path:
            return

        try:
            launch_game(path)
        except Exception as error:
            QMessageBox.warning(
                self, "Ошибка запуска", str(error)
            )

    def delete_selected(self):
        path = self.selected_path()

        if not path:
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            "Убрать игру из библиотеки? Файлы игры останутся на компьютере."
        )

        if answer == QMessageBox.StandardButton.Yes:
            remove_game(path)
            self.refresh_library()

    def rename_selected(self):
        path = self.selected_path()

        if not path:
            return

        name, accepted = QInputDialog.getText(
            self, "Переименование", "Новое название:"
        )

        if accepted:
            try:
                rename_game(path, name)
                self.refresh_library()
            except Exception as error:
                QMessageBox.warning(
                    self, "Ошибка", str(error)
                )

    def open_page(self, name):
        page_data = self.pages.get(name)

        if page_data:
            page, _layout = page_data
            self.stack.setCurrentWidget(page)

            if name == "Моя библиотека":
                self.refresh_library()


