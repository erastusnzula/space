from kivy.uix.screenmanager import Screen


def on_touch_down(self, touch):
    if not self.game_over and self.start_game and not self.pause:
        if touch.x < self.width / 2:
            self.current_speed = self.SPEED_x
        else:
            self.current_speed = -self.SPEED_x
    if self.start_btn.opacity == 0:
        self.start_btn.disabled = True
    return super(Screen, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.current_speed = 0
