import sys


def key_pressed(self, keyboard, keycode, text, modifier):
    if keycode[1] == 'left':
        self.current_speed = self.SPEED_x
    elif keycode[1] == 'right':
        self.current_speed = -self.SPEED_x

    elif keycode[1] == 'spacebar':
        if not self.pause_button.disabled:
            self.pause_resume_control()
    elif keycode[1] == 'q' or 'esc':
        sys.exit()

    return True


def key_released(self, keyboard, keycode):
    self.current_speed = 0
    return True


def keyboard_closed(self):
    self.keyboard.unbind(on_key_down=self.key_pressed)
    self.keyboard.unbind(on_key_up=self.key_released)
    self.keyboard = None
