import arcade
import random
import time
import os
import json
import ctypes

# Константы
user32 = ctypes.windll.user32
SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

ANIMATION_SPEED = 0.1  # Время между кадрами анимации (в секундах)

# Имя файла для хранения значения переменной SCORE
SCORE_FILE = "score.json"

# Функция для чтения значения SCORE из файла
def read_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as file:
            data = json.load(file)
            return data.get("SCORE", 0)
    else:
        return 0

# Функция для записи значения SCORE в файл
def write_score(value):
    data = {"SCORE": value}
    with open(SCORE_FILE, "w") as file:
        json.dump(data, file)

class Bird(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(50, arcade.color.YELLOW)  # Увеличенная текстура для птицы
        self.radius = 25
        self.center_x = 100
        self.center_y = SCREEN_HEIGHT // 2
        self.velocity_y = 0
        self.gravity = 1.0
        self.flap_strength = 20  # Увеличенная сила подъема

    def update(self):
        self.velocity_y -= self.gravity
        self.center_y += self.velocity_y

        # Проверка на выход за границы экрана
        if self.center_y < 0:
            self.center_y = 0
            self.velocity_y = 0  # Останавливаем падение
        elif self.center_y > SCREEN_HEIGHT:
            self.center_y = SCREEN_HEIGHT  # Не даем птице выйти за верхнюю границу
            self.velocity_y = 0

class Pipe(arcade.Sprite):
    def __init__(self, x, height, is_top):
        super().__init__()
        self.texture = arcade.load_texture("images/Enemy/0.png")  # Замените на путь к четкой текстуре трубы
        self.width = 60
        self.height = height
        self.center_x = x
        self.is_top = is_top

    def draw(self):
        if self.is_top:
            arcade.draw_texture_rectangle(self.center_x, SCREEN_HEIGHT - self.height // 2, self.width, self.height, self.texture)
        else:
            arcade.draw_texture_rectangle(self.center_x, self.height // 2, self.width, self.height, self.texture)

class FlappyBirdGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.bird = Bird()
        self.pipes = arcade.SpriteList()
        self.score = 0
        self.game_over = False
        self.spawn_pipe_time = 0
        self.background = arcade.load_texture("images/background/background.jpg")  # Задний фон
        self.background_x1 = 0  # Первая позиция фона
        self.background_x2 = SCREEN_WIDTH  # Вторая позиция фона

    def setup(self):
        self.bird = Bird()
        self.pipes = arcade.SpriteList()
        self.score = 0
        self.game_over = False
        self.spawn_pipe_time = time.time()

    def on_draw(self):
        arcade.start_render()

        # Рисуем движущийся фон
        arcade.draw_texture_rectangle(self.background_x1, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_texture_rectangle(self.background_x2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Проверяем, нужно ли повторить фон
        if self.background_x1 <= -SCREEN_WIDTH:
            self.background_x1 = SCREEN_WIDTH  # Сброс первой позиции фона
        if self.background_x2 <= -SCREEN_WIDTH:
            self.background_x2 = SCREEN_WIDTH  # Сброс второй позиции фона

        self.bird.draw()
        self.pipes.draw()
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 20)

        if self.game_over:
            arcade.draw_text("Game Over", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, arcade.color.RED, 40)

    def on_update(self, delta_time):
        if not self.game_over:
            self.bird.update()

            # Обновляем трубы
            self.pipes.update()
            for pipe in self.pipes:
                pipe.center_x -= 3  # Двигаем трубы влево
                if pipe.center_x < -pipe.width:
                    self.pipes.remove(pipe)
                    self.score += 1  # Начисляем очки за каждую пройденную трубу

            # Спавн новых труб с разными расстояниями между ними
            if time.time() - self.spawn_pipe_time > 1.5:
                height_top = random.randint(150, SCREEN_HEIGHT - 50)  # Высота верхней трубы
                height_bottom = SCREEN_HEIGHT - height_top - 200  # Высота нижней трубы

                # Создаем верхнюю и нижнюю трубы
                new_pipe_top = Pipe(SCREEN_WIDTH, height_top, True)
                new_pipe_bottom = Pipe(SCREEN_WIDTH, height_bottom, False)
                self.pipes.append(new_pipe_top)
                self.pipes.append(new_pipe_bottom)

                self.spawn_pipe_time = time.time()

            # Проверка на столкновение
            if self.bird.center_y < 0 or self.bird.center_y > SCREEN_HEIGHT:
                self.game_over = True

            for pipe in self.pipes:
                if arcade.check_for_collision(self.bird, pipe):
                    self.game_over = True

            # Двигаем фон влево
            self.background_x1 -= 3  # Скорость движения фона
            self.background_x2 -= 3  # Скорость движения фона

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and not self.game_over:
            self.bird.velocity_y = self.bird.flap_strength  # Подъем птицы
        elif self.game_over:
            self.setup()  # Перезапуск игры

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Flappy Bird")
    game_view = FlappyBirdGame()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()
