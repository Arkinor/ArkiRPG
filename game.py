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


# SCREEN_WIDTH = 1900  # Ширина экрана
# SCREEN_HEIGHT = 1000  # Высота экрана
ANIMATION_SPEED = 0.1  # Время между кадрами анимации (в секундах)



# Имя файла для хранения значения переменной POINT
POINT_FILE = "point.json"
# Функция для чтения значения POINT из файла
def read_point():
    if os.path.exists(POINT_FILE):
        with open(POINT_FILE, "r") as file:
            data = json.load(file)
            return data.get("POINT", 0)
    else:
        return 0
# Функция для записи значения POINT в файл
def write_point(value):
    data = {"POINT": value}
    with open(POINT_FILE, "w") as file:
        json.dump(data, file)




def draw_grid():
    # Рисуем горизонтальные линии
    for y in range(0, SCREEN_HEIGHT, 100):
        arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.GRAY, 1)
    # Рисуем вертикальные линии
    for x in range(0, SCREEN_WIDTH, 100):
        arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.GRAY, 1)
    # Рисуем координаты
    for y in range(0, SCREEN_HEIGHT, 100):
        for x in range(0, SCREEN_WIDTH, 100):
            arcade.draw_text(f"{x},{y}", x + 5, y + 5, arcade.color.GRAY, 12)

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 300  # Здоровье игрока
        self.damage = 50  # Сила удара игрока
        self.speed = 5  # Скорость передвижения игрока
        self.jump_strength = 20  # Сила прыжка
        self.gravity = 1  # Сила гравитации
        self.current_frame = 0  # Индекс текущего кадра анимации
        self.is_jumping = False  # Флаг, указывающий, находится ли игрок в прыжке
        self.jump_speed = 0  # Скорость прыжка
        self.shooting = False  # Флаг, указывающий, стреляет ли игрок
        self.arrow_speed = 10  # Скорость полета стрелы
        self.shooting_frame = 0  # Индекс текущего кадра анимации выстрела
        self.animation_time = 0  # Время, прошедшее с последнего обновления кадра анимации
        self.can_shoot_while_moving = True  # Переменная, позволяющая стрелять на ходу
        self.arrow_created = False  # Флаг, указывающий, была ли создана стрела

        # Загрузка кадров анимации игрока
        self.player_sprites = [arcade.load_texture(f"images/Player/Right/{i}.png") for i in range(5)]

        # Загрузка кадров анимации выстрела
        self.shooting_sprites = [arcade.load_texture(f"images/Player/Attack/{i}.png") for i in range(4)]

        self.texture = self.player_sprites[0]  # Устанавливаем первую текстуру
        self.center_x = 150  # Начальная позиция по X
        self.center_y = 150  # Начальная позиция по Y

    def update_animation(self, delta_time):
        self.animation_time += delta_time  # Увеличиваем время анимации
        if self.animation_time >= ANIMATION_SPEED:  # Проверяем, достаточно ли времени прошло
            self.animation_time = 0  # Сбрасываем время анимации

            if self.shooting:
                self.texture = self.shooting_sprites[self.shooting_frame]
                self.shooting_frame += 1
                if self.shooting_frame >= len(self.shooting_sprites):
                    self.shooting = False  # Завершаем анимацию
                    self.shooting_frame = 0  # Сбрасываем кадр анимации
                    self.texture = self.player_sprites[self.current_frame]  # Возвращаемся к текстуре движения
                    self.arrow_created = False  # Сбрасываем флаг создания стрелы
            else:
                if self.change_x != 0:  # Обновляем анимацию только если игрок движется
                    self.texture = self.player_sprites[self.current_frame]
                    self.current_frame = (self.current_frame + 1) % len(self.player_sprites)
                else:
                    self.texture = self.player_sprites[0]  # Возвращаемся к первой текстуре, когда движение прекращается

    def update(self, delta_time):
        self.update_animation(delta_time)

        # Обработка прыжка
        if self.is_jumping:
            self.center_y += self.jump_speed  # Изменяем вертикальную позицию игрока
            self.jump_speed -= self.gravity  # Применяем гравитацию
            if self.center_y <= 150:  # Проверяем, не упал ли игрок на землю
                self.center_y = 150  # Устанавливаем игрока на землю
                self.is_jumping = False  # Завершаем прыжок

        # Обработка движения игрока
        if not self.shooting or self.can_shoot_while_moving:
            self.center_x += self.change_x

        # Ограничиваем движение игрока в пределах экрана
        if self.left < 0:
            self.left = 0  # Не даем игроку выйти за левую границу
        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH  # Не даем игроку выйти за правую границу

