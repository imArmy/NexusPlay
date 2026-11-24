from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent
import random


class ArcadeGame(QWidget):
    def __init__(self, game="2048"):
        super().__init__()
        self.game = game
        self.setWindowTitle("Nexus Arcade")
        self.resize(450, 550)

        layout = QVBoxLayout(self)
        self.title = QLabel(game)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.board = QLabel()
        self.board.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.board.setStyleSheet(
            "font-size: 22px; background: #101a30; padding: 20px;"
        )

        restart = QPushButton("Новая игра")
        restart.clicked.connect(self.start_game)

        layout.addWidget(self.title)
        layout.addWidget(self.board, 1)
        layout.addWidget(restart)

        self.start_game()

    def start_game(self):
        if self.game == "2048":
            self.grid = [[0] * 4 for _ in range(4)]
            self.spawn()
            self.spawn()
            self.render_2048()
        elif self.game == "Snake":
            self.snake = [(5, 5), (4, 5), (3, 5)]
            self.direction = (1, 0)
            self.food = (8, 5)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.move_snake)
            self.timer.start(180)
            self.render_snake()
        elif self.game == "Сапёр":
            self.mines = random.sample(range(64), 10)
            self.revealed = set()
            self.render_mines()
        elif self.game == "Tetris":
            self.tetris = [[0] * 10 for _ in range(15)]
            self.render_tetris()

        self.setFocus()

    def spawn(self):
        empty = [(r, c) for r in range(4) for c in range(4)
                 if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 2 if random.random() < 0.9 else 4

    def render_2048(self):
        self.board.setText("\n".join(
            "   ".join(str(x or ".") for x in row)
            for row in self.grid
        ))

    def render_snake(self):
        rows = []
        for y in range(10):
            row = ""
            for x in range(10):
                if (x, y) in self.snake:
                    row += " 🟦"
                elif (x, y) == self.food:
                    row += " 🍎"
                else:
                    row += " ⬛"
            rows.append(row)
        self.board.setText("\n".join(rows))

    def move_snake(self):
        head = self.snake[0]
        new = (head[0] + self.direction[0],
               head[1] + self.direction[1])
        if (new[0] < 0 or new[0] >= 10 or
                new[1] < 0 or new[1] >= 10 or new in self.snake):
            self.timer.stop()
            QMessageBox.information(self, "Snake", "Игра окончена!")
            return
        self.snake.insert(0, new)
        if new == self.food:
            empty = [(x, y) for x in range(10) for y in range(10)
                     if (x, y) not in self.snake]
            if empty:
                self.food = random.choice(empty)
        else:
            self.snake.pop()
        self.render_snake()

    def render_mines(self):
        rows = []
        for i in range(64):
            if i in self.revealed:
                rows.append("💣" if i in self.mines else "▫️")
            else:
                rows.append("⬜")
        self.board.setText(" ".join(rows))

    def render_tetris(self):
        self.board.setText(
            "TETRIS\n\n"
            "Игровое поле 10 × 15\n\n"
            "Управление: ← → ↓\n"
            "Пробел — вращение\n\n"
            "Модуль поля подготовлен."
        )

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if self.game == "2048":
            self.move_2048(key)
        elif self.game == "Snake":
            directions = {
                Qt.Key.Key_Up: (0, -1),
                Qt.Key.Key_Down: (0, 1),
                Qt.Key.Key_Left: (-1, 0),
                Qt.Key.Key_Right: (1, 0)
            }
            new_direction = directions.get(key)
            if new_direction and new_direction != (
                -self.direction[0], -self.direction[1]
            ):
                self.direction = new_direction

    def move_2048(self, key):
        if key not in (
            Qt.Key.Key_Left, Qt.Key.Key_Right,
            Qt.Key.Key_Up, Qt.Key.Key_Down
        ):
            return

        old = [row[:] for row in self.grid]

        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            for row in self.grid:
                values = [x for x in row if x]
                if key == Qt.Key.Key_Right:
                    values.reverse()
                merged = []
                i = 0
                while i < len(values):
                    if i + 1 < len(values) and values[i] == values[i + 1]:
                        merged.append(values[i] * 2)
                        i += 2
                    else:
                        merged.append(values[i])
                        i += 1
                merged += [0] * (4 - len(merged))
                if key == Qt.Key.Key_Right:
                    merged.reverse()
                row[:] = merged
        else:
            for c in range(4):
                values = [self.grid[r][c] for r in range(4) if self.grid[r][c]]
                if key == Qt.Key.Key_Down:
                    values.reverse()
                merged = []
                i = 0
                while i < len(values):
                    if i + 1 < len(values) and values[i] == values[i + 1]:
                        merged.append(values[i] * 2)
                        i += 2
                    else:
                        merged.append(values[i])
                        i += 1
                merged += [0] * (4 - len(merged))
                if key == Qt.Key.Key_Down:
                    merged.reverse()
                for r in range(4):
                    self.grid[r][c] = merged[r]

        if old != self.grid:
            self.spawn()
            self.render_2048()
