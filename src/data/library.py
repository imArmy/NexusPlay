import os
import json
import subprocess
from pathlib import Path


APPDATA = os.getenv("APPDATA") or str(Path.home())
DATA_DIR = Path(APPDATA) / "NexusPlay"
LIBRARY_FILE = DATA_DIR / "library.json"


def load_games():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not LIBRARY_FILE.exists():
        return []

    try:
        with open(LIBRARY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_games(games):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(LIBRARY_FILE, "w", encoding="utf-8") as file:
        json.dump(games, file, ensure_ascii=False, indent=4)


def add_game(path, name=None):
    path = str(Path(path).resolve())

    if not path.lower().endswith(".exe"):
        raise ValueError("Можно добавлять только EXE-файлы.")

    if not os.path.isfile(path):
        raise FileNotFoundError("Файл игры не найден.")

    games = load_games()

    if any(game.get("path", "").lower() == path.lower()
           for game in games):
        raise ValueError("Эта игра уже есть в библиотеке.")

    if not name:
        name = Path(path).stem

    game = {
        "name": name,
        "path": path
    }

    games.append(game)
    save_games(games)

    return game


def remove_game(path):
    games = load_games()

    updated = [
        game for game in games
        if game.get("path") != path
    ]

    save_games(updated)


def launch_game(path):
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError("EXE-файл игры не найден.")

    subprocess.Popen(
        [str(path)],
        cwd=str(path.parent)
    )


def rename_game(path, new_name):
    if not new_name.strip():
        raise ValueError("Название не может быть пустым.")

    games = load_games()

    for game in games:
        if game.get("path") == path:
            game["name"] = new_name.strip()
            save_games(games)
            return

    raise ValueError("Игра не найдена в библиотеке.")
