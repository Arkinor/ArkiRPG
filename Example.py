import arcade
import random

# Константы
SCREEN_WIDTH = 800  # Ширина окна игры
SCREEN_HEIGHT = 600  # Высота окна игры
PLAYER_SPEED = 5  # Скорость движения персонажей
OBSTACLE_COUNT = 5  # Количество препятствий


class Player(arcade.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.color = color  # Цвет персонажа
        self.center_x = x  # Начальная позиция по оси X
        self.center_y = y  # Начальная позиция по оси Y
        self.width = 50  # Ширина персонажа
        self.height = 50  # Высота персонажа

    def draw(self):
        # Рисуем персонажа
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, self.color)


class Obstacle(arcade.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.center_x = x  # Позиция по оси X
        self.center_y = y  # Позиция по оси Y
        self.width = width  # Ширина препятствия
        self.height = height  # Высота препятствия

    def draw(self):
        # Рисуем препятствие
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, arcade.color.GRAY)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Догонялки")  # Инициализация окна игры
        self.setup()  # Настраиваем игру

    def setup(self):
        self.player1 = Player(arcade.color.BLUE, 100, SCREEN_HEIGHT // 2)  # Первый игрок (синий)
        self.player2 = Player(arcade.color.RED, 700, SCREEN_HEIGHT // 2)  # Второй игрок (красный)
        self.player1_change_x = 0  # Изменение позиции по оси X для первого игрока
        self.player1_change_y = 0  # Изменение позиции по оси Y для первого игрока
        self.player2_change_x = 0  # Изменение позиции по оси X для второго игрока
        self.player2_change_y = 0  # Изменение позиции по оси Y для второго игрока
        self.game_over = False  # Флаг окончания игры
        self.winner = None  # Переменная для хранения победителя
        self.obstacles = self.create_obstacles()  # Создаём препятствия

    def create_obstacles(self):
        obstacles = []
        while len(obstacles) < OBSTACLE_COUNT:
            width = random.randint(50, 150)  # Случайная ширина
            height = random.randint(50, 150)  # Случайная высота
            x = random.randint(width // 2, SCREEN_WIDTH - width // 2)  # Случайная позиция по оси X
            y = random.randint(height // 2, SCREEN_HEIGHT - height // 2)  # Случайная позиция по оси Y

            # Проверка на пересечение с игроками
            if not self.check_collision_with_players(x, y, width, height):
                obstacle = Obstacle(x, y, width, height)
                obstacles.append(obstacle)
        return obstacles

    def check_collision_with_players(self, x, y, width, height):
        # Проверяет, пересекается ли новое препятствие с игроками
        player1_bounds = (self.player1.center_x - self.player1.width / 2,
                          self.player1.center_x + self.player1.width / 2,
                          self.player1.center_y - self.player1.height / 2,
                          self.player1.center_y + self.player1.height / 2)

        player2_bounds = (self.player2.center_x - self.player2.width / 2,
                          self.player2.center_x + self.player2.width / 2,
                          self.player2.center_y - self.player2.height / 2,
                          self.player2.center_y + self.player2.height / 2)

        # Проверка на пересечение с первым игроком
        if (x + width / 2 > player1_bounds[0] and x - width / 2 < player1_bounds[1] and
                y + height / 2 > player1_bounds[2] and y - height / 2 < player1_bounds[3]):
            return True

        # Проверка на пересечение со вторым игроком
        if (x + width / 2 > player2_bounds[0] and x - width / 2 < player2_bounds[1] and
                y + height / 2 > player2_bounds[2] and y - height / 2 < player2_bounds[3]):
            return True

        return False

    def on_draw(self):
        arcade.start_render()  # Начинаем отрисовку
        if self.game_over:
            # Отображаем сообщение о победителе
            arcade.draw_text(f"Победил: {self.winner}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                             arcade.color.WHITE, font_size=24, anchor_x="center")
            # Кнопки "Начать заново" и "Выйти"
            arcade.draw_text("Нажмите R, чтобы начать заново", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.WHITE, font_size=20, anchor_x="center")
            arcade.draw_text("Нажмите Q, чтобы выйти", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30,
                             arcade.color.WHITE, font_size=20, anchor_x="center")
        else:
            self.player1.draw()  # Рисуем первого игрока
            self.player2.draw()  # Рисуем второго игрока
            for obstacle in self.obstacles:
                obstacle.draw()  # Рисуем препятствия

    def on_update(self, delta_time):
        if not self.game_over:
            # Временные позиции для проверки столкновения
            new_player1_x = self.player1.center_x + self.player1_change_x
            new_player1_y = self.player1.center_y + self.player1_change_y
            new_player2_x = self.player2.center_x + self.player2_change_x
            new_player2_y = self.player2.center_y + self.player2_change_y

            # Проверяем столкновения с препятствиями для первого игрока
            if not self.check_obstacle_collision(new_player1_x, new_player1_y):
                self.player1.center_x = new_player1_x
                self.player1.center_y = new_player1_y

            # Проверяем столкновения с препятствиями для второго игрока
            if not self.check_obstacle_collision(new_player2_x, new_player2_y):
                self.player2.center_x = new_player2_x
                self.player2.center_y = new_player2_y

            # Проверяем границы экрана для первого игрока
            self.player1.center_x = max(self.player1.width // 2,
                                        min(SCREEN_WIDTH - self.player1.width // 2, self.player1.center_x))
            self.player1.center_y = max(self.player1.height // 2,
                                        min(SCREEN_HEIGHT - self.player1.height // 2, self.player1.center_y))

            # Проверяем границы экрана для второго игрока
            self.player2.center_x = max(self.player2.width // 2,
                                        min(SCREEN_WIDTH - self.player2.width // 2, self.player2.center_x))
            self.player2.center_y = max(self.player2.height // 2,
                                        min(SCREEN_HEIGHT - self.player2.height // 2, self.player2.center_y))

            # Проверяем столкновение между игроками
            if arcade.check_for_collision(self.player1, self.player2):
                self.game_over = True  # Завершаем игру
                self.winner = "Игрок 1" if self.player1.center_x < self.player2.center_x else "Игрок 2"

    def check_obstacle_collision(self, new_x, new_y):
        # Проверяет столкновение игрока с препятствиями
        for obstacle in self.obstacles:
            if (new_x + self.player1.width / 2 > obstacle.center_x - obstacle.width / 2 and
                    new_x - self.player1.width / 2 < obstacle.center_x + obstacle.width / 2 and
                    new_y + self.player1.height / 2 > obstacle.center_y - obstacle.height / 2 and
                    new_y - self.player1.height / 2 < obstacle.center_y + obstacle.height / 2):
                return True
        return False

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.R:
                self.setup()  # Начинаем игру заново
            elif key == arcade.key.Q:
                arcade.close_window()  # Выходим из игры
            return

        # Обрабатываем нажатия клавиш для управления первым игроком (WASD)
        if key == arcade.key.W:
            self.player1_change_y = PLAYER_SPEED  # Движение вверх
        elif key == arcade.key.S:
            self.player1_change_y = -PLAYER_SPEED  # Движение вниз
        elif key == arcade.key.A:
            self.player1_change_x = -PLAYER_SPEED  # Движение влево
        elif key == arcade.key.D:
            self.player1_change_x = PLAYER_SPEED  # Движение вправо

        # Обрабатываем нажатия клавиш для управления вторым игроком (стрелки)
        if key == arcade.key.UP:
            self.player2_change_y = PLAYER_SPEED  # Движение вверх
        elif key == arcade.key.DOWN:
            self.player2_change_y = -PLAYER_SPEED  # Движение вниз
        elif key == arcade.key.LEFT:
            self.player2_change_x = -PLAYER_SPEED  # Движение влево
        elif key == arcade.key.RIGHT:
            self.player2_change_x = PLAYER_SPEED  # Движение вправо

    def on_key_release(self, key, modifiers):
        if not self.game_over:
            # Обрабатываем отпускание клавиш для первого игрока
            if key == arcade.key.W or key == arcade.key.S:
                self.player1_change_y = 0  # Останавливаем движение по оси Y
            if key == arcade.key.A or key == arcade.key.D:
                self.player1_change_x = 0  # Останавливаем движение по оси X

            # Обрабатываем отпускание клавиш для второго игрока
            if key == arcade.key.UP or key == arcade.key.DOWN:
                self.player2_change_y = 0  # Останавливаем движение по оси Y
            if key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.player2_change_x = 0  # Останавливаем движение по оси X


if __name__ == "__main__":
    game = MyGame()  # Создаём игру
    arcade.run()  # Запускаем игру
