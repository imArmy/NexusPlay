import json
import os
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "NEXUS PLAY"
VERSION = "6.0"
BG = "#080d18"
SIDEBAR = "#0d1525"
PANEL = "#111d31"
PANEL_ALT = "#172640"
ACCENT = "#287cff"
ACCENT_HOVER = "#4590ff"
TEXT = "#f4f7ff"
MUTED = "#9aabc5"
GREEN = "#45d49a"
RED = "#ff667a"

STORES = [
    ("Steam", "https://store.steampowered.com/search/?term={q}", "PC"),
    ("Epic Games Store", "https://store.epicgames.com/en-US/browse?q={q}", "PC"),
    ("GOG", "https://www.gog.com/en/games?query={q}", "PC"),
    ("itch.io", "https://itch.io/search?q={q}", "PC"),
    ("PlayStation Store", "https://store.playstation.com/en-us/search/{q}", "PlayStation"),
]
EMULATORS = [
    ("PlayStation 1", "DuckStation", "https://duckstation.org/", "Высокая зрелость проекта"),
    ("PlayStation 2", "PCSX2", "https://pcsx2.net/", "Эмуляция PS2 на ПК"),
    ("PlayStation 3", "RPCS3", "https://rpcs3.net/", "Проверяй совместимость конкретной игры"),
    ("PlayStation 4", "shadPS4", "https://github.com/shadps4-emu/shadPS4", "Экспериментальная совместимость"),
    ("PlayStation 5", "Экспериментальные проекты", "https://github.com/topics/ps5-emulator", "Полноценной стабильной эмуляции PS5 пока нет"),
]

def data_dir():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "NexusPlay")
    os.makedirs(path, exist_ok=True)
    return path

LIBRARY_FILE = os.path.join(data_dir(), "library.json")

