import arcade

# Константы
SCREEN_WIDTH = 1300  # Ширина экрана
SCREEN_HEIGHT = 600  # Высота экрана

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100  # Здоровье игрока
        self.damage = 10    # Сила удара игрока
        self.speed = 5      # Скорость передвижения игрока
        self.jump_strength = 15  # Сила прыжка
        self.gravity = 1           # Сила гравитации
        self.current_frame = 0     # Индекс текущего кадра анимации
        self.player_sprites = []    # Список кадров анимации
        self.is_jumping = False      # Флаг, указывающий, находится ли игрок в прыжке
        self.jump_speed = 0          # Скорость прыжка

        # Загрузка кадров анимации
        for i in range(5):  # Предполагаем, что у вас 5 кадров
            texture = arcade.load_texture(f"images/Player/Right/{i}.png")
            self.player_sprites.append(texture)

        self.texture = self.player_sprites[0]  # Устанавливаем первую текстуру
        self.center_x = SCREEN_WIDTH // 3      # Начальная позиция по X
        self.center_y = SCREEN_HEIGHT // 5      # Начальная позиция по Y

    def update(self):
        # Обновление текстуры на основе текущего кадра анимации
        self.texture = self.player_sprites[self.current_frame]

        # Обработка прыжка
        if self.is_jumping:
            self.center_y += self.jump_speed  # Изменяем вертикальную позицию игрока
            self.jump_speed -= self.gravity  # Применяем гравитацию
            if self.center_y <= SCREEN_HEIGHT // 5:  # Проверяем, не упал ли игрок на землю
                self.center_y = SCREEN_HEIGHT // 5  # Устанавливаем игрока на землю
                self.is_jumping = False  # Завершаем прыжок

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Моя Игра")
        self.background = None  # Текстура фона
        self.keys_pressed = set()  # Нажатые клавиши
        self.player_sprite = Player()  # Создаем экземпляр игрока

    def setup(self):
        # Загрузка изображений фона
        self.background = arcade.load_texture("../images/background/background.jpg")

    def on_draw(self):
        arcade.start_render()
        # Рисуем фон
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)

        # Рисуем спрайт игрока
        self.player_sprite.draw()

    def update(self, delta_time):
        # Обработка передвижения игрока
        if arcade.key.LEFT in self.keys_pressed:
            self.player_sprite.change_x = -self.player_sprite.speed  # Двигаем игрока влево
            self.player_sprite.current_frame = (self.player_sprite.current_frame + 1) % len(self.player_sprite.player_sprites)
        elif arcade.key.RIGHT in self.keys_pressed:
            self.player_sprite.change_x = self.player_sprite.speed  # Двигаем игрока вправо
            self.player_sprite.current_frame = (self.player_sprite.current_frame + 1) % len(self.player_sprite.player_sprites)
        else:
            self.player_sprite.change_x = 0  # Останавливаем игрока, если нет нажатых клавиш
            self.player_sprite.current_frame = 0  # Сбрасываем анимацию к первой картинке

        # Обновляем позицию игрока
        self.player_sprite.center_x += self.player_sprite.change_x

        # Ограничиваем движение игрока в пределах экрана
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0  # Не даем игроку выйти за левую границу
        elif self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.right = SCREEN_WIDTH  # Не даем игроку выйти за правую границу

        # Обновляем спрайт игрока
        self.player_sprite.update()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)  # Добавляем нажатую клавишу в набор
        if key == arcade.key.SPACE and not self.player_sprite.is_jumping:  # Проверяем, нажата ли пробел и не прыгает ли игрок
            self.player_sprite.is_jumping = True  # Начинаем прыжок
            self.player_sprite.jump_speed = self.player_sprite.jump_strength  # Устанавливаем скорость прыжка

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)  # Убираем отпущенную клавишу из набора

if __name__ == "__main__":
    game = MyGame()  # Создаем экземпляр игры
    game.setup()  # Настраиваем игру
    arcade.run()  # Запускаем главный цикл игры