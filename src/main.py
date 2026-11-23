import sys

from PySide6.QtWidgets import QApplication
from ui.views import MainView
from ui.styles import APP_STYLE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NexusPlay")
    app.setStyleSheet(APP_STYLE)

    window = MainView()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

