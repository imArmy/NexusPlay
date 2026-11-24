APP_STYLE = """
QMainWindow {
    background-color: #070b16;
}

QWidget {
    background-color: #070b16;
    color: #f4f7ff;
    font-family: "Segoe UI";
    font-size: 14px;
}

#Sidebar {
    background-color: #101a30;
    border: 1px solid #203354;
    border-radius: 18px;
}

#Logo {
    color: #168cff;
    font-size: 27px;
    font-weight: 900;
    padding: 15px;
}

#PageTitle {
    color: #ffffff;
    font-size: 34px;
    font-weight: 800;
}

#Subtitle {
    color: #94a8c9;
    font-size: 14px;
}

#NavButton {
    background-color: transparent;
    color: #c5d2e9;
    border: none;
    border-radius: 10px;
    padding: 14px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}

#NavButton:hover {
    background-color: #1b3154;
    color: white;
}

#NavButton:pressed {
    background-color: #168cff;
}

#Version {
    color: #7184a5;
    font-size: 10px;
    font-weight: bold;
    padding: 8px;
}

QPushButton {
    background-color: #167bea;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 18px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #369dff;
}

QPushButton:pressed {
    background-color: #0756ad;
}

QLineEdit {
    background-color: #14223b;
    border: 1px solid #263d62;
    border-radius: 10px;
    padding: 12px;
    color: white;
    selection-background-color: #168cff;
}

QListWidget {
    background-color: #101a30;
    border: 1px solid #203354;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    background-color: #172642;
    border-radius: 8px;
    padding: 14px;
    margin: 4px;
}

QListWidget::item:hover {
    background-color: #213c64;
}

QListWidget::item:selected {
    background-color: #167bea;
    color: white;
}

QLabel {
    background-color: transparent;
}

QMessageBox {
    background-color: #101a30;
}

QInputDialog {
    background-color: #101a30;
}
"""
