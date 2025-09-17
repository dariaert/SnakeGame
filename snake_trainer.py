import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import random
import time
import csv
import os
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------
# --- PyGame Snake ---
# --------------------
def run_snake_game(settings):
    """
    Запускает PyGame-змейку на основе настроек (dict).
    Возвращает dict с результатами: {'score': int, 'duration': float, 'datetime': str, 'level': int}
    """
    block = settings.get('block', 20)
    cols = settings.get('cols', 30)
    rows = settings.get('rows', 20)
    width = cols * block
    height = rows * block
    base_speed = settings.get('base_speed', 10)
    bonus_count = settings.get('bonus_count', 1)
    enable_bonus = bonus_count > 0

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snake — Trainer Demo")
    clock = pygame.time.Clock()

    # Загружаем спрайты еды и бонуса
    try:
        apple_img = pygame.image.load("apple.png")
        apple_img = pygame.transform.scale(apple_img, (block, block))

        bonus_img = pygame.image.load("bonus.png")
        bonus_img = pygame.transform.scale(bonus_img, (block, block))
    except Exception as e:
        print("⚠ Не удалось загрузить изображения, будут квадраты:", e)
        apple_img = None
        bonus_img = None

    # Загружаем спрайты змейки
    try:
        snake_head_img = pygame.image.load("snake_head.png")
        snake_head_img = pygame.transform.scale(snake_head_img, (block, block))

        snake_body_img = pygame.image.load("snake_body.png")
        snake_body_img = pygame.transform.scale(snake_body_img, (block, block))
    except Exception as e:
        print("⚠ Не удалось загрузить спрайты змейки, будут квадраты:", e)
        snake_head_img = None
        snake_body_img = None

    # Colors
    BG = (40, 48, 63)
    GRID = (55, 66, 85)
    SNAKE_HEAD = (20, 200, 80)
    SNAKE_BODY = (40, 220, 120)
    FOOD_COLOR = (220, 60, 60)
    BONUS_COLOR = (255, 200, 40)
    TEXT_COLOR = (230, 230, 230)

    font = pygame.font.SysFont("Arial", int(block * 0.8))

    def draw_grid():
        for x in range(0, width, block):
            pygame.draw.line(screen, GRID, (x, 0), (x, height))
        for y in range(0, height, block):
            pygame.draw.line(screen, GRID, (0, y), (width, y))

    def draw_text(s, pos):
        surf = font.render(s, True, TEXT_COLOR)
        screen.blit(surf, pos)

    # place item on grid
    def random_cell():
        return random.randrange(0, cols) * block, random.randrange(0, rows) * block

    # initial snake - center
    x = (cols // 2) * block
    y = (rows // 2) * block
    snake = [[x, y]]  # <-- начинаем только с головы
    direction = (block, 0)  # dx, dy
    length = 1  # <-- длина = 1

    food = random_cell()
    bonuses = []
    for _ in range(bonus_count):
        bonuses.append(random_cell())

    score = 0
    level = 1
    speed = base_speed
    start_time = time.perf_counter()

    running = True
    gameover = False

    # Prevent reversing direction
    def valid_direction(new_dx, new_dy, cur_dx, cur_dy):
        return not (new_dx == -cur_dx and new_dy == -cur_dy)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gameover = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if valid_direction(-block, 0, *direction):
                        direction = (-block, 0)
                elif event.key == pygame.K_RIGHT:
                    if valid_direction(block, 0, *direction):
                        direction = (block, 0)
                elif event.key == pygame.K_UP:
                    if valid_direction(0, -block, *direction):
                        direction = (0, -block)
                elif event.key == pygame.K_DOWN:
                    if valid_direction(0, block, *direction):
                        direction = (0, block)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    gameover = True

        if not running:
            break

        # Move head
        head_x = snake[-1][0] + direction[0]
        head_y = snake[-1][1] + direction[1]

        # check boundaries
        if head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            gameover = True
            running = False
        else:
            new_head = [head_x, head_y]
            # check self-collision
            if new_head in snake:
                gameover = True
                running = False
            else:
                snake.append(new_head)
                if len(snake) > length:
                    del snake[0]

        # check food collision
        if snake[-1][0] == food[0] and snake[-1][1] == food[1]:
            score += 1
            length += 1
            food = random_cell()
            # ensure food not spawned on snake or bonus
            while food in snake or (enable_bonus and food in bonuses):
                food = random_cell()

        # check bonuses
        for i, b in enumerate(bonuses):
            if snake[-1][0] == b[0] and snake[-1][1] == b[1]:
                score += 3
                length += 2
                # respawn bonus
                bonuses[i] = random_cell()
                while bonuses[i] in snake or bonuses[i] == food or bonuses[i] in bonuses[:i]:
                    bonuses[i] = random_cell()

        # level up every 5 points
        if score > 0:
            new_level = score // 5 + 1
            if new_level != level:
                level = new_level
                speed = base_speed + (level - 1) * 2

        # Draw
        screen.fill(BG)
        draw_grid()

        # draw food
        if apple_img:
            screen.blit(apple_img, (food[0], food[1]))
        else:
            pygame.draw.rect(screen, FOOD_COLOR, (food[0], food[1], block, block))

        # draw bonuses
        if enable_bonus:
            for b in bonuses:
                if bonus_img:
                    screen.blit(bonus_img, (b[0], b[1]))
                else:
                    pygame.draw.rect(screen, BONUS_COLOR, (b[0], b[1], block, block))

        # draw snake using sprites if available
        for idx, seg in enumerate(snake):
            if idx == len(snake) - 1:  # голова
                if snake_head_img:
                    screen.blit(snake_head_img, (seg[0], seg[1]))
                else:
                    pygame.draw.rect(screen, SNAKE_HEAD, (seg[0], seg[1], block, block))
            else:  # тело
                if snake_body_img:
                    screen.blit(snake_body_img, (seg[0], seg[1]))
                else:
                    # градиент как запасной вариант
                    ratio = idx / max(1, len(snake) - 1)
                    r = int(SNAKE_HEAD[0] * (1 - ratio) + SNAKE_BODY[0] * ratio)
                    g = int(SNAKE_HEAD[1] * (1 - ratio) + SNAKE_BODY[1] * ratio)
                    bcol = int(SNAKE_HEAD[2] * (1 - ratio) + SNAKE_BODY[2] * ratio)
                    pygame.draw.rect(screen, (r, g, bcol), (seg[0], seg[1], block, block))

        # HUD
        draw_text(f"Score: {score}", (5, 5))
        draw_text(f"Level: {level}", (5, 5 + int(block * 0.9)))

        pygame.display.flip()
        clock.tick(speed)

    duration = time.perf_counter() - start_time
    pygame.quit()
    result = {
        'score': score,
        'duration': round(duration, 2),
        'datetime': datetime.now().isoformat(sep=' ', timespec='seconds'),
        'level': level
    }
    return result

# --------------------
# --- Tkinter App ---
# --------------------
class TrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Trainer — Game + Analytics")
        self.root.geometry("820x600")
        self.results_file = "results.csv"

        # Default settings
        self.block_var = tk.IntVar(value=20)
        self.cols_var = tk.IntVar(value=30)
        self.rows_var = tk.IntVar(value=20)
        self.speed_var = tk.IntVar(value=10)
        self.bonus_var = tk.IntVar(value=1)

        self.build_ui()
        self.load_results_into_table()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(frm)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))

        ttk.Label(left, text="Настройки игры", font=("Arial", 14, "bold")).pack(pady=(0,8))
        # block size
        ttk.Label(left, text="Размер клетки (px)").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=10, to=60, textvariable=self.block_var, width=6).pack(anchor=tk.W, pady=2)

        # cols
        ttk.Label(left, text="Кол-во колонок").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=10, to=60, textvariable=self.cols_var, width=6).pack(anchor=tk.W, pady=2)

        # rows
        ttk.Label(left, text="Кол-во строк").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=8, to=40, textvariable=self.rows_var, width=6).pack(anchor=tk.W, pady=2)

        # speed
        ttk.Label(left, text="Базовая скорость").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=5, to=30, textvariable=self.speed_var, width=6).pack(anchor=tk.W, pady=2)

        # bonus
        ttk.Label(left, text="Кол-во бонусов").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=0, to=5, textvariable=self.bonus_var, width=6).pack(anchor=tk.W, pady=2)

        ttk.Button(left, text="Start Game", command=self.start_game, width=20).pack(pady=(12,4))
        ttk.Button(left, text="Show Graph", command=self.show_graph, width=20).pack(pady=4)
        ttk.Button(left, text="Export CSV...", command=self.export_csv, width=20).pack(pady=4)
        ttk.Button(left, text="Clear results", command=self.clear_results, width=20).pack(pady=4)

        # right side - results table and plot area
        right = ttk.Frame(frm)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Результаты игр", font=("Arial", 14, "bold")).pack(anchor=tk.W)

        cols = ("datetime", "score", "duration", "level")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=10)
        self.tree.heading("datetime", text="Дата/Время")
        self.tree.heading("score", text="Счёт")
        self.tree.heading("duration", text="Время (с)")
        self.tree.heading("level", text="Уровень")
        self.tree.pack(fill=tk.X, pady=(4,10))

        # Matplotlib figure placeholder
        self.fig = Figure(figsize=(6,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_game(self):
        # gather settings
        settings = {
            'block': int(self.block_var.get()),
            'cols': int(self.cols_var.get()),
            'rows': int(self.rows_var.get()),
            'base_speed': int(self.speed_var.get()),
            'bonus_count': int(self.bonus_var.get())
        }

        # hide root window to allow pygame window focus
        self.root.withdraw()
        try:
            result = run_snake_game(settings)
        except Exception as e:
            messagebox.showerror("Error", f"Ошибка при запуске игры:\n{e}")
            self.root.deiconify()
            return

        # show root and save result
        self.root.deiconify()
        messagebox.showinfo("Game Over", f"Игра окончена!\nСчёт: {result['score']}\nВремя: {result['duration']} с\nУровень: {result['level']}")
        self.append_result(result)
        self.load_results_into_table()

    def append_result(self, result):
        file_exists = os.path.exists(self.results_file)
        with open(self.results_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["datetime", "score", "duration", "level"])
            writer.writerow([result['datetime'], result['score'], result['duration'], result['level']])

    def load_results_into_table(self):
        # clear
        for r in self.tree.get_children():
            self.tree.delete(r)
        if not os.path.exists(self.results_file):
            return
        with open(self.results_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.tree.insert("", tk.END, values=(row["datetime"], row["score"], row["duration"], row["level"]))

    def show_graph(self):
        # read CSV and plot score over time
        if not os.path.exists(self.results_file):
            messagebox.showwarning("Нет данных", "Файл results.csv не найден. Сыграйте хотя бы одну игру.")
            return
        times = []
        scores = []
        with open(self.results_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    times.append(datetime.fromisoformat(row["datetime"]))
                    scores.append(int(row["score"]))
                except Exception:
                    continue
        if not times:
            messagebox.showwarning("Нет данных", "Нет корректных записей в results.csv")
            return
        # plot
        self.ax.clear()
        self.ax.plot(times, scores, marker='o', linestyle='-')
        self.ax.set_title("Счёт по времени")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Счёт")
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def export_csv(self):
        if not os.path.exists(self.results_file):
            messagebox.showwarning("Нет данных", "Файл results.csv не найден.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if path:
            try:
                with open(self.results_file, "rb") as src, open(path, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Экспорт", f"Экспортировано в {path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Нельзя экспортировать: {e}")

    def clear_results(self):
        if messagebox.askyesno("Очистить", "Удалить все результаты?"):
            if os.path.exists(self.results_file):
                os.remove(self.results_file)
            self.load_results_into_table()
            self.ax.clear()
            self.canvas.draw()

# --------------------
# --- Main ----------
# --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainerApp(root)
    root.mainloop()
