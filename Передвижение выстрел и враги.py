import arcade
import random
import time

# Константы
SCREEN_WIDTH = 1800  # Ширина экрана
SCREEN_HEIGHT = 900  # Высота экрана
ANIMATION_SPEED = 0.1  # Время между кадрами анимации (в секундах)
ENEMY_SPEED = 2  # Скорость врага
SPAWN_FREQUENCY = 5  # Частота появления врагов (в секундах)
THROW_FREQUENCY = 3  # Частота кидания камней врагами (в секундах)
HEART_IMAGE = "images/Player/heart/heart.png"  # Путь к изображению сердечка

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
        self.health = 100  # Здоровье игрока
        self.damage = 10  # Сила удара игрока
        self.speed = 5  # Скорость передвижения игрока
        self.jump_strength = 16  # Сила прыжка
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
    def __init__(self, player):
        super().__init__()
        self.health = 100
        self.damage = 10
        self.speed = ENEMY_SPEED
        self.player = player  # Ссылка на игрока для следования за ним
        self.throw_time = time.time()
        self.throw_frequency = THROW_FREQUENCY
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
        self.center_x -= self.speed  # Враг движется влево
        if self.center_x < 0:  # Если враг уходит за левую границу экрана, он удаляется
            self.remove_from_sprite_lists()

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

class GameOverView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Press R to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Press Q to quit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            arcade.close_window()
        elif key == arcade.key.R:
            game_view = MyGame()
            game_view.setup()
            self.window.show_view(game_view)

class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None  # Текстура фона
        self.keys_pressed = set()  # Нажатые клавиши
        self.player_sprite = Player()  # Создаем экземпляр игрока
        self.arrows = arcade.SpriteList()  # Список стрел
        self.enemies = arcade.SpriteList()  # Список врагов
        self.stones = arcade.SpriteList()  # Список камней
        self.show_grid = False  # Флаг для отображения сетки
        self.last_spawn_time = time.time()
        self.start_time = time.time()  # Время начала игры
        self.arrow_count = 30  # Начальное количество стрел
        self.heart_texture = arcade.load_texture(HEART_IMAGE)  # Загрузка изображения сердечка
        self.last_arrow_add_time = time.time()  # Время последнего добавления стрелы

    def setup(self):
        # Загрузка изображений фона
        self.background = arcade.load_texture("images/background/background.jpg")

    def on_draw(self):
        arcade.start_render()
        # Рисуем фон
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)

        # Рисуем спрайт игрока
        self.player_sprite.draw()
        # Рисуем стрелы
        self.arrows.draw()
        # Рисуем врагов
        self.enemies.draw()
        # Рисуем камни
        self.stones.draw()

        # Рисуем здоровье игрока
        arcade.draw_texture_rectangle(40, SCREEN_HEIGHT - 40, 32, 32, self.heart_texture)
        arcade.draw_text(f"HP: {self.player_sprite.health}", 80, SCREEN_HEIGHT - 50, arcade.color.RED, 24)

        # Рисуем таймер
        current_time = int(time.time() - self.start_time)
        arcade.draw_text(f"Time: {current_time}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, arcade.color.RED, 24)

        # Рисуем количество стрел
        arcade.draw_text(f"Arrows: {self.arrow_count}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, arcade.color.RED, 24)

        # Рисуем сетку, если включена
        if self.show_grid:
            draw_grid()

    def update(self, delta_time):
        # Обработка движения игрока
        if arcade.key.LEFT in self.keys_pressed:
            self.player_sprite.change_x = -self.player_sprite.speed  # Двигаем игрока влево
        elif arcade.key.RIGHT in self.keys_pressed:
            self.player_sprite.change_x = self.player_sprite.speed  # Двигаем игрока вправо
        else:
            self.player_sprite.change_x = 0  # Останавливаем игрока, если нет нажатых клавиш

        # Обновляем спрайт игрока
        self.player_sprite.update(delta_time)

        # Обновляем врагов
        self.enemies.update()

        # Обновляем камни
        self.stones.update()

        # Обновляем стрелы
        self.arrows.update()

        # Проверяем столкновения стрел с врагами
        for arrow in self.arrows:
            enemies_hit = arcade.check_for_collision_with_list(arrow, self.enemies)
            for enemy in enemies_hit:
                enemy.remove_from_sprite_lists()  # Удаляем врага при попадании стрелы
                arrow.remove_from_sprite_lists()  # Удаляем стрелу после попадания

        # Проверяем здоровье игрока
        if self.player_sprite.health <= 0:
            game_over_view = GameOverView()
            self.window.show_view(game_over_view)
            return

        # Проверяем столкновения камней с игроком
        for stone in self.stones:
            if arcade.check_for_collision(stone, self.player_sprite):
                stone.remove_from_sprite_lists()
                self.player_sprite.health -= 50
                if self.player_sprite.health <= 0:
                    game_over_view = GameOverView()
                    self.window.show_view(game_over_view)
                    return

        # Проверяем столкновения врагов с игроком
        for enemy in self.enemies:
            if arcade.check_for_collision(enemy, self.player_sprite):
                self.player_sprite.health = 0
                game_over_view = GameOverView()
                self.window.show_view(game_over_view)
                return

        # Если анимация выстрела завершена, создаем стрелу
        if self.player_sprite.shooting and not self.player_sprite.arrow_created and self.arrow_count > 0:
            if self.player_sprite.shooting_frame == len(self.player_sprite.shooting_sprites) - 1:
                arrow = Arrow(self.player_sprite)  # Создаем новую стрелу
                self.arrows.append(arrow)  # Добавляем стрелу в список стрел
                self.player_sprite.arrow_created = True  # Устанавливаем флаг создания стрелы
                self.arrow_count -= 1  # Уменьшаем количество стрел

        # Спавн врагов
        current_time = time.time()
        if current_time - self.last_spawn_time > SPAWN_FREQUENCY:
            enemy = Enemy(self.player_sprite)
            self.enemies.append(enemy)
            self.last_spawn_time = current_time

        # Враги кидают камни
        for enemy in self.enemies:
            if current_time - enemy.throw_time > enemy.throw_frequency:
                stone = Stone(enemy, self.player_sprite)
                self.stones.append(stone)
                enemy.throw_time = current_time

        # Каждые 10 секунд добавляем стрелу
        if current_time - self.last_arrow_add_time >= 10:
            self.arrow_count += 1
            self.last_arrow_add_time = current_time

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)  # Добавляем нажатую клавишу в набор
        if key == arcade.key.SPACE and not self.player_sprite.is_jumping:  # Проверяем, нажата ли пробел и не прыгает ли игрок
            self.player_sprite.is_jumping = True  # Начинаем прыжок
            self.player_sprite.jump_speed = self.player_sprite.jump_strength  # Устанавливаем скорость прыжка
        if key == arcade.key.ENTER and not self.player_sprite.shooting:  # Проверяем, нажата ли клавиша ENTER
            self.player_sprite.shooting = True  # Начинаем анимацию выстрела
            self.player_sprite.arrow_created = False  # Сбрасываем флаг создания стрелы
            if not self.player_sprite.can_shoot_while_moving:
                self.player_sprite.change_x = 0  # Останавливаем игрока, если он не может стрелять на ходу

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)  # Убираем отпущенную клавишу из набора


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Моя Игра")
    game = MyGame()
    game.setup()
    window.show_view(game)
    arcade.run()
