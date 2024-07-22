import arcade

class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Нажмите 'S' для начала игры", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.S:
            game_view = MyGame()
            self.window.show_view(game_view)