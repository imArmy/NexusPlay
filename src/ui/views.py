from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from data.library import (
    load_games, add_game, remove_game,
    launch_game, rename_game
)
from data.ps5_store import FREE_GAMES, STORE_URL
from data.pc_stores import PC_STORES


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NexusPlay 2.0")
        self.resize(1250, 800)
        self.setMinimumSize(950, 650)

        self.stack = QStackedWidget()
        self.pages = {
            "Главная": self.create_page("NEXUSPLAY", "Твоя игровая платформа"),
            "PlayStation Store": self.create_page("PlayStation Store", "Игры PlayStation"),
            "PC Store": self.create_page("PC Store", "Магазины компьютерных игр"),
            "Моя библиотека": self.create_page("Моя библиотека", "Твои установленные игры"),
            "Мини-игры": self.create_page("Nexus Arcade", "Мини-игры"),
            "Настройки": self.create_page("Настройки", "Настройки приложения")
        }

        for page, layout in self.pages.values():
            self.stack.addWidget(page)

        self.build_interface()
        self.build_library()
        self.build_ps_store()
        self.build_pc_store()
        self.open_page("Главная")

    def create_page(self, title, subtitle):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        heading = QLabel(title)
        heading.setObjectName("PageTitle")
        description = QLabel(subtitle)
        description.setObjectName("Subtitle")

        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(15)
        return page, layout

    def build_interface(self):
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)

        logo = QLabel("NEXUSPLAY")
        logo.setObjectName("Logo")
        side_layout.addWidget(logo)

        for name in self.pages:
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.clicked.connect(
                lambda checked=False, n=name: self.open_page(n)
            )
            side_layout.addWidget(button)

        side_layout.addStretch()
        version = QLabel("NEXUSPLAY 2.0")
        version.setObjectName("Version")
        side_layout.addWidget(version)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

    def open_page(self, name):
        page_data = self.pages.get(name)
        if page_data:
            self.stack.setCurrentWidget(page_data[0])
            if name == "Моя библиотека":
                self.refresh_library()

    # PLAYSTATION STORE

    def build_ps_store(self):
        page, layout = self.pages["PlayStation Store"]

        self.ps_search = QLineEdit()
        self.ps_search.setPlaceholderText("Поиск игр PlayStation...")
        layout.addWidget(self.ps_search)

        self.ps_game_list = QListWidget()
        layout.addWidget(self.ps_game_list)

        button = QPushButton("ОТКРЫТЬ В PLAYSTATION STORE")
        button.clicked.connect(self.open_ps_game)
        layout.addWidget(button)

        self.ps_search.textChanged.connect(self.filter_ps_games)
        self.filter_ps_games("")

    def filter_ps_games(self, text):
        self.ps_game_list.clear()
        for game in FREE_GAMES:
            if text.lower() in game["name"].lower():
                item = QListWidgetItem(
                    f'{game["name"]} • {game["platform"]} • {game["price"]}'
                )
                item.setData(Qt.ItemDataRole.UserRole, game["name"])
                self.ps_game_list.addItem(item)

    def open_ps_game(self):
        item = self.ps_game_list.currentItem()
        if not item:
            QMessageBox.information(self, "PlayStation Store", "Выбери игру.")
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        encoded = QUrl.toPercentEncoding(name).data().decode()
        QDesktopServices.openUrl(
            QUrl(STORE_URL + "en-us/search/" + encoded)
        )

    # PC STORE

    def build_pc_store(self):
        page, layout = self.pages["PC Store"]

        for store in PC_STORES:
            card = QFrame()
            card.setObjectName("Sidebar")
            card_layout = QVBoxLayout(card)

            title = QLabel(store["name"])
            title.setStyleSheet("font-size: 22px; font-weight: bold;")
            description = QLabel(store["description"])

            buttons = QHBoxLayout()

            main_button = QPushButton("Открыть магазин")
            main_button.clicked.connect(
                lambda checked=False, url=store["url"]: self.open_url(url)
            )

            free_button = QPushButton("Бесплатные игры")
            free_button.clicked.connect(
                lambda checked=False, url=store["free_url"]: self.open_url(url)
            )

            buttons.addWidget(main_button)
            buttons.addWidget(free_button)

            card_layout.addWidget(title)
            card_layout.addWidget(description)
            card_layout.addLayout(buttons)
            layout.addWidget(card)

        layout.addStretch()

    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

    # MY LIBRARY

    def build_library(self):
        page, layout = self.pages["Моя библиотека"]

        buttons = QHBoxLayout()

        add_button = QPushButton("Добавить игру")
        add_button.clicked.connect(self.add_library_game)

        launch_button = QPushButton("Запустить")
        launch_button.clicked.connect(self.launch_library_game)

        rename_button = QPushButton("Переименовать")
        rename_button.clicked.connect(self.rename_library_game)

        remove_button = QPushButton("Удалить из списка")
        remove_button.clicked.connect(self.remove_library_game)

        for button in (add_button, launch_button, rename_button, remove_button):
            buttons.addWidget(button)

        layout.addLayout(buttons)
        self.game_list = QListWidget()
        layout.addWidget(self.game_list)

    def refresh_library(self):
        self.game_list.clear()
        for game in load_games():
            item = QListWidgetItem(game["name"])
            item.setData(Qt.ItemDataRole.UserRole, game["path"])
            self.game_list.addItem(item)

    def selected_game_path(self):
        item = self.game_list.currentItem()
        if not item:
            QMessageBox.information(self, "Библиотека", "Сначала выбери игру.")
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def add_library_game(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбери EXE-файл игры", "", "Программы (*.exe)"
        )
        if not path:
            return
        try:
            add_game(path)
            self.refresh_library()
        except Exception as error:
            QMessageBox.warning(self, "Ошибка", str(error))

    def launch_library_game(self):
        path = self.selected_game_path()
        if not path:
            return
        try:
            launch_game(path)
        except Exception as error:
            QMessageBox.warning(self, "Ошибка", str(error))

    def rename_library_game(self):
        path = self.selected_game_path()
        if not path:
            return
        name, ok = QInputDialog.getText(
            self, "Переименование", "Новое название:"
        )
        if ok:
            try:
                rename_game(path, name)
                self.refresh_library()
            except Exception as error:
                QMessageBox.warning(self, "Ошибка", str(error))

    def remove_library_game(self):
        path = self.selected_game_path()
        if not path:
            return
        answer = QMessageBox.question(
            self, "Удаление",
            "Убрать игру из библиотеки? Сам файл игры останется."
        )
        if answer == QMessageBox.StandardButton.Yes:
            remove_game(path)
            self.refresh_library()
