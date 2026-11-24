import random

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class ArcadeGame(QWidget):
    def __init__(self, game="2048"):
        super().__init__()

        self.game = game
        self.setWindowTitle("NexusPlay Arcade — " + game)
        self.resize(520, 620)

        self.layout = QVBoxLayout(self)

        self.title = QLabel(game)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #168cff;"
        )

        self.info = QLabel("Управление: стрелки клавиатуры")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.board = QLabel()
        self.board.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.board.setFont(QFont("Consolas", 15))
        self.board.setStyleSheet(
            "background: #101a30; color: white; "
            "padding: 20px; border-radius: 15px;"
        )

        self.restart_button = QPushButton("НОВАЯ ИГРА")
        self.restart_button.clicked.connect(self.start_game)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.board, 1)
        self.layout.addWidget(self.restart_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.start_game()

    def start_game(self):
        self.timer.stop()
        self.over = False
        self.score = 0
        self.cursor = 0

        if self.game == "2048":
            self.grid = [[0] * 4 for _ in range(4)]
            self.spawn_2048()
            self.spawn_2048()
            self.render_2048()

        elif self.game == "Snake":
            self.snake = [(5, 5), (4, 5), (3, 5)]
            self.direction = (1, 0)
            self.food = (8, 5)
            self.timer.start(160)
            self.render_snake()

        elif self.game == "Tetris":
            self.grid = [[0] * 10 for _ in range(18)]
            self.shapes = [
                [(0, 0), (1, 0), (0, 1), (1, 1)],
                [(0, 0), (1, 0), (2, 0), (3, 0)],
                [(0, 0), (0, 1), (0, 2), (1, 2)],
                [(1, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (2, 0), (0, 1), (1, 1)]
            ]
            self.new_piece()
            self.timer.start(450)
            self.render_tetris()

        elif self.game == "Сапёр":
            self.mines = set(random.sample(range(100), 15))
            self.revealed = set()
            self.flags = set()
            self.cursor = 0
            self.game_won = False
            self.render_mines()

        self.setFocus()

    # 2048

    def spawn_2048(self):
        empty = [
            (r, c)
            for r in range(4)
            for c in range(4)
            if self.grid[r][c] == 0
        ]

        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 2 if random.random() < 0.9 else 4

    def render_2048(self):
        lines = []

        for row in self.grid:
            lines.append(
                " | ".join(f"{v or '.':^4}" for v in row)
            )

        self.board.setText(
            "СЧЁТ: " + str(self.score) +
            "\n\n" + "\n".join(lines) +
            "\n\nСтрелки — перемещение"
        )

    def move_2048(self, key):
        old = [row[:] for row in self.grid]

        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            for row in self.grid:
                values = [x for x in row if x]

                if key == Qt.Key.Key_Right:
                    values.reverse()

                merged = []
                i = 0

                while i < len(values):
                    if (
                        i + 1 < len(values)
                        and values[i] == values[i + 1]
                    ):
                        merged.append(values[i] * 2)
                        self.score += values[i] * 2
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
                values = [
                    self.grid[r][c]
                    for r in range(4)
                    if self.grid[r][c]
                ]

                if key == Qt.Key.Key_Down:
                    values.reverse()

                merged = []
                i = 0

                while i < len(values):
                    if (
                        i + 1 < len(values)
                        and values[i] == values[i + 1]
                    ):
                        merged.append(values[i] * 2)
                        self.score += values[i] * 2
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
            self.spawn_2048()
            self.render_2048()

    # SNAKE

    def render_snake(self):
        lines = []

        for y in range(12):
            row = ""

            for x in range(12):
                if (x, y) in self.snake:
                    row += "■ "
                elif (x, y) == self.food:
                    row += "● "
                else:
                    row += "· "

            lines.append(row)

        self.board.setText(
            "СЧЁТ: " + str(self.score) +
            "\n\n" + "\n".join(lines)
        )

    def move_snake(self):
        head = self.snake[0]

        new_head = (
            head[0] + self.direction[0],
            head[1] + self.direction[1]
        )

        if (
            new_head[0] < 0 or new_head[0] >= 12
            or new_head[1] < 0 or new_head[1] >= 12
            or new_head in self.snake
        ):
            self.finish("Snake", "Игра окончена! Счёт: " + str(self.score))
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            empty = [
                (x, y)
                for x in range(12)
                for y in range(12)
                if (x, y) not in self.snake
            ]

            if empty:
                self.food = random.choice(empty)
        else:
            self.snake.pop()

        self.render_snake()

    # TETRIS

    def new_piece(self):
        self.shape = random.choice(self.shapes)
        self.piece_x = 4
        self.piece_y = 0

        if self.collides(self.piece_x, self.piece_y, self.shape):
            self.finish("Tetris", "Игра окончена! Счёт: " + str(self.score))

    def collides(self, x, y, shape):
        for dx, dy in shape:
            nx = x + dx
            ny = y + dy

            if nx < 0 or nx >= 10 or ny >= 18:
                return True

            if ny >= 0 and self.grid[ny][nx]:
                return True

        return False

    def lock_piece(self):
        for dx, dy in self.shape:
            x = self.piece_x + dx
            y = self.piece_y + dy

            if 0 <= y < 18:
                self.grid[y][x] = 1

        remaining = [row for row in self.grid if not all(row)]
        cleared = 18 - len(remaining)

        self.score += cleared * 100

        for _ in range(cleared):
            remaining.insert(0, [0] * 10)

        self.grid = remaining
        self.new_piece()

    def tick(self):
        if self.game == "Snake":
            self.move_snake()

        elif self.game == "Tetris":
            if not self.collides(
                self.piece_x, self.piece_y + 1, self.shape
            ):
                self.piece_y += 1
            else:
                self.lock_piece()

            self.render_tetris()

    def render_tetris(self):
        display = [row[:] for row in self.grid]

        for dx, dy in self.shape:
            x = self.piece_x + dx
            y = self.piece_y + dy

            if 0 <= y < 18 and 0 <= x < 10:
                display[y][x] = 2

        lines = [
            "|" + "".join(
                "■" if cell == 1 else
                "□" if cell == 2 else "·"
                for cell in row
            ) + "|"
            for row in display
        ]

        self.board.setText(
            "СЧЁТ: " + str(self.score) +
            "\n\n" + "\n".join(lines) +
            "\n\n← → движение | ↓ ускорение | ↑ поворот"
        )

    def rotate_piece(self):
        rotated = [(-y, x) for x, y in self.shape]

        min_x = min(x for x, y in rotated)
        min_y = min(y for x, y in rotated)

        rotated = [
            (x - min_x, y - min_y)
            for x, y in rotated
        ]

        if not self.collides(
            self.piece_x, self.piece_y, rotated
        ):
            self.shape = rotated

    # MINESWEEPER

    def adjacent_mines(self, index):
        x = index % 10
        y = index // 10
        count = 0

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx = x + dx
                ny = y + dy

                if 0 <= nx < 10 and 0 <= ny < 10:
                    if ny * 10 + nx in self.mines:
                        count += 1

        return count

    def reveal_mine(self, index):
        if index in self.flags or index in self.revealed:
            return

        if index in self.mines:
            self.revealed.add(index)
            self.render_mines()
            self.finish("Сапёр", "Ты попал на мину!")
            return

        self.revealed.add(index)

        if self.adjacent_mines(index) == 0:
            x = index % 10
            y = index // 10

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx = x + dx
                    ny = y + dy

                    if 0 <= nx < 10 and 0 <= ny < 10:
                        neighbour = ny * 10 + nx

                        if neighbour not in self.revealed:
                            self.reveal_mine(neighbour)

        if len(self.revealed) == 85:
            self.game_won = True
            self.finish("Сапёр", "Поздравляем! Ты победил!")

        self.render_mines()

    def render_mines(self):
        lines = []

        for y in range(10):
            row = []

            for x in range(10):
                i = y * 10 + x

                if i == self.cursor:
                    symbol = "@"
                elif i in self.flags:
                    symbol = "F"
                elif i in self.revealed:
                    count = self.adjacent_mines(i)
                    symbol = str(count) if count else "."
                else:
                    symbol = "#"

                row.append(symbol)

            lines.append(" ".join(row))

        self.board.setText(
            "МИН: 15 | ОТКРЫТО: " +
            str(len(self.revealed)) +
            "\n\n" + "\n".join(lines) +
            "\n\nСтрелки — выбор | Enter — открыть"
            "\nПробел — флажок"
        )

    def move_mines_cursor(self, key):
        x = self.cursor % 10
        y = self.cursor // 10

        if key == Qt.Key.Key_Left:
            x = max(0, x - 1)
        elif key == Qt.Key.Key_Right:
            x = min(9, x + 1)
        elif key == Qt.Key.Key_Up:
            y = max(0, y - 1)
        elif key == Qt.Key.Key_Down:
            y = min(9, y + 1)

        self.cursor = y * 10 + x
        self.render_mines()

    # COMMON

    def finish(self, title, message):
        self.timer.stop()
        self.over = True
        QMessageBox.information(self, title, message)

    def keyPressEvent(self, event):
        key = event.key()

        if self.over:
            return

        if self.game == "2048":
            self.move_2048(key)

        elif self.game == "Snake":
            directions = {
                Qt.Key.Key_Up: (0, -1),
                Qt.Key.Key_Down: (0, 1),
                Qt.Key.Key_Left: (-1, 0),
                Qt.Key.Key_Right: (1, 0)
            }

            direction = directions.get(key)

            if direction and direction != (
                -self.direction[0], -self.direction[1]
            ):
                self.direction = direction

        elif self.game == "Tetris":
            if key == Qt.Key.Key_Left:
                if not self.collides(
                    self.piece_x - 1, self.piece_y, self.shape
                ):
                    self.piece_x -= 1

            elif key == Qt.Key.Key_Right:
                if not self.collides(
                    self.piece_x + 1, self.piece_y, self.shape
                ):
                    self.piece_x += 1

            elif key == Qt.Key.Key_Down:
                self.tick()

            elif key == Qt.Key.Key_Up:
                self.rotate_piece()

            self.render_tetris()

        elif self.game == "Сапёр":
            if key in (
                Qt.Key.Key_Left, Qt.Key.Key_Right,
                Qt.Key.Key_Up, Qt.Key.Key_Down
            ):
                self.move_mines_cursor(key)

            elif key in (
                Qt.Key.Key_Return, Qt.Key.Key_Enter
            ):
                self.reveal_mine(self.cursor)

            elif key == Qt.Key.Key_Space:
                if self.cursor not in self.revealed:
                    if self.cursor in self.flags:
                        self.flags.remove(self.cursor)
                    else:
                        self.flags.add(self.cursor)

                    self.render_mines()