class Arrow(arcade.Sprite):
    def __init__(self, player):
        super().__init__()
        self.texture = arcade.load_texture("images/Player/Arrow/arrow.png")
        self.center_x = player.center_x + 50  # Позиция стрелы справа от игрока
        self.center_y = player.center_y  # Высота стрелы на высоте игрока
        self.speed = player.arrow_speed  # Скорость полета стрелы

    def update(self):
        self.center_x += self.speed  # Двигаем стрелу вправо
        if self.center_x > SCREEN_WIDTH:
            self.remove_from_sprite_lists()  # Удаляем стрелу, когда она улетает за экран

class Enemy(arcade.Sprite):
    base_health = 100  # Базовое здоровье врага
    throw_frequency = 5  # Частота кидания камней врагами (в секундах)
    SPAWN_FREQUENCY = 10  # Частота появления врагов (в секундах)
    enemy_speed = 1  # Скорость врага
    def __init__(self, player):
        super().__init__()
        self.damage = 50

        self.player = player  # Ссылка на игрока для следования за ним
        self.throw_time = time.time()

        self.current_frame = 0
        self.animation_time = 0

        # Загрузка кадров анимации врага
        self.enemy_sprites = [arcade.load_texture(f"images/Enemy/{i}.png") for i in range(3)]
        self.texture = self.enemy_sprites[0]  # Устанавливаем первую текстуру

        self.center_x = 1750  # Начальная позиция по X
        self.center_y = 150  # Начальная позиция по Y

    def update_animation(self, delta_time):
        self.animation_time += delta_time  # Увеличиваем время анимации
        if self.animation_time >= ANIMATION_SPEED:  # Проверяем, достаточно ли времени прошло
            self.animation_time = 0  # Сбрасываем время анимации
            self.texture = self.enemy_sprites[self.current_frame]
            self.current_frame = (self.current_frame + 1) % len(self.enemy_sprites)

    def update(self):
        self.update_animation(1/60)
        self.center_x -= Enemy.enemy_speed  # Враг движется влево
        if self.center_x < 0:  # Если враг уходит за левую границу экрана, он удаляется
            self.remove_from_sprite_lists()

    def draw_health(self):
        arcade.draw_text(f"{self.base_health}", self.center_x, self.center_y + 70, arcade.color.RED, 20, anchor_x="center")