class NexusPlay:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE} — PC & PlayStation")
        self.root.geometry("1180x760")
        self.root.minsize(960, 640)
        self.root.configure(bg=BG)
        self.library = self.load_library()
        self.search_generation = 0
        self.page = None
        self.build_shell()
        self.show_home()

    def load_library(self):
        try:
            with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                value = json.load(f)
            return value if isinstance(value, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_library(self):
        try:
            with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.library, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            messagebox.showerror("Ошибка сохранения", str(exc), parent=self.root)

    def label(self, parent, text, size=10, color=TEXT, bold=False, bg=None, **kwargs):
        return tk.Label(parent, text=text, bg=bg or parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"),
                        anchor=kwargs.get("anchor", "w"), justify=kwargs.get("justify", "left"),
                        wraplength=kwargs.get("wraplength", 0))

    def btn(self, parent, text, command, primary=False, small=False):
        return tk.Button(parent, text=text, command=command, cursor="hand2",
                         bg=ACCENT if primary else PANEL_ALT, fg="white",
                         activebackground=ACCENT_HOVER, activeforeground="white",
                         relief="flat", bd=0, padx=12 if small else 16,
                         pady=7 if small else 10,
                         font=("Segoe UI", 9 if small else 10, "bold"))

    def build_shell(self):
        top = tk.Frame(self.root, bg=BG, height=76)
        top.pack(fill="x", padx=22, pady=(15, 10))
        top.pack_propagate(False)
        brand = tk.Frame(top, bg=BG)
        brand.pack(side="left", fill="y")
        self.label(brand, "NEXUS", 22, TEXT, True).pack(side="left", pady=15)
        self.label(brand, "PLAY", 22, ACCENT, True).pack(side="left", pady=15)
        self.label(top, "PC  /  PLAYSTATION  •  V6.0", 9, MUTED, True).pack(side="right", pady=25)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.sidebar = tk.Frame(main, bg=SIDEBAR, width=190)
        self.sidebar.pack(side="left", fill="y", padx=(0, 14))
        self.sidebar.pack_propagate(False)
        self.content = tk.Frame(main, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.label(self.sidebar, "МЕНЮ", 9, MUTED, True, bg=SIDEBAR).pack(anchor="w", padx=16, pady=(18, 12))
        nav_items = [
            ("⌂   Главная", self.show_home),
            ("▦   Магазин", self.show_store),
            ("◈   PlayStation", self.show_playstation),
            ("▣   Библиотека", self.show_library),
            ("⚙   Эмуляторы", self.show_emulators),
        ]
        for title, command in nav_items:
            b = tk.Button(self.sidebar, text=title, command=command, anchor="w",
                          bg=SIDEBAR, fg=TEXT, activebackground=PANEL_ALT,
                          activeforeground="white", relief="flat", bd=0,
                          padx=16, pady=12, font=("Segoe UI", 10, "bold"),
                          cursor="hand2")
            b.pack(fill="x", padx=6, pady=2)
        self.label(self.sidebar, "ИНФОРМАЦИЯ", 9, MUTED, True, bg=SIDEBAR).pack(anchor="w", padx=16, pady=(28, 8))
        self.label(self.sidebar, "Каталоги открываются через официальные магазины.\n\nДля PlayStation используй собственные копии игр и проверяй совместимость эмулятора.", 9, MUTED, bg=SIDEBAR, wraplength=155).pack(anchor="w", padx=16)
        self.status = tk.StringVar(value="Готово")
        statusbar = tk.Frame(self.root, bg=SIDEBAR, height=28)
        statusbar.pack(fill="x", side="bottom")
        tk.Label(statusbar, textvariable=self.status, bg=SIDEBAR, fg=MUTED,
                 font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=14, pady=5)

    def clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def heading(self, title, subtitle=""):
        self.label(self.content, title, 23, TEXT, True).pack(anchor="w", pady=(10, 3))
        if subtitle:
            self.label(self.content, subtitle, 10, MUTED).pack(anchor="w", pady=(0, 12))

    def panel(self, parent, padx=16, pady=14):
        return tk.Frame(parent, bg=PANEL, padx=padx, pady=pady)

    def show_home(self):
        self.clear()
        self.heading("ТВОЙ ИГРОВОЙ ЦЕНТР", "Игры для ПК и PlayStation — поиск, источники и личная библиотека.")
        hero = tk.Frame(self.content, bg="#132b50", padx=24, pady=24)
        hero.pack(fill="x", pady=(8, 16))
        self.label(hero, "ОДНА БИБЛИОТЕКА. МНОГО МИРОВ.", 20, TEXT, True, bg="#132b50").pack(anchor="w")
        self.label(hero, "Находи игры в магазинах, открывай официальные страницы и запускай установленные игры с компьютера.", 10, "#c7d9f5", bg="#132b50", wraplength=720).pack(anchor="w", pady=(8, 14))
        self.btn(hero, "Перейти в магазин", self.show_store, True).pack(anchor="w")
        grid = tk.Frame(self.content, bg=BG)
        grid.pack(fill="x")
        tiles = [
            ("МАГАЗИН ПК", "Steam, Epic, GOG и itch.io", self.show_store),
            ("PLAYSTATION", "Поиск PS Store и поколения PS1–PS5", self.show_playstation),
            ("МОЯ БИБЛИОТЕКА", f"Добавлено игр: {len(self.library)}", self.show_library),
            ("ЭМУЛЯТОРЫ", "Официальные страницы проектов", self.show_emulators),
        ]
        for i, (title, desc, fn) in enumerate(tiles):
            p = self.panel(grid, 15, 14)
            p.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
            self.label(p, title, 11, ACCENT, True, bg=PANEL).pack(anchor="w")
            self.label(p, desc, 10, MUTED, bg=PANEL).pack(anchor="w", pady=(7, 12))
            self.btn(p, "Открыть", fn, small=True).pack(anchor="w")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        self.label(self.content, "Примечание: единый каталог не означает, что все игры можно бесплатно скачать. Покупка и установка защищённых игр проходят в соответствующих магазинах.", 9, MUTED, wraplength=850).pack(anchor="w", pady=12)

    def search_bar(self, placeholder, command):
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill="x", pady=(5, 10))
        entry = tk.Entry(row, font=("Segoe UI", 11), bg=PANEL, fg=TEXT,
                         insertbackground=TEXT, relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 8))
        entry.insert(0, placeholder)
        self.btn(row, "Искать", lambda: command(entry.get()), True).pack(side="left")
        entry.bind("<Return>", lambda event: command(entry.get()))
        return entry

    def show_store(self):
        self.clear()
        self.heading("МАГАЗИН ИГР ДЛЯ ПК", "Онлайн-поиск Steam и быстрый переход к поиску в других магазинах.")
        self.results_area = tk.Frame(self.content, bg=BG)
        self.results_area.pack(fill="both", expand=True)
        entry = self.search_bar("Например, Minecraft, Cyberpunk 2077, Terraria…", self.search_steam)
        links = tk.Frame(self.content, bg=BG)
        links.pack(fill="x", pady=(0, 10))
        for store, template, _ in STORES[:4]:
            self.btn(links, store, lambda s=store, e=entry: self.open_store(s, e.get()), small=True).pack(side="left", padx=(0, 6))
        self.show_hint("Steam выдаёт результаты прямо в приложении. Epic, GOG и itch.io открывают официальный поиск магазина.")

    def show_hint(self, text):
        for w in self.results_area.winfo_children():
            w.destroy()
        self.label(self.results_area, text, 10, MUTED, wraplength=820).pack(anchor="w", pady=18)

    def open_store(self, store, query):
        template = next((x[1] for x in STORES if x[0] == store), None)
        if template:
            webbrowser.open(template.format(q=urllib.parse.quote(query.strip())))

    def search_steam(self, query):
        query = query.strip()
        if not query:
            self.status.set("Введи название игры")
            return
        self.search_generation += 1
        generation = self.search_generation
        self.show_hint("Подключаемся к каталогу Steam…")
        self.status.set("Поиск в Steam…")
        threading.Thread(target=self._fetch_steam, args=(query, generation), daemon=True).start()

    def _fetch_steam(self, query, generation):
        try:
            url = "https://store.steampowered.com/api/storesearch/?term=" + urllib.parse.quote(query) + "&l=russian&cc=ru"
            request = urllib.request.Request(url, headers={"User-Agent": "NexusPlay/6.0"})
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            items = data.get("items", [])
            self.root.after(0, lambda: self.render_steam(items, generation))
        except Exception as exc:
            self.root.after(0, lambda: self.render_search_error(str(exc), generation))

    def render_search_error(self, error, generation):
        if generation != self.search_generation:
            return
        self.show_hint("Не удалось загрузить результаты. Проверь интернет или попробуй позже.\n" + error[:220])
        self.status.set("Ошибка поиска")

    def render_steam(self, items, generation):
        if generation != self.search_generation:
            return
        for w in self.results_area.winfo_children():
            w.destroy()
        if not items:
            self.show_hint("В Steam ничего не найдено. Попробуй другое название.")
            self.status.set("Ничего не найдено")
            return
        canvas = tk.Canvas(self.results_area, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.results_area, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for item in items[:50]:
            appid = item.get("id")
            title = item.get("name", "Без названия")
            price_data = item.get("price") or {}
            price = price_data.get("final_formatted") or ("Бесплатно" if item.get("free") else "Цена на странице")
            card = tk.Frame(inner, bg=PANEL, padx=12, pady=9)
            card.pack(fill="x", pady=3)
            self.label(card, title, 10, TEXT, True, bg=PANEL).pack(side="left", fill="x", expand=True)
            self.label(card, price, 9, MUTED, bg=PANEL).pack(side="left", padx=10)
            self.btn(card, "Страница игры", lambda a=appid: webbrowser.open(f"https://store.steampowered.com/app/{a}/"), small=True).pack(side="right")
        self.status.set(f"Найдено результатов: {len(items)}")

    def show_playstation(self):
        self.clear()
        self.heading("PLAYSTATION", "Ищи игры в официальном PlayStation Store и выбирай поколение консоли.")
        self.results_area = tk.Frame(self.content, bg=BG)
        self.results_area.pack(fill="both", expand=True)
        entry = self.search_bar("Название игры PlayStation…", self.search_ps)
        generations = tk.Frame(self.content, bg=BG)
        generations.pack(fill="x", pady=6)
        for gen in ["PS5", "PS4", "PS3", "PS2", "PS1"]:
            self.btn(generations, gen, lambda g=gen, e=entry: self.search_ps(g + " " + e.get() if e.get().strip() else g), small=True).pack(side="left", padx=(0, 7))
        self.btn(self.content, "Открыть PlayStation Store", lambda: webbrowser.open("https://store.playstation.com/"), True).pack(anchor="w", pady=10)
        self.show_hint("Поиск ведёт в PlayStation Store. Доступность игр зависит от региона и поколения консоли. Для старых систем могут понадобиться эмуляторы.")

    def search_ps(self, query):
        if not query.strip():
            query = "games"
        webbrowser.open("https://store.playstation.com/en-us/search/" + urllib.parse.quote(query.strip()))

    def show_library(self):
        self.clear()
        self.heading("МОЯ БИБЛИОТЕКА", "Список сохраняется на этом компьютере. Добавляй EXE уже установленных игр.")
        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", pady=5)
        self.btn(toolbar, "＋ Добавить EXE", self.add_game, True).pack(side="left")
        self.btn(toolbar, "Обновить список", self.show_library, small=True).pack(side="left", padx=8)
        self.library_area = tk.Frame(self.content, bg=BG)
        self.library_area.pack(fill="both", expand=True, pady=10)
        self.render_library()

    def add_game(self):
        path = filedialog.askopenfilename(parent=self.root, title="Выбери исполняемый файл игры", filetypes=[("Windows-программы", "*.exe"), ("Все файлы", "*.* )")])
        if not path:
            return
        if any(x.get("path", "").lower() == path.lower() for x in self.library):
            messagebox.showinfo("Уже добавлено", "Эта игра уже есть в библиотеке.", parent=self.root)
            return
        self.library.append({"name": os.path.splitext(os.path.basename(path))[0], "path": path})
        self.save_library()
        self.render_library()
        self.status.set("Игра добавлена")

    def render_library(self):
        for w in self.library_area.winfo_children():
            w.destroy()
        if not self.library:
            self.label(self.library_area, "Библиотека пока пуста. Нажми «Добавить EXE».", 10, MUTED).pack(anchor="w", pady=20)
            return
        for index, game in enumerate(self.library):
            path = game.get("path", "")
            row = tk.Frame(self.library_area, bg=PANEL, padx=12, pady=9)
            row.pack(fill="x", pady=3)
            self.label(row, game.get("name", "Игра"), 10, TEXT, True, bg=PANEL).pack(side="left")
            self.btn(row, "Запустить", lambda p=path: self.launch_game(p), True, True).pack(side="right", padx=3)
            self.btn(row, "Папка", lambda p=path: self.open_folder(p), small=True).pack(side="right", padx=3)
            self.btn(row, "Удалить", lambda i=index: self.remove_game(i), small=True).pack(side="right", padx=3)

    def launch_game(self, path):
        if not os.path.isfile(path):
            messagebox.showerror("Файл не найден", "Путь к EXE больше не существует. Удали запись и добавь игру заново.", parent=self.root)
            return
        try:
            os.startfile(path)
        except AttributeError:
            try:
                subprocess.Popen([path], cwd=os.path.dirname(path) or None)
            except Exception as exc:
                messagebox.showerror("Не удалось запустить", str(exc), parent=self.root)
        except Exception as exc:
            messagebox.showerror("Не удалось запустить", str(exc), parent=self.root)

    def open_folder(self, path):
        folder = os.path.dirname(path)
        if os.path.isdir(folder):
            os.startfile(folder)

    def remove_game(self, index):
        if 0 <= index < len(self.library):
            name = self.library[index].get("name", "игру")
            if messagebox.askyesno("Удалить запись", f"Убрать «{name}» из библиотеки? Файлы игры не будут удалены.", parent=self.root):
                self.library.pop(index)
                self.save_library()
                self.render_library()

    def show_emulators(self):
        self.clear()
        self.heading("ЭМУЛЯТОРЫ PLAYSTATION", "Ссылки на проекты. Загружай программы с официальных страниц.")
        for generation, name, url, note in EMULATORS:
            card = self.panel(self.content, 14, 11)
            card.pack(fill="x", pady=4)
            left = tk.Frame(card, bg=PANEL)
            left.pack(side="left", fill="x", expand=True)
            self.label(left, generation + "  •  " + name, 11, TEXT, True, bg=PANEL).pack(anchor="w")
            self.label(left, note, 9, MUTED, bg=PANEL).pack(anchor="w", pady=(4, 0))
            self.btn(card, "Открыть сайт", lambda u=url: webbrowser.open(u), small=True).pack(side="right")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    NexusPlay(root)
    root.mainloop()