class Stone(arcade.Sprite):
    def __init__(self, enemy, player):
        super().__init__()
        self.texture = arcade.load_texture("images/Enemy/rock.png")
        self.center_x = enemy.center_x
        self.center_y = enemy.center_y
        self.speed = 5
        self.player = player

    def update(self):
        self.center_x -= self.speed  # Камень движется влево
        if self.center_x < 0:  # Если камень уходит за левую границу экрана, он удаляется
            self.remove_from_sprite_lists()

        if arcade.check_for_collision(self, self.player):
            self.player.health -= 50
            self.remove_from_sprite_lists()


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.start_button = arcade.SpriteSolidColor(200, 40, arcade.color.GRAY)
        self.start_button.center_x = SCREEN_WIDTH // 2
        self.start_button.center_y = SCREEN_HEIGHT // 2 + 50
        self.start_button_text = "СТАРТ"

        self.shop_button = arcade.SpriteSolidColor(200, 40, arcade.color.GRAY)
        self.shop_button.center_x = SCREEN_WIDTH // 2
        self.shop_button.center_y = SCREEN_HEIGHT // 2 - 50
        self.shop_button_text = "МАГАЗИН"

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        arcade.start_render()
        # Отрисовка кнопок
        self.draw_button(self.start_button, self.start_button_text)
        self.draw_button(self.shop_button, self.shop_button_text)

    def draw_button(self, button, text):
        button.draw()
        arcade.draw_text(text, button.center_x, button.center_y, arcade.color.WHITE, 18, anchor_x="center",
                         anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_mouse_over_button(x, y, self.start_button):
            game_view = GameView()
            self.window.show_view(game_view)
        elif self.is_mouse_over_button(x, y, self.shop_button):
            arcade.draw_text("Shop view not implemented yet", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE,
                             24, anchor_x="center")

    def is_mouse_over_button(self, x, y, button):
        left = button.center_x - button.width // 2
        right = button.center_x + button.width // 2
        top = button.center_y + button.height // 2
        bottom = button.center_y - button.height // 2
        return left <= x <= right and bottom <= y <= top

class GameOverView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Press R to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Press Q to quit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView()
            self.window.show_view(game_view)
        elif key == arcade.key.Q:
            arcade.close_window()

class GameView(arcade.View):

    def __init__(self):
        super().__init__()


        self.player_sprite = Player()
        self.arrow_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.stone_list = arcade.SpriteList()
        self.background = arcade.load_texture("images/background/background.jpg") # задний фон
        self.heart_texture = arcade.load_texture("images/Player/heart/heart.png") # Путь к изображению сердечка
        self.arrow_count = 40  # Начальное количество стрел
        self.show_grid = False # Флаг для отображения сетки
        self.start_time = time.time() # Время начала игры
        self.enemy_spawn_time = time.time() # время последнего заспавненого врага
        self.last_arrow_add_time = time.time()  # Время последнего добавления стрелы
        self.last_health_increase_time = time.time()  # Время последнего увеличения здоровья врагов
        self.last_spawn_increase_time = time.time()  # Время последнего увеличения частоты спавна врагов
        self.last_speed_increase_time = time.time()  # Время последнего увеличения скорости врагов



    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):


        # Пример использования размеров экрана
        arcade.draw_text(f"Screen Width: {SCREEN_WIDTH}", 10, 20, arcade.color.WHITE, 12)
        arcade.draw_text(f"Screen Height: {SCREEN_HEIGHT}", 10, 40, arcade.color.WHITE, 12)


        # Рисуем фон
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Рисуем спрайт игрока
        self.player_sprite.draw()
        # Рисуем стрелы
        self.arrow_list.draw()
        # Рисуем врагов
        self.enemy_list.draw()
        # Рисуем камни
        self.stone_list.draw()

        # Рисуем здоровье игрока
        arcade.draw_texture_rectangle(40, SCREEN_HEIGHT - 40, 32, 32, self.heart_texture)
        arcade.draw_text(f"HP: {self.player_sprite.health}", 80, SCREEN_HEIGHT - 50, arcade.color.RED, 24)

        # Рисуем очки игрока
        arcade.draw_text(f"POINT: {read_point()}", 80, SCREEN_HEIGHT - 100, arcade.color.GREEN, 24)


        # Рисуем таймер
        current_time = int(time.time() - self.start_time)
        arcade.draw_text(f"Time: {current_time}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, arcade.color.RED, 24)

        # Рисуем количество стрел
        arcade.draw_text(f"Arrows: {self.arrow_count}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, arcade.color.RED, 24)

        # Рисуем сетку, если включена
        if self.show_grid:
            draw_grid()

            # Рисуем здоровье врагов
        for enemy in self.enemy_list:
            enemy.draw_health()

    def on_update(self, delta_time):
        global POINT
        self.player_sprite.update(delta_time)
        self.arrow_list.update()
        self.enemy_list.update()
        self.stone_list.update()

        # Заканчиваем игру, если здоровье игрока меньше или равно нулю
        if self.player_sprite.health <= 0:
            Enemy.base_health = 100
            Enemy.SPAWN_FREQUENCY = 10  # Частота появления врагов (в секундах)
            Enemy.enemy_speed = 1  # Скорость врага


            game_over_view = GameOverView()
            self.window.show_view(game_over_view)

        # Обработка столкновений стрел с врагами
        for arrow in self.arrow_list:
            hit_list = arcade.check_for_collision_with_list(arrow, self.enemy_list)
            if hit_list:  # Если стрела попадает в одного или более врагов
                for enemy in hit_list:
                    enemy.base_health -= self.player_sprite.damage
                    if enemy.base_health <= 0:
                        enemy.remove_from_sprite_lists()
                        write_point(read_point() + 5)
                arrow.remove_from_sprite_lists()  # Удаляем стрелу после обработки всех столкновений

        # Обработка столкновений игрока с врагами
        player_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        if player_hit_list:
            for enemy in player_hit_list:
                self.player_sprite.health -= 40  # Уменьшаем здоровье игрока на 10 за каждое столкновение
                enemy.remove_from_sprite_lists()  # Удаляем врага после столкновения
        # Создание врагов
        if time.time() - self.enemy_spawn_time >= Enemy(self.player_sprite).SPAWN_FREQUENCY:
            enemy = Enemy(self.player_sprite)
            self.enemy_list.append(enemy)
            self.enemy_spawn_time = time.time()

        # Кидание камней врагами
        for enemy in self.enemy_list:
            if time.time() - enemy.throw_time >= enemy.throw_frequency:
                stone = Stone(enemy, self.player_sprite)
                self.stone_list.append(stone)
                enemy.throw_time = time.time()

        # Каждые 10 секунд добавляем стрелу
        if time.time() - self.last_arrow_add_time >= 10:
            self.arrow_count += 1
            self.last_arrow_add_time = time.time()

        # Каждые 20 секунд увеличиваем здоровье врагов на 10 единиц
        if time.time() - self.last_health_increase_time >= 20:
            Enemy.base_health += 10  # Увеличиваем здоровье каждого врага на 10
            self.last_health_increase_time = time.time()

            # Каждые 30 секунд увеличиваем частоту спавна врагов и их скорость

            if time.time() - self.last_spawn_increase_time >= 30:
                if Enemy.SPAWN_FREQUENCY > 3:
                    Enemy.SPAWN_FREQUENCY = max(3, Enemy.SPAWN_FREQUENCY - 1)  # Минимальное значение частоты спавна - 3
                if Enemy.enemy_speed < 5:
                    Enemy.enemy_speed = min(3, Enemy.enemy_speed + 0.5)  # Максимальное значение скорости врагов - 3
                self.last_spawn_increase_time = time.time()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -self.player_sprite.speed
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = self.player_sprite.speed
        elif key == arcade.key.SPACE and not self.player_sprite.is_jumping:  # Проверяем, нажата ли пробел и не прыгает ли игрок
            self.player_sprite.is_jumping = True  # Начинаем прыжок
            self.player_sprite.jump_speed = self.player_sprite.jump_strength  # Устанавливаем скорость прыжка
        elif key == arcade.key.ENTER and not self.player_sprite.shooting and self.arrow_count > 0:
            self.player_sprite.shooting = True
            self.arrow_count -= 1
            arrow = Arrow(self.player_sprite)
            self.arrow_list.append(arrow)
        elif key == arcade.key.G:
            self.show_grid = not self.show_grid

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")
    main_menu_view = MainMenuView()
    window.show_view(main_menu_view)
    arcade.run()

if __name__ == "__main__":
    main()
